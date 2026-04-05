PROJECT_FOCUS_BACKGROUND = '__PROJECT_FOCUS_BACKGROUND__'
PROJECT_FOCUS_BORDER = '__PROJECT_FOCUS_BORDER__'
FOCUS_BACKGROUND_COLOR = '#F0F9FF'
FOCUS_BORDER_COLOR = '#2563EB'

APP_STYLE_TEMPLATE = '''
QMainWindow {
    background: #0F172A;
}
QWidget {
    font-family: "Prompt", "Segoe UI", sans-serif;
    font-size: 10pt;
    color: #0F172A;
}
QDialog#appDialog {
    background: #F8FAFC;
}
#startCard, #monitorPanel {
    background: #F8FAFC;
    border: 1px solid #CBD5E1;
    border-radius: 0px;
    color: #0F172A;
}
#startShell {
    background: transparent;
    border: none;
}
#startNavRail {
    background: #E2E8F0;
    border-right: 1px solid #CBD5E1;
    min-width: 148px;
    max-width: 148px;
}
#startNavButton {
    background: transparent;
    color: #334155;
    border: none;
    border-radius: 0px;
    min-height: 54px;
    padding: 0 18px;
    font-size: 11pt;
    font-weight: 700;
    text-align: left;
}
#startNavButton:hover {
    background: #93C5FD;
    color: #0B1220;
}
#startNavButton[active='true'] {
    background: #2563EB;
    color: #FFFFFF;
}
#startRecentList {
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 8px;
}
#startRecentList::item {
    min-height: 32px;
    padding: 8px 10px;
    border-radius: 5px;
}
#startRecentList::item:selected {
    background: #DBEAFE;
    color: #0F172A;
}
#monitorViewport {
    background: #FAF9F6;
    border: none;
    border-radius: 0px;
}
#monitorOverlay {
    background: rgba(255, 255, 255, 0.86);
    border: 1px solid #CBD5E1;
    border-radius: 6px;
}
#drawingOverlay {
    background: rgba(255, 255, 255, 0.86);
    border: 1px solid #CBD5E1;
    border-radius: 6px;
}
#viewOverlayButton {
    background: transparent;
    color: #334155;
    border: 1px solid #CBD5E1;
    border-radius: 5px;
    min-width: 42px;
    max-width: 42px;
    min-height: 28px;
    max-height: 28px;
    padding: 0;
    font-size: 9pt;
    font-weight: 700;
}
#viewOverlayButtonWide {
    background: transparent;
    color: #334155;
    border: 1px solid #CBD5E1;
    border-radius: 5px;
    min-width: 58px;
    max-width: 58px;
    min-height: 28px;
    max-height: 28px;
    padding: 0;
    font-size: 8.5pt;
    font-weight: 700;
}
#viewOverlayButton:hover {
    background: #CFFAFE;
    border-color: #06B6D4;
}
#viewOverlayButtonWide:hover {
    background: #CFFAFE;
    border-color: #06B6D4;
}
#viewOverlayButton[active="true"] {
    background: #DBEAFE;
    color: #334155;
    border: 2px solid #2563EB;
}
#viewOverlayButtonWide[active="true"] {
    background: #DBEAFE;
    color: #334155;
    border: 2px solid #2563EB;
}
#drawingToolButton {
    background: transparent;
    color: #334155;
    border: 1px solid #CBD5E1;
    border-radius: 5px;
    min-width: 42px;
    max-width: 42px;
    min-height: 42px;
    max-height: 42px;
    padding: 0;
    font-size: 8.5pt;
    font-weight: 700;
}
#drawingToolButton:hover {
    background: #CFFAFE;
    border-color: #06B6D4;
}
#drawingToolButton[active="true"] {
    background: transparent;
    color: #334155;
    border: 2px solid #2563EB;
}
#drawingStatus {
    background: #FFFFFF;
    color: #475569;
    border: 1px solid #CBD5E1;
    border-radius: 5px;
    padding: 10px 12px;
}
#heroTitle {
    color: #0F172A;
    font-size: 19pt;
    font-weight: 700;
}
#panelTitle, #monitorTitle {
    color: #0F172A;
    font-size: 12pt;
    font-weight: 700;
}
#sectionTitle {
    color: #0F172A;
    font-size: 10pt;
    font-weight: 700;
}
#hintText {
    color: #475569;
}
#materialFieldLabel {
    color: #334155;
    font-size: 8.5pt;
    font-weight: 600;
}
#sectionCard {
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
}
#sectionCard[muted='true'] {
    background: #F8FAFC;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
}
#accordionCard {
    background: #F8FAFC;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
}
#accordionHeader {
    background: #F1F5F9;
    color: #0F172A;
    border: none;
    border-bottom: 1px solid #CBD5E1;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    min-height: 38px;
    padding: 0 12px;
    font-weight: 700;
    text-align: left;
}
#accordionHeader:hover {
    background: #E0F2FE;
}
#accordionHeader[expanded='true'] {
    background: #ECFDF5;
    border-bottom: 1px solid #BBF7D0;
    color: #166534;
}
#accordionContent {
    background: #FFFFFF;
    border-bottom-left-radius: 8px;
    border-bottom-right-radius: 8px;
}
#accordionItemButton {
    background: transparent;
    color: #0F172A;
    border: 1px solid transparent;
    border-radius: 6px;
    min-height: 30px;
    padding: 0 10px 0 16px;
    text-align: left;
    font-weight: 400;
}
#accordionItemButton:hover {
    background: #E0F2FE;
    border-color: #7DD3FC;
}
#accordionItemButton:checked,
#accordionItemButton[selected='true'] {
    background: #DBEAFE;
    border-color: #60A5FA;
    color: #1D4ED8;
}
#segmentCard {
    background: #E2E8F0;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
}
#segmentButton {
    background: transparent;
    color: #475569;
    border: none;
    border-radius: 5px;
    min-height: 32px;
    padding: 0 12px;
    font-weight: 700;
}
#segmentButton:checked {
    background: #16A34A;
    color: #FFFFFF;
    border: 1px solid #166534;
}
#primaryButton {
    background: #16A34A;
    color: white;
    border: 1px solid #166534;
    border-radius: 5px;
    min-height: 34px;
    padding: 0 14px;
    font-weight: 700;
}
#primaryButton:hover {
    background: #15803D;
    border-color: #14532D;
}
#primaryButton:disabled {
    background: #BBF7D0;
    color: #F8FAFC;
    border-color: #86EFAC;
}
#secondaryButton, QPushButton {
    background: #FFFFFF;
    color: #0F172A;
    border: 1px solid #94A3B8;
    border-radius: 5px;
    min-height: 32px;
    padding: 0 12px;
    font-weight: 700;
}
#secondaryButton:hover, QPushButton:hover {
    background: #CFFAFE;
    border-color: #06B6D4;
}
#secondaryButton:disabled, QPushButton:disabled {
    background: #F8FAFC;
    color: #94A3B8;
    border-color: #CBD5E1;
}
#calToggleButton {
    background: #FFFFFF;
    color: #0F172A;
    border: 1px solid #94A3B8;
    border-radius: 5px;
    min-height: 32px;
    max-height: 32px;
    padding: 0 12px;
    font-weight: 700;
}
#calToggleButton:hover {
    background: #FFEDD5;
    border-color: #F97316;
}
#calToggleButton:checked {
    background: #F97316;
    color: #FFFFFF;
    border: 1px solid #C2410C;
}
#calToggleButton:checked:hover {
    background: #EA580C;
    border-color: #9A3412;
}
#calToggleButton:disabled {
    background: #F8FAFC;
    color: #94A3B8;
    border-color: #CBD5E1;
}
#calAllButton {
    background: #FFFFFF;
    color: #0F172A;
    border: 1px solid #94A3B8;
    border-radius: 5px;
    min-height: 32px;
    max-height: 32px;
    padding: 0 12px;
    font-weight: 700;
}
#calAllButton:hover {
    background: #DBEAFE;
    border-color: #3B82F6;
}
#calAllButton:pressed {
    background: #3B82F6;
    color: #FFFFFF;
    border-color: #1D4ED8;
}
#calAllButton:disabled {
    background: #F8FAFC;
    color: #94A3B8;
    border-color: #CBD5E1;
}
#pickerButton {
    background: #FFFFFF;
    color: #0F172A;
    border: 1px solid #94A3B8;
    border-radius: 11px;
    outline: none;
    min-height: 36px;
    padding: 0 14px;
    font-weight: 600;
    text-align: left;
}
#pickerButton[compact='true'] {
    min-height: 30px;
    max-height: 30px;
    padding: 0 8px;
    border-radius: 9px;
    font-size: 9pt;
}
#pickerButton:focus {
    outline: none;
    background: __PROJECT_FOCUS_BACKGROUND__;
    border: 2px solid __PROJECT_FOCUS_BORDER__;
}
#pickerButton:hover {
    background: #F8FAFC;
    border-color: #64748B;
}
#pickerButton:disabled {
    background: #F8FAFC;
    color: #94A3B8;
    border-color: #CBD5E1;
}
QLineEdit:disabled {
    background: #F8FAFC;
    color: #94A3B8;
    border-color: #CBD5E1;
}
QLabel:disabled {
    color: #94A3B8;
}
#pickerPopup {
    background: #FFFFFF;
    border: 1px solid #94A3B8;
    border-radius: 14px;
    outline: none;
}
#pickerList {
    background: #FFFFFF;
    color: #0F172A;
    border: none;
    border-radius: 10px;
    outline: none;
    padding: 4px;
}
#pickerList:focus {
    outline: none;
    border: none;
}
#pickerList::item {
    min-height: 28px;
    padding: 6px 14px;
    border-radius: 10px;
    border: none;
}
#pickerList::item:hover {
    background: #CFFAFE;
    color: #0F172A;
    border: 1px solid #06B6D4;
}
#pickerList::item:selected {
    background: #DCFCE7;
    color: #0F172A;
    border: 1px solid #BBF7D0;
}
QTabBar::scroller {
    width: 88px;
}
QTabBar QToolButton {
    background: #0F172A;
    color: #E2E8F0;
    border: 1px solid #334155;
    border-radius: 6px;
    min-width: 36px;
    max-width: 36px;
    min-height: 28px;
    max-height: 28px;
    padding: 0;
    margin-top: 2px;
    margin-bottom: 4px;
}
QTabBar QToolButton#ScrollLeftButton {
    margin-right: 10px;
}
QTabBar QToolButton#ScrollRightButton {
    margin-left: 10px;
}
QTabBar QToolButton:hover {
    background: #1E293B;
}
QTabWidget::pane {
    border: 1px solid #334155;
    background: #F8FAFC;
    border-radius: 5px;
    top: 0px;
}
QTabBar::tab {
    background: #1E293B;
    color: #CBD5E1;
    border: 1px solid #334155;
    border-top-left-radius: 7px;
    border-top-right-radius: 7px;
    padding: 6px 10px;
    margin-right: 4px;
    min-width: 72px;
    min-height: 16px;
}
QTabBar::tab:selected {
    background: #F8FAFC;
    color: #0F172A;
}
QListWidget {
    background: white;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 5px;
    padding: 4px;
}
QLabel {
    color: #0F172A;
}
QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, QTableWidget {
    background: white;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 5px;
    padding: 2px 8px;
    min-height: 32px;
    outline: 0;
}
QTableWidget#setupDataTable {
    background: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 5px;
    padding: 0px;
    gridline-color: #CBD5E1;
}
QTableWidget#setupDataTable::item {
    padding: 0px;
    border: none;
}
QLineEdit[compact='true'] {
    min-height: 30px;
    max-height: 30px;
    padding: 1px 8px;
    font-size: 9pt;
}
QDoubleSpinBox, QSpinBox, QLineEdit {
    max-height: 32px;
    qproperty-alignment: AlignRight;
}
QDoubleSpinBox:disabled, QSpinBox:disabled {
    background: #F8FAFC;
    color: #94A3B8;
    border-color: #CBD5E1;
}
QLineEdit[readOnly="true"] {
    background: #F8FAFC;
    color: #64748B;
    border: 1px solid #CBD5E1;
}
QComboBox {
    max-height: 32px;
    qproperty-alignment: AlignLeft;
}
QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QSpinBox:focus {
    background: __PROJECT_FOCUS_BACKGROUND__;
    border: 2px solid __PROJECT_FOCUS_BORDER__;
    outline: 0;
}
QLineEdit[readOnly="true"]:focus {
    background: #F8FAFC;
    color: #64748B;
    border: 1px solid #CBD5E1;
    outline: 0;
}
QComboBox::drop-down {
    width: 24px;
    border: none;
}
QComboBox:on {
    outline: 0;
}
QComboBox QAbstractItemView {
    background: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 5px;
    outline: 0;
    selection-background-color: #DCFCE7;
    selection-color: #0F172A;
}
QComboBox QAbstractItemView::item:hover {
    background: #CFFAFE;
    color: #0F172A;
}
QAbstractItemView {
    background: #FFFFFF;
    color: #0F172A;
    alternate-background-color: #F8FAFC;
    selection-background-color: #DCFCE7;
    selection-color: #0F172A;
    outline: 0;
}
QAbstractItemView::item:hover {
    background: #CFFAFE;
    color: #0F172A;
}
QHeaderView::section {
    background: #E2E8F0;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    padding: 4px 6px;
    font-weight: 700;
}
QTableWidget QLineEdit {
    border: none;
    background: transparent;
    padding: 0 2px;
    min-height: 0px;
}
QToolButton {
    background: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 5px;
    min-height: 30px;
    padding: 0 10px;
    font-weight: 700;
}
QToolButton:checked {
    background: #2563EB;
    color: white;
    border-color: #1D4ED8;
}
QToolButton#stepButton {
    background: #FFFFFF;
    border: 1px solid #94A3B8;
    border-radius: 5px;
    min-width: 32px;
    max-width: 32px;
    min-height: 32px;
    max-height: 32px;
    padding: 0;
    font-size: 11pt;
}
QToolButton#stepButton:hover {
    background: #CFFAFE;
    border-color: #06B6D4;
}
QToolButton#stepButton:disabled {
    background: #F8FAFC;
    border-color: #CBD5E1;
}
QScrollArea#materialScrollArea {
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
}
QScrollArea#materialScrollArea > QWidget > QWidget {
    background: #FFFFFF;
}
QScrollArea#setupFormScrollArea {
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
}
QScrollArea#setupFormScrollArea > QWidget > QWidget {
    background: #FFFFFF;
}
QScrollBar:vertical {
    background: #E2E8F0;
    width: 12px;
    margin: 6px 3px 6px 0;
    border-radius: 6px;
}
QScrollBar::handle:vertical {
    background: #94A3B8;
    min-height: 52px;
    border-radius: 6px;
    border: 2px solid #E2E8F0;
}
QScrollBar::handle:vertical:hover {
    background: #64748B;
}
QScrollBar::handle:vertical:pressed {
    background: #475569;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
    background: transparent;
    border: none;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
}
QScrollBar:horizontal {
    background: #E2E8F0;
    height: 12px;
    margin: 0 6px 6px 6px;
    border-radius: 6px;
}
QScrollBar::handle:horizontal {
    background: #60A5FA;
    min-width: 56px;
    border-radius: 6px;
    border: 2px solid #E2E8F0;
}
QScrollBar::handle:horizontal:hover {
    background: #3B82F6;
}
QScrollBar::handle:horizontal:pressed {
    background: #2563EB;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
    background: transparent;
    border: none;
}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: transparent;
}
'''

APP_STYLE = (
    APP_STYLE_TEMPLATE.replace(PROJECT_FOCUS_BACKGROUND, FOCUS_BACKGROUND_COLOR)
    .replace(PROJECT_FOCUS_BORDER, FOCUS_BORDER_COLOR)
)
