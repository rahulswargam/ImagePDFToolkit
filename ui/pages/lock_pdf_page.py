import os

from PySide6.QtWidgets import QApplication, QFileDialog, QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

import activity_store
from tools.lock_pdf import lock_pdf
from ui import icons as icon_lib
from ui.components.buttons import AnimatedButton, ProcessingBar
from ui.components.feedback import CompletionDialog
from ui.components.inputs import PasswordField
from ui.components.pdf_preview import PdfPreviewCard
from ui.components.workspace import DropWorkspace

EXTENSIONS = (".pdf",)
_ACCENT = "#ef4444"


class LockPdfPage(QWidget):

    def __init__(self, notify, parent=None):
        super().__init__(parent)

        self.notify = notify
        self.input_path = None
        self._last_output_folder = None
        self._preview_card = None

        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 15, 0, 0)
        main_layout.setSpacing(16)

        header = QHBoxLayout()
        header.setSpacing(10)
        shield_icon = QLabel()
        shield_icon.setPixmap(icon_lib.get_pixmap("shield", _ACCENT, 22))
        header.addWidget(shield_icon)
        header_text = QLabel("Encrypts your PDF with a password so only people who know it can open it.")
        header_text.setObjectName("pageSubtitle")
        header_text.setWordWrap(True)
        header.addWidget(header_text, 1)
        main_layout.addLayout(header)

        self.drop_workspace = DropWorkspace(
            EXTENSIONS,
            _ACCENT,
            multiple=False,
            title="Drop a PDF here",
            subtitle="Drag & drop a PDF, or click to browse",
            hint="PDF",
        )
        self.drop_workspace.filesDropped.connect(lambda paths: self.load_pdf(paths[0]))
        self.drop_workspace.browseRequested.connect(self.select_pdf)
        main_layout.addWidget(self.drop_workspace)

        self.preview_container = QVBoxLayout()
        main_layout.addLayout(self.preview_container)

        settings_card = QFrame()
        settings_card.setObjectName("toolCard")

        settings_layout = QVBoxLayout(settings_card)
        settings_layout.setContentsMargins(20, 18, 20, 18)
        settings_layout.setSpacing(14)

        settings_title = QLabel("Set Password")
        settings_title.setObjectName("toolTitle")
        settings_layout.addWidget(settings_title)

        self.password_field = PasswordField("Password", show_strength=True)
        settings_layout.addWidget(self.password_field)

        self.confirm_field = PasswordField("Confirm password")
        settings_layout.addWidget(self.confirm_field)

        main_layout.addWidget(settings_card)

        self.lock_button = AnimatedButton("Protect PDF")
        self.lock_button.setObjectName("toolButton")
        self.lock_button.setMinimumHeight(45)
        self.lock_button.clicked.connect(self.lock)
        main_layout.addWidget(self.lock_button)

        self.processing_bar = ProcessingBar()
        main_layout.addWidget(self.processing_bar)

        main_layout.addStretch()

    def select_pdf(self):

        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")

        if file_path:
            self.load_pdf(file_path)

    def load_pdf(self, file_path):

        self.input_path = file_path

        if self._preview_card is not None:
            self._preview_card.setParent(None)
            self._preview_card.deleteLater()

        self._preview_card = PdfPreviewCard(file_path)
        self._preview_card.removed.connect(self._clear_pdf)
        self.preview_container.addWidget(self._preview_card)

        self.drop_workspace.set_text(os.path.basename(file_path), "Drop a different PDF or click to replace")

    def _clear_pdf(self):
        self.input_path = None

        if self._preview_card is not None:
            self._preview_card.setParent(None)
            self._preview_card.deleteLater()
            self._preview_card = None

        self.drop_workspace.set_text("Drop a PDF here", "Drag & drop a PDF, or click to browse")

    def lock(self):

        if not self.input_path:
            CompletionDialog.warn(self, "No PDF Selected", "Please select a PDF first.")
            return

        password = self.password_field.text()
        confirm = self.confirm_field.text()

        if not password:
            CompletionDialog.warn(self, "Missing Password", "Please enter a password.")
            return

        if password != confirm:
            CompletionDialog.warn(self, "Password Mismatch", "Passwords do not match.")
            return

        self.lock_button.set_processing(True, "Protecting…")
        self.processing_bar.show()
        QApplication.processEvents()

        try:
            output_path = lock_pdf(self.input_path, password)
            self._last_output_folder = os.path.dirname(output_path)

            activity_store.record("lock", os.path.basename(output_path), "Password protected")

            self.password_field.clear()
            self.confirm_field.clear()

            self.lock_button.set_processing(False)
            self.processing_bar.hide()

            CompletionDialog.success(
                self,
                "Processing complete",
                "PDF protected successfully.",
                open_folder=self._open_output_folder,
            )

        except Exception as error:
            self.lock_button.set_processing(False)
            self.processing_bar.hide()
            CompletionDialog.error(self, "Processing Failed", f"Unable to protect this PDF.\n\n{error}")

    def _open_output_folder(self):
        if self._last_output_folder and os.path.isdir(self._last_output_folder):
            os.startfile(self._last_output_folder)
