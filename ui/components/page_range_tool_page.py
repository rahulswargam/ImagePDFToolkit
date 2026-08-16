import os

from PySide6.QtWidgets import QApplication, QFileDialog, QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from tools.pdf_organize import get_page_count, parse_page_range
from ui.components.buttons import AnimatedButton, ProcessingBar
from ui.components.feedback import CompletionDialog
from ui.components.pdf_preview import PdfPreviewCard
from ui.components.inputs import LabeledLineEdit
from ui.components.workspace import DropWorkspace

EXTENSIONS = (".pdf",)
_ACCENT = "#ef4444"


class PageRangeToolPage(QWidget):
    """Base page for single-PDF tools driven by a 1-indexed page range
    string (e.g. "1,3,5-8"): Remove Pages, Extract Pages.

    Subclasses set BUTTON_LABEL, PROCESSING_TEXT, PLACEHOLDER, NOTE_TEXT,
    and override `process(input_path, pages_zero_indexed)` (must return
    output_path) and `success_message(output_path)`.
    """

    BUTTON_LABEL = "Apply"
    PROCESSING_TEXT = "Processing…"
    FIELD_LABEL = "Pages"
    PLACEHOLDER = "e.g. 1,3,5-8"
    NOTE_TEXT = ""

    def __init__(self, notify, parent=None):
        super().__init__(parent)

        self.notify = notify
        self.input_path = None
        self.page_count = 0
        self._last_output_folder = None
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

        card = QFrame()
        card.setObjectName("toolCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(14)

        title = QLabel(self.FIELD_LABEL)
        title.setObjectName("toolTitle")
        card_layout.addWidget(title)

        row = QHBoxLayout()
        self.range_field = LabeledLineEdit("Page Numbers", self.PLACEHOLDER)
        row.addWidget(self.range_field, 1)
        card_layout.addLayout(row)

        self.page_count_label = QLabel("")
        self.page_count_label.setObjectName("fileGridMeta")
        card_layout.addWidget(self.page_count_label)

        main_layout.addWidget(card)

        if self.NOTE_TEXT:
            note = QLabel(self.NOTE_TEXT)
            note.setObjectName("toolDescription")
            note.setWordWrap(True)
            main_layout.addWidget(note)

        self.apply_button = AnimatedButton(self.BUTTON_LABEL)
        self.apply_button.setObjectName("toolButton")
        self.apply_button.setMinimumHeight(45)
        self.apply_button.setEnabled(False)
        self.apply_button.clicked.connect(self.apply)
        main_layout.addWidget(self.apply_button)

        self.processing_bar = ProcessingBar()
        main_layout.addWidget(self.processing_bar)

        main_layout.addStretch()

    def process(self, input_path, pages_zero_indexed):
        raise NotImplementedError

    def success_message(self, output_path):
        return "Done."

    def select_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.load_pdf(file_path)

    def load_pdf(self, file_path):

        try:
            self.page_count = get_page_count(file_path)
        except Exception as error:
            CompletionDialog.error(self, "Unable to Open PDF", str(error))
            return

        self.input_path = file_path
        self.apply_button.setEnabled(True)

        if self._preview_card is not None:
            self._preview_card.setParent(None)
            self._preview_card.deleteLater()

        self._preview_card = PdfPreviewCard(file_path)
        self._preview_card.removed.connect(self._clear_pdf)
        self.preview_container.addWidget(self._preview_card)

        plural = "page" if self.page_count == 1 else "pages"
        self.page_count_label.setText(f"This PDF has {self.page_count} {plural}.")
        self.drop_workspace.set_text(os.path.basename(file_path), "Drop a different PDF or click to replace")

    def _clear_pdf(self):
        self.input_path = None
        self.page_count = 0
        self.apply_button.setEnabled(False)
        self.page_count_label.setText("")

        if self._preview_card is not None:
            self._preview_card.setParent(None)
            self._preview_card.deleteLater()
            self._preview_card = None

        self.drop_workspace.set_text("Drop a PDF here", "Drag & drop a PDF, or click to browse")

    def apply(self):

        if not self.input_path:
            CompletionDialog.warn(self, "No PDF Selected", "Please select a PDF first.")
            return

        try:
            pages = parse_page_range(self.range_field.text(), self.page_count)
        except ValueError as error:
            CompletionDialog.warn(self, "Invalid Page Numbers", str(error))
            return

        self.apply_button.set_processing(True, self.PROCESSING_TEXT)
        self.processing_bar.show()
        QApplication.processEvents()

        try:
            output_path = self.process(self.input_path, pages)
            self._last_output_folder = os.path.dirname(output_path)

            self.apply_button.set_processing(False)
            self.processing_bar.hide()

            CompletionDialog.success(
                self,
                "Processing complete",
                self.success_message(output_path),
                open_folder=self._open_output_folder,
            )

        except Exception as error:
            self.apply_button.set_processing(False)
            self.processing_bar.hide()
            CompletionDialog.error(self, "Processing Failed", f"Unable to process this PDF.\n\n{error}")

    def _open_output_folder(self):
        if self._last_output_folder and os.path.isdir(self._last_output_folder):
            os.startfile(self._last_output_folder)
