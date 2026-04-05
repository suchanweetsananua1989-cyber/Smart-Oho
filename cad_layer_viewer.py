from __future__ import annotations

import math
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

import ezdxf
from ezdxf.addons import odafc
from PyQt6 import QtCore, QtGui, QtWidgets

from .ui.common_controls import show_critical

try:
    import comtypes.client as com_client
except Exception:
    com_client = None


@dataclass
class GraphicPrimitive:
    kind: str
    layer: str
    data: tuple


class CADDocument:
    def __init__(self, path: Path, doc, temp_path: Path | None = None):
        self.path = path
        self.doc = doc
        self.temp_path = temp_path
        self.modelspace = doc.modelspace()
        self.layers = self._collect_layers()

    def _collect_layers(self) -> list[str]:
        layers = {entity.dxf.layer for entity in self.modelspace if hasattr(entity.dxf, 'layer')}
        return sorted(layers)

    def extract_primitives(self, layer_name: str) -> list[GraphicPrimitive]:
        primitives: list[GraphicPrimitive] = []
        if not layer_name:
            return primitives

        for entity in self.modelspace.query(f'*[layer=="{layer_name}"]'):
            dtype = entity.dxftype()
            if dtype == 'LINE':
                start = entity.dxf.start
                end = entity.dxf.end
                primitives.append(GraphicPrimitive('line', layer_name, ((start.x, start.y), (end.x, end.y))))
            elif dtype == 'LWPOLYLINE':
                points = [(point[0], point[1]) for point in entity.get_points('xy')]
                if points:
                    primitives.append(GraphicPrimitive('polyline', layer_name, (tuple(points), bool(entity.closed))))
            elif dtype == 'POLYLINE':
                points = [(vertex.dxf.location.x, vertex.dxf.location.y) for vertex in entity.vertices]
                if points:
                    closed = bool(getattr(entity, 'is_closed', False))
                    primitives.append(GraphicPrimitive('polyline', layer_name, (tuple(points), closed)))
            elif dtype == 'CIRCLE':
                center = entity.dxf.center
                primitives.append(GraphicPrimitive('circle', layer_name, ((center.x, center.y), entity.dxf.radius)))
            elif dtype == 'ARC':
                center = entity.dxf.center
                primitives.append(
                    GraphicPrimitive(
                        'arc',
                        layer_name,
                        ((center.x, center.y), entity.dxf.radius, entity.dxf.start_angle, entity.dxf.end_angle),
                    )
                )
            elif dtype == 'POINT':
                location = entity.dxf.location
                primitives.append(GraphicPrimitive('point', layer_name, (location.x, location.y)))
            elif dtype == 'INSERT':
                insert = entity.dxf.insert
                primitives.append(GraphicPrimitive('insert', layer_name, (insert.x, insert.y, entity.dxf.name)))
        return primitives


def load_cad_document(path: str | Path) -> CADDocument:
    cad_path = Path(path)
    suffix = cad_path.suffix.lower()
    if suffix == '.dxf':
        document = ezdxf.readfile(cad_path)
        return CADDocument(cad_path, document)

    if suffix == '.dwg':
        if not odafc.is_installed():
            return _load_dwg_via_autocad(cad_path)
        document = odafc.readfile(str(cad_path))
        return CADDocument(cad_path, document)

    raise RuntimeError(f'Unsupported CAD format: {cad_path.suffix}')


def _call_with_retry(func, attempts: int = 12, delay: float = 0.5):
    last_error = None
    for _ in range(attempts):
        try:
            return func()
        except Exception as exc:
            last_error = exc
            if 'Call was rejected by callee' not in str(exc):
                raise
            time.sleep(delay)
    if last_error is not None:
        raise last_error
    raise RuntimeError('AutoCAD automation call failed unexpectedly.')


