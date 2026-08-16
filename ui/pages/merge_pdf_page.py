import os

from PySide6.QtWidgets import QApplication, QFileDialog, QLabel, QVBoxLayout, QWidget

from tools.image_resizer import format_file_size
from tools.pdf_organize import merge_pdfs
from ui.components.buttons import AnimatedButton, ProcessingBar
from ui.components.feedback import CompletionDialog
from ui.components.workspace import MAX_BATCH_FILES, DropWorkspace, FileGrid, clip_to_max_files

EXTENSIONS = (".pdf",)
_ACCENT = "#ef4444"


class MergePdfPage(QWidget):

    def __init__(self, notify, parent=None):
        super().__init__(parent)

        self.notify = notify
        self.input_paths = []
        self._last_output_folder = None

        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 15, 0, 0)
        main_layout.setSpacing(16)

        self.drop_workspace = DropWorkspace(
            EXTENSIONS,
            _ACCENT,
            multiple=True,
            title="Drop PDFs here",
            subtitle=f"Drag & drop up to {MAX_BATCH_FILES} PDFs, or click to browse",
            hint="PDF",
        )
        self.drop_workspace.filesDropped.connect(self.load_pdfs)
        self.drop_workspace.browseRequested.connect(self.select_pdfs)
        main_layout.addWidget(self.drop_workspace)

        self.summary_label = QLabel("")
        self.summary_label.setObjectName("pageSubtitle")
        self.summary_label.hide()
        main_layout.addWidget(self.summary_label)

        self.file_grid = FileGrid(lambda path: "pdf", self._pdf_meta)
        self.file_grid.filesChanged.connect(self.on_files_changed)
        main_layout.addWidget(self.file_grid)

        note = QLabel("PDFs are merged in the order shown above. Remove and re-add a file to move it.")
        note.setObjectName("toolDescription")
        note.setWordWrap(True)
        main_layout.addWidget(note)

        self.merge_button = AnimatedButton("Merge PDFs")
        self.merge_button.setObjectName("toolButton")
        self.merge_button.setMinimumHeight(45)
        self.merge_button.setEnabled(False)
        self.merge_button.clicked.connect(self.merge)
        main_layout.addWidget(self.merge_button)

        self.processing_bar = ProcessingBar()
        main_layout.addWidget(self.processing_bar)

        main_layout.addStretch()

    def _pdf_meta(self, path):
        try:
            return format_file_size(os.path.getsize(path))
        except OSError:
            return ""

    def select_pdfs(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select PDFs", "", "PDF Files (*.pdf)")
        if file_paths:
            self.load_pdfs(file_paths)

    def load_pdfs(self, file_paths):

        file_paths, truncated = clip_to_max_files(list(self.input_paths) + list(file_paths))

        self.input_paths = file_paths
        self.file_grid.set_files(file_paths)
        self.refresh_summary()

        if truncated:
            CompletionDialog.warn(
                self,
                "Too Many PDFs",
                f"Only the first {MAX_BATCH_FILES} PDFs were kept "
                f"({truncated} extra file(s) were not added).",
            )

    def on_files_changed(self, file_paths):
        self.input_paths = file_paths
        self.refresh_summary()

    def refresh_summary(self):

        file_paths = self.input_paths

        if not file_paths:
            self.summary_label.hide()
            self.merge_button.setEnabled(False)
            self.drop_workspace.set_text(
                "Drop PDFs here", f"Drag & drop up to {MAX_BATCH_FILES} PDFs, or click to browse"
            )
            return

        plural = "PDF" if len(file_paths) == 1 else "PDFs"
        self.summary_label.setText(f"{len(file_paths)} {plural} selected")
        self.summary_label.show()

        self.merge_button.setEnabled(len(file_paths) >= 2)
        self.drop_workspace.set_text(f"{len(file_paths)} {plural} ready", "Drop more PDFs or click to add")

    def merge(self):

        if len(self.input_paths) < 2:
            CompletionDialog.warn(self, "Not Enough PDFs", "Select at least 2 PDFs to merge.")
            return

        self.merge_button.set_processing(True, "Merging…")
        self.processing_bar.show()
        QApplication.processEvents()

        try:
            output_path = merge_pdfs(self.input_paths)
            self._last_output_folder = os.path.dirname(output_path)

            self.merge_button.set_processing(False)
            self.processing_bar.hide()

            CompletionDialog.success(
                self,
                "Processing complete",
                f"{len(self.input_paths)} PDFs merged into one document.",
                open_folder=self._open_output_folder,
            )

        except Exception as error:
            self.merge_button.set_processing(False)
            self.processing_bar.hide()
            CompletionDialog.error(self, "Processing Failed", f"Unable to merge these PDFs.\n\n{error}")

    def _open_output_folder(self):
        if self._last_output_folder and os.path.isdir(self._last_output_folder):
            os.startfile(self._last_output_folder)
