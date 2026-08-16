import os

from PySide6.QtWidgets import QApplication, QFileDialog, QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from tools.unlock_pdf import unlock_pdf
from ui import icons as icon_lib
from ui.components.buttons import AnimatedButton, ProcessingBar
from ui.components.feedback import CompletionDialog
from ui.components.inputs import PasswordField
from ui.components.pdf_preview import PdfPreviewCard
from ui.components.workspace import DropWorkspace

EXTENSIONS = (".pdf",)
_ACCENT = "#ef4444"


class UnlockPdfPage(QWidget):

    def __init__(self, notify, parent=None):
        super().__init__(parent)

        self.notify = notify
        self.input_path = None
        self._last_output_path = None
        self._preview_card = None

        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 15, 0, 0)
        main_layout.setSpacing(16)

        header = QHBoxLayout()
        header.setSpacing(10)
        shield_icon = QLabel()
        shield_icon.setPixmap(icon_lib.get_pixmap("unlock", _ACCENT, 22))
        header.addWidget(shield_icon)
        header_text = QLabel("Removes password protection from a PDF you already have access to.")
        header_text.setObjectName("pageSubtitle")
        header_text.setWordWrap(True)
        header.addWidget(header_text, 1)
        main_layout.addLayout(header)

        self.drop_workspace = DropWorkspace(
            EXTENSIONS,
            _ACCENT,
            multiple=False,
            title="Drop a locked PDF here",
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

        settings_title = QLabel("Current Password")
        settings_title.setObjectName("toolTitle")
        settings_layout.addWidget(settings_title)

        self.password_field = PasswordField("Password")
        settings_layout.addWidget(self.password_field)

        main_layout.addWidget(settings_card)

        self.unlock_button = AnimatedButton("Unlock PDF")
        self.unlock_button.setObjectName("toolButton")
        self.unlock_button.setMinimumHeight(45)
        self.unlock_button.clicked.connect(self.unlock)
        main_layout.addWidget(self.unlock_button)

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

        self.drop_workspace.set_text("Drop a locked PDF here", "Drag & drop a PDF, or click to browse")

    def unlock(self):

        if not self.input_path:
            CompletionDialog.warn(self, "No PDF Selected", "Please select a PDF first.")
            return

        self.unlock_button.set_processing(True, "Unlocking…")
        self.processing_bar.show()
        QApplication.processEvents()

        try:
            output_path = unlock_pdf(self.input_path, self.password_field.text())
            self._last_output_path = output_path

            self.password_field.clear()

            self.unlock_button.set_processing(False)
            self.processing_bar.hide()

            CompletionDialog.success(
                self,
                "Processing complete",
                "PDF unlocked successfully.",
                open_file=self._open_output_file,
            )

        except Exception as error:
            self.unlock_button.set_processing(False)
            self.processing_bar.hide()
            CompletionDialog.error(self, "Processing Failed", f"Unable to unlock this PDF.\n\n{error}")

    def _open_output_file(self):
        if self._last_output_path and os.path.isfile(self._last_output_path):
            os.startfile(self._last_output_path)