def _load_dwg_via_autocad(cad_path: Path) -> CADDocument:
    if com_client is None:
        raise RuntimeError(
            'DWG loading requires ODA File Converter or AutoCAD COM support. '
            'Install ODA File Converter, or add comtypes/AutoCAD automation support.'
        )

    temp_dir = Path(tempfile.gettempdir()) / 'smart_footing_cad'
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_dxf = temp_dir / f'{cad_path.stem}_{int(time.time() * 1000)}.dxf'

    acad = None
    drawing = None
    try:
        acad = _call_with_retry(lambda: com_client.CreateObject('AutoCAD.Application', dynamic=True))
        _call_with_retry(lambda: setattr(acad, 'Visible', False))
        drawing = _call_with_retry(lambda: acad.Documents.Open(str(cad_path.resolve())))
        _call_with_retry(lambda: drawing.SaveAs(str(temp_dxf.resolve())))
        _call_with_retry(lambda: drawing.Close(False))
        drawing = None
        document = ezdxf.readfile(temp_dxf)
        return CADDocument(cad_path, document, temp_path=temp_dxf)
    except Exception as exc:
        if temp_dxf.exists():
            temp_dxf.unlink(missing_ok=True)
        raise RuntimeError(
            'Failed to load DWG via AutoCAD automation. '
            'Open the DWG once in AutoCAD and try again, or export it to DXF. '
            f'Details: {exc}'
        ) from exc
    finally:
        try:
            if drawing is not None:
                drawing.Close(False)
        except Exception:
            pass


class CADGraphicsView(QtWidgets.QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setScene(QtWidgets.QGraphicsScene(self))
        self.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QtGui.QPainter.RenderHint.TextAntialiasing)
        self.setBackgroundBrush(QtGui.QColor('#F8FAFC'))
        self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

    def wheelEvent(self, event: QtGui.QWheelEvent):
        zoom_factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(zoom_factor, zoom_factor)


