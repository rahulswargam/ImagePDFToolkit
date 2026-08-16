import os

from PySide6.QtWidgets import QApplication, QFileDialog, QLabel, QVBoxLayout, QWidget

from tools.pdf_organize import split_pdf
from ui.components.buttons import AnimatedButton, ProcessingBar
from ui.components.feedback import CompletionDialog
from ui.components.pdf_preview import PdfPreviewCard
from ui.components.workspace import DropWorkspace

EXTENSIONS = (".pdf",)
_ACCENT = "#ef4444"


class SplitPdfPage(QWidget):

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

        note = QLabel("Every page becomes its own single-page PDF, saved into a new subfolder.")
        note.setObjectName("toolDescription")
        note.setWordWrap(True)
        main_layout.addWidget(note)

        self.split_button = AnimatedButton("Split PDF")
        self.split_button.setObjectName("toolButton")
        self.split_button.setMinimumHeight(45)
        self.split_button.setEnabled(False)
        self.split_button.clicked.connect(self.split)
        main_layout.addWidget(self.split_button)

        self.processing_bar = ProcessingBar()
        main_layout.addWidget(self.processing_bar)

        main_layout.addStretch()

    def select_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.load_pdf(file_path)

    def load_pdf(self, file_path):

        self.input_path = file_path
        self.split_button.setEnabled(True)

        if self._preview_card is not None:
            self._preview_card.setParent(None)
            self._preview_card.deleteLater()

        self._preview_card = PdfPreviewCard(file_path)
        self._preview_card.removed.connect(self._clear_pdf)
        self.preview_container.addWidget(self._preview_card)

        self.drop_workspace.set_text(os.path.basename(file_path), "Drop a different PDF or click to replace")

    def _clear_pdf(self):
        self.input_path = None
        self.split_button.setEnabled(False)

        if self._preview_card is not None:
            self._preview_card.setParent(None)
            self._preview_card.deleteLater()
            self._preview_card = None

        self.drop_workspace.set_text("Drop a PDF here", "Drag & drop a PDF, or click to browse")

    def split(self):

        if not self.input_path:
            CompletionDialog.warn(self, "No PDF Selected", "Please select a PDF first.")
            return

        self.split_button.set_processing(True, "Splitting…")
        self.processing_bar.show()
        QApplication.processEvents()

        try:
            output_paths = split_pdf(self.input_path)
            self._last_output_path = output_paths[0]

            self.split_button.set_processing(False)
            self.processing_bar.hide()

            plural = "pages" if len(output_paths) != 1 else "page"
            CompletionDialog.success(
                self,
                "Processing complete",
                f"Split into {len(output_paths)} separate {plural}.",
                open_file=self._open_output_file,
            )

        except Exception as error:
            self.split_button.set_processing(False)
            self.processing_bar.hide()
            CompletionDialog.error(self, "Processing Failed", f"Unable to split this PDF.\n\n{error}")

    def _open_output_file(self):
        if self._last_output_path and os.path.isfile(self._last_output_path):
            os.startfile(self._last_output_path)
