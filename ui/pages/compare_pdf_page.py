import os

from PySide6.QtWidgets import QApplication, QFileDialog, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from tools.pdf_security_extra import compare_pdfs
from ui.components.buttons import AnimatedButton, ProcessingBar
from ui.components.feedback import CompletionDialog
from ui.components.pdf_preview import PdfPreviewCard
from ui.components.workspace import DropWorkspace

EXTENSIONS = (".pdf",)
_ACCENT = "#ef4444"


class _SingleSlot:
    """One half of the two-up compare layout: drop zone + preview card."""

    def __init__(self, page, label, container_layout):
        self.page = page
        self.path = None
        self._preview_card = None
        self._container_layout = container_layout

        self.drop_workspace = DropWorkspace(
            EXTENSIONS,
            _ACCENT,
            multiple=False,
            title=f"Drop {label} here",
            subtitle="Drag & drop, or click to browse",
            hint="PDF",
        )
        self.drop_workspace.filesDropped.connect(lambda paths: self.load(paths[0]))
        self.drop_workspace.browseRequested.connect(self._browse)
        self.label = label

    def _browse(self):
        file_path, _ = QFileDialog.getOpenFileName(self.page, f"Select {self.label}", "", "PDF Files (*.pdf)")
        if file_path:
            self.load(file_path)

    def load(self, file_path):
        self.path = file_path

        if self._preview_card is not None:
            self._preview_card.setParent(None)
            self._preview_card.deleteLater()

        self._preview_card = PdfPreviewCard(file_path)
        self._preview_card.removed.connect(self.clear)
        self._container_layout.addWidget(self._preview_card)

        self.drop_workspace.set_text(os.path.basename(file_path), "Drop a different PDF or click to replace")
        self.page._refresh_state()

    def clear(self):
        self.path = None

        if self._preview_card is not None:
            self._preview_card.setParent(None)
            self._preview_card.deleteLater()
            self._preview_card = None

        self.drop_workspace.set_text(f"Drop {self.label} here", "Drag & drop, or click to browse")
        self.page._refresh_state()


class ComparePdfPage(QWidget):
    """Compares the text content of two PDFs, page by page, and writes a diff report."""

    def __init__(self, notify, parent=None):
        super().__init__(parent)

        self.notify = notify
        self._last_output_folder = None

        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 15, 0, 0)
        main_layout.setSpacing(16)

        columns = QHBoxLayout()
        columns.setSpacing(16)

        column_a = QVBoxLayout()
        preview_a = QVBoxLayout()
        self.slot_a = _SingleSlot(self, "PDF A", preview_a)
        column_a.addWidget(self.slot_a.drop_workspace)
        column_a.addLayout(preview_a)
        columns.addLayout(column_a, 1)

        column_b = QVBoxLayout()
        preview_b = QVBoxLayout()
        self.slot_b = _SingleSlot(self, "PDF B", preview_b)
        column_b.addWidget(self.slot_b.drop_workspace)
        column_b.addLayout(preview_b)
        columns.addLayout(column_b, 1)

        main_layout.addLayout(columns)

        note = QLabel("Compares text content page by page and saves a diff report you can open afterward.")
        note.setObjectName("toolDescription")
        note.setWordWrap(True)
        main_layout.addWidget(note)

        self.result_label = QLabel("")
        self.result_label.setObjectName("pageSubtitle")
        self.result_label.hide()
        main_layout.addWidget(self.result_label)

        self.compare_button = AnimatedButton("Compare PDFs")
        self.compare_button.setObjectName("toolButton")
        self.compare_button.setMinimumHeight(45)
        self.compare_button.setEnabled(False)
        self.compare_button.clicked.connect(self.compare)
        main_layout.addWidget(self.compare_button)

        self.processing_bar = ProcessingBar()
        main_layout.addWidget(self.processing_bar)

        main_layout.addStretch()

    def _refresh_state(self):
        self.compare_button.setEnabled(bool(self.slot_a.path and self.slot_b.path))
        self.result_label.hide()

    def compare(self):

        if not (self.slot_a.path and self.slot_b.path):
            CompletionDialog.warn(self, "Missing a PDF", "Please select both PDFs to compare.")
            return

        self.compare_button.set_processing(True, "Comparing…")
        self.processing_bar.show()
        QApplication.processEvents()

        try:
            report_path, differing, total = compare_pdfs(self.slot_a.path, self.slot_b.path)
            self._last_output_folder = os.path.dirname(report_path)

            self.compare_button.set_processing(False)
            self.processing_bar.hide()

            plural = "page" if total == 1 else "pages"
            if differing == 0:
                summary = f"No differences found across {total} {plural}."
            else:
                differ_plural = "page" if differing == 1 else "pages"
                summary = f"{differing} of {total} {plural} differ."

            self.result_label.setText(summary)
            self.result_label.show()

            CompletionDialog.success(
                self,
                "Comparison complete",
                f"{summary}\nA full report was saved.",
                open_folder=self._open_output_folder,
            )

        except Exception as error:
            self.compare_button.set_processing(False)
            self.processing_bar.hide()
            CompletionDialog.error(self, "Comparison Failed", f"Unable to compare these PDFs.\n\n{error}")

    def _open_output_folder(self):
        if self._last_output_folder and os.path.isdir(self._last_output_folder):
            os.startfile(self._last_output_folder)