class CADLayerViewer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('CAD Layer Viewer Prototype')
        self.resize(1200, 800)

        self.document: CADDocument | None = None

        self.file_path = QtWidgets.QLineEdit()
        self.file_path.setPlaceholderText('Select .dxf or .dwg file')
        self.file_path.setReadOnly(True)

        self.btn_open = QtWidgets.QPushButton('Open CAD File')
        self.btn_open.clicked.connect(self.open_cad_file)

        self.cmb_shape = QtWidgets.QComboBox()
        self.cmb_column = QtWidgets.QComboBox()
        self.cmb_point = QtWidgets.QComboBox()
        for combo in (self.cmb_shape, self.cmb_column, self.cmb_point):
            combo.currentIndexChanged.connect(self.refresh_preview)

        self.info_box = QtWidgets.QTextEdit()
        self.info_box.setReadOnly(True)
        self.info_box.setMaximumHeight(140)
        self.info_box.setPlainText(
            'Open a DXF or DWG file to inspect its layers.\n'
            'DWG loading uses ODA File Converter if available, otherwise AutoCAD on this machine.'
        )

        self.view = CADGraphicsView()

        form = QtWidgets.QFormLayout()
        form.addRow('1. Shape Layer', self.cmb_shape)
        form.addRow('2. Column Layer', self.cmb_column)
        form.addRow('3. Point Layer', self.cmb_point)

        file_row = QtWidgets.QHBoxLayout()
        file_row.addWidget(self.file_path)
        file_row.addWidget(self.btn_open)

        left_panel = QtWidgets.QVBoxLayout()
        left_panel.addLayout(file_row)
        left_panel.addLayout(form)
        left_panel.addWidget(self.info_box)
        left_panel.addStretch(1)

        layout = QtWidgets.QHBoxLayout(self)
        sidebar = QtWidgets.QWidget()
        sidebar.setLayout(left_panel)
        sidebar.setMaximumWidth(360)
        layout.addWidget(sidebar)
        layout.addWidget(self.view, 1)

    def _make_pen(self, color: str, width: float, dashed: bool = False):
        pen = QtGui.QPen(QtGui.QColor(color), width)
        pen.setCosmetic(True)
        if dashed:
            pen.setStyle(QtCore.Qt.PenStyle.DashLine)
        return pen

    def _primitive_bounds(self, primitive: GraphicPrimitive) -> QtCore.QRectF:
        kind = primitive.kind
        if kind == 'line':
            (x1, y1), (x2, y2) = primitive.data
            return QtCore.QRectF(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1)).normalized()
        if kind == 'polyline':
            points, _ = primitive.data
            xs = [point[0] for point in points]
            ys = [point[1] for point in points]
            return QtCore.QRectF(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)).normalized()
        if kind == 'circle':
            (cx, cy), radius = primitive.data
            return QtCore.QRectF(cx - radius, cy - radius, radius * 2.0, radius * 2.0)
        if kind == 'arc':
            (cx, cy), radius, _, _ = primitive.data
            return QtCore.QRectF(cx - radius, cy - radius, radius * 2.0, radius * 2.0)
        if kind == 'point':
            x_val, y_val = primitive.data
            return QtCore.QRectF(x_val, y_val, 0.0, 0.0)
        if kind == 'insert':
            x_val, y_val, _ = primitive.data
            return QtCore.QRectF(x_val, y_val, 0.0, 0.0)
        return QtCore.QRectF()

    def _compute_content_rect(self, primitives: list[GraphicPrimitive]) -> QtCore.QRectF:
        rect = QtCore.QRectF()
        has_rect = False
        for primitive in primitives:
            primitive_rect = self._primitive_bounds(primitive)
            if primitive_rect.isNull() and primitive_rect.width() == 0.0 and primitive_rect.height() == 0.0:
                primitive_rect = primitive_rect.adjusted(-0.01, -0.01, 0.01, 0.01)
            rect = rect.united(primitive_rect) if has_rect else primitive_rect
            has_rect = True
        if not has_rect:
            return QtCore.QRectF()
        return rect.normalized()

    def _fit_scene_to_rect(self, content_rect: QtCore.QRectF):
        span = max(content_rect.width(), content_rect.height(), 1.0)
        padding = max(span * 0.08, span * 0.02)
        padded = content_rect.adjusted(-padding, -padding, padding, padding)
        self.view.scene().setSceneRect(padded)
        self.view.resetTransform()
        self.view.fitInView(padded, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        self.view.scale(1.0, -1.0)

    def open_cad_file(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Open CAD file',
            '',
            'CAD Files (*.dxf *.dwg);;DXF Files (*.dxf);;DWG Files (*.dwg)',
        )
        if not file_name:
            return

        try:
            self.document = load_cad_document(file_name)
        except Exception as exc:
            show_critical(self, 'CAD Load Error', str(exc))
            return

        self.file_path.setText(str(self.document.path))
        self.populate_layer_combos(self.document.layers)
        self.refresh_preview()

    def populate_layer_combos(self, layers: list[str]):
        combo_pairs = [
            (self.cmb_shape, 'shape'),
            (self.cmb_column, 'column'),
            (self.cmb_point, 'point'),
        ]
        for combo, keyword in combo_pairs:
            combo.blockSignals(True)
            combo.clear()
            combo.addItem('')
            combo.addItems(layers)
            default_index = next((index for index, name in enumerate(layers, start=1) if keyword in name.lower()), 0)
            combo.setCurrentIndex(default_index)
            combo.blockSignals(False)

    def refresh_preview(self):
        scene = self.view.scene()
        scene.clear()

        if self.document is None:
            self.info_box.setPlainText('Open a DXF or DWG file to inspect its layers.')
            return

        shape_layer = self.cmb_shape.currentText()
        column_layer = self.cmb_column.currentText()
        point_layer = self.cmb_point.currentText()

        summary_lines = [
            f'File: {self.document.path.name}',
            f'Layers found: {len(self.document.layers)}',
            f'Imported from temp DXF: {self.document.temp_path.name if self.document.temp_path else "no"}',
            f'Shape layer: {shape_layer or "-"}',
            f'Column layer: {column_layer or "-"}',
            f'Point layer: {point_layer or "-"}',
        ]

        selections = []
        all_primitives: list[GraphicPrimitive] = []
        for layer_name, pen, brush in [
            (shape_layer, self._make_pen('#2563EB', 2.2), QtGui.QBrush(QtGui.QColor(37, 99, 235, 35))),
            (column_layer, self._make_pen('#D97706', 2.0), QtGui.QBrush(QtGui.QColor(217, 119, 6, 40))),
            (point_layer, self._make_pen('#059669', 2.0), QtGui.QBrush(QtGui.QColor(5, 150, 105, 120))),
        ]:
            primitives = self.document.extract_primitives(layer_name)
            selections.append((layer_name, pen, brush, primitives))
            if layer_name:
                summary_lines.append(f'{layer_name}: {len(primitives)} entities')
            all_primitives.extend(primitives)

        content_rect = self._compute_content_rect(all_primitives)
        span = max(content_rect.width(), content_rect.height(), 1.0) if not content_rect.isNull() else 1.0
        marker_size = max(span * 0.035, 0.06)
        label_height = max(span * 0.025, 0.12)

        has_geometry = False
        for layer_name, pen, brush, primitives in selections:
            for primitive in primitives:
                item = self._add_primitive(scene, primitive, pen, brush, marker_size, label_height)
                if item is not None:
                    has_geometry = True

        self.info_box.setPlainText('\n'.join(summary_lines))
        if has_geometry:
            self._fit_scene_to_rect(content_rect)
        else:
            scene.setSceneRect(QtCore.QRectF(-100, -100, 200, 200))

    def _add_primitive(self, scene, primitive: GraphicPrimitive, pen, brush, marker_size: float, label_height: float):
        kind = primitive.kind
        if kind == 'line':
            (x1, y1), (x2, y2) = primitive.data
            return scene.addLine(x1, y1, x2, y2, pen)
        if kind == 'polyline':
            points, closed = primitive.data
            polygon = QtGui.QPolygonF([QtCore.QPointF(x, y) for x, y in points])
            if closed:
                return scene.addPolygon(polygon, pen, brush)
            item = QtWidgets.QGraphicsPathItem()
            path = QtGui.QPainterPath()
            if points:
                path.moveTo(points[0][0], points[0][1])
                for x_val, y_val in points[1:]:
                    path.lineTo(x_val, y_val)
            item.setPath(path)
            item.setPen(pen)
            scene.addItem(item)
            return item
        if kind == 'circle':
            (cx, cy), radius = primitive.data
            return scene.addEllipse(cx - radius, cy - radius, radius * 2, radius * 2, pen, brush)
        if kind == 'arc':
            (cx, cy), radius, start_angle, end_angle = primitive.data
            rect = QtCore.QRectF(cx - radius, cy - radius, radius * 2, radius * 2)
            item = QtWidgets.QGraphicsPathItem()
            path = QtGui.QPainterPath()
            start_rad = math.radians(start_angle)
            start_point = QtCore.QPointF(cx + radius * math.cos(start_rad), cy + radius * math.sin(start_rad))
            path.moveTo(start_point)
            span_angle = end_angle - start_angle
            path.arcTo(rect, start_angle, span_angle)
            item.setPath(path)
            item.setPen(pen)
            scene.addItem(item)
            return item
        if kind == 'point':
            x_val, y_val = primitive.data
            radius = marker_size
            group = QtWidgets.QGraphicsItemGroup()
            circle = scene.addEllipse(x_val - radius, y_val - radius, radius * 2, radius * 2, pen, brush)
            line1 = scene.addLine(x_val - radius * 1.8, y_val, x_val + radius * 1.8, y_val, pen)
            line2 = scene.addLine(x_val, y_val - radius * 1.8, x_val, y_val + radius * 1.8, pen)
            group.addToGroup(circle)
            group.addToGroup(line1)
            group.addToGroup(line2)
            scene.addItem(group)
            return group
        if kind == 'insert':
            x_val, y_val, block_name = primitive.data
            text = scene.addText(block_name)
            text.setDefaultTextColor(pen.color())
            font = text.font()
            font.setPointSizeF(10.0)
            text.setFont(font)
            text.setScale(label_height / max(text.boundingRect().height(), 1.0))
            text.setPos(x_val, y_val)
            return text
        return None


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = CADLayerViewer()
    window.show()
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())