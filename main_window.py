from pathlib import Path

from PyQt6 import QtCore, QtWidgets

from .styles import APP_STYLE
from .ui.common_controls import show_warning
from .ui.licensing.license_manager import (
    LICENSE_TYPE_TRIAL,
    LicenseStatus,
    current_license_status,
)
from .ui.project.project_document import (
    PROJECT_DOCUMENT_FILE_FILTER,
    read_project_document,
)
from .ui.project.recent_projects import add_recent_project, remove_recent_project
from .ui.start_page import StartPage
from .ui.workspace_page import WorkspacePage


class FootingRebuildMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Footing Design Rebuild Shell')
        self.setFixedSize(850, 850)

        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        self.start_page = StartPage()
        self.workspace_page = WorkspacePage()
        self.stack.addWidget(self.start_page)
        self.stack.addWidget(self.workspace_page)

        self.start_page.newRequested.connect(self.create_new_project)
        self.start_page.openRequested.connect(self.open_project_dialog)
        self.start_page.recentProjectRequested.connect(self.open_project_file)
        self.start_page.license_panel.licenseChanged.connect(self._apply_license_status)
        self.workspace_page.projectSaved.connect(self._handle_project_saved)
        self.start_page.refresh_recent_projects()
        self.setStyleSheet(APP_STYLE)
        self._license_status = self._resolve_startup_license_status()
        self.workspace_page.apply_license_status(self._license_status)
        self._apply_license_status()
        self._license_refresh_timer = QtCore.QTimer(self)
        self._license_refresh_timer.setInterval(1500)
        self._license_refresh_timer.timeout.connect(self._poll_start_page_license_status)
        self._license_refresh_timer.start()

    def _center_on_active_screen(self):
        screen = self.screen()
        if screen is None:
            screen = QtWidgets.QApplication.primaryScreen()
        if screen is None:
            return

        available = screen.availableGeometry()
        frame = self.frameGeometry()
        frame.moveCenter(available.center())
        top_left = frame.topLeft()
        self.move(top_left)

    def _activate_workspace(self) -> None:
        self.setMaximumSize(16777215, 16777215)
        self.setMinimumSize(1360, 860)
        if self.width() < 1360 or self.height() < 860:
            self.resize(max(self.width(), 1360), max(self.height(), 860))
        self._center_on_active_screen()

    def _resolve_startup_license_status(self) -> LicenseStatus:
        return current_license_status()

    def _apply_license_status(self) -> None:
        self._license_status = self._resolve_startup_license_status()
        if self._license_status.valid and self._license_status.license_type == LICENSE_TYPE_TRIAL:
            title = 'Trial Active'
        else:
            title = 'License Activated' if self._license_status.valid else 'License Required'
        self.start_page.set_license_status(
            valid=self._license_status.valid,
            title=title,
            message=self._license_status.message,
        )
        self.workspace_page.apply_license_status(self._license_status)

    def _poll_start_page_license_status(self) -> None:
        if self.stack.currentWidget() is not self.start_page:
            return
        self._apply_license_status()

    def _ensure_license_ready(self) -> bool:
        self._apply_license_status()
        if self._license_status.valid:
            return True
        self.open_license_dialog()
        self._apply_license_status()
        if self._license_status.valid:
            return True
        show_warning(self, 'License Activation', 'A valid machine-bound license is required before using the application.')
        return False

    def create_new_project(self):
        if not self._ensure_license_ready():
            return
        self._activate_workspace()
        self.workspace_page.initialize_project()
        self.stack.setCurrentWidget(self.workspace_page)

    def open_project_dialog(self) -> None:
        if not self._ensure_license_ready():
            return
        file_path, _selected_filter = QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Open Smart Footing Project',
            '',
            PROJECT_DOCUMENT_FILE_FILTER,
        )
        if file_path:
            self.open_project_file(file_path)

    def open_project_file(self, file_path: str) -> None:
        if not self._ensure_license_ready():
            return
        document_path = Path(file_path)
        if not document_path.exists():
            remove_recent_project(file_path)
            self.start_page.refresh_recent_projects()
            show_warning(self, 'Open Smart Footing Project', 'The selected project file could not be found.')
            return

        try:
            payload = read_project_document(file_path)
        except Exception as exc:
            show_warning(self, 'Open Smart Footing Project', f'Could not open the selected project.\n\n{exc}')
            return

        self._activate_workspace()
        self.workspace_page.import_project_document_payload(payload, file_path=file_path)
        self.stack.setCurrentWidget(self.workspace_page)
        project_name = str(payload.get('projectName', '') or '').strip()
        add_recent_project(file_path, project_name)
        self.start_page.refresh_recent_projects()

    def _handle_project_saved(self, file_path: str, project_name: str) -> None:
        add_recent_project(file_path, project_name)
        self.start_page.refresh_recent_projects()

    def open_license_dialog(self) -> None:
        self.stack.setCurrentWidget(self.start_page)
        self.start_page.show_license_page()
        self._apply_license_status()
