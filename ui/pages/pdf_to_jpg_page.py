import os

from PySide6.QtWidgets import QApplication, QFileDialog, QLabel, QVBoxLayout, QWidget

from tools.image_resizer import format_file_size
from tools.pdf_to_jpg import convert_pdf_to_jpg
from ui.components.buttons import AnimatedButton, ProcessingBar
from ui.components.feedback import CompletionDialog
from ui.components.workspace import MAX_BATCH_FILES, DropWorkspace, FileGrid, clip_to_max_files

EXTENSIONS = (".pdf",)
MAX_QUALITY = 100
MAX_DPI = 600
_ACCENT = "#ef4444"
_MAX_FAILURES_SHOWN = 3


class PdfToJpgPage(QWidget):

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

        note = QLabel(
            "Each PDF's pages are exported at maximum quality and resolution "
            "(600 DPI) into their own subfolder."
        )
        note.setObjectName("toolDescription")
        note.setWordWrap(True)
        main_layout.addWidget(note)

        self.convert_button = AnimatedButton("Convert to JPG")
        self.convert_button.setObjectName("toolButton")
        self.convert_button.setMinimumHeight(45)
        self.convert_button.setEnabled(False)
        self.convert_button.clicked.connect(self.convert)
        main_layout.addWidget(self.convert_button)

        self.processing_bar = ProcessingBar()
        main_layout.addWidget(self.processing_bar)

        main_layout.addStretch()

    def _pdf_meta(self, path):
        try:
            return format_file_size(os.path.getsize(path))
        except OSError:
            return ""

    def select_pdfs(self):

        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select PDFs", "", "PDF Files (*.pdf)"
        )

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
            self.convert_button.setEnabled(False)
            self.drop_workspace.set_text(
                "Drop PDFs here",
                f"Drag & drop up to {MAX_BATCH_FILES} PDFs, or click to browse",
            )
            return

        plural = "PDF" if len(file_paths) == 1 else "PDFs"
        self.summary_label.setText(f"{len(file_paths)} {plural} selected")
        self.summary_label.show()

        self.convert_button.setEnabled(True)
        self.drop_workspace.set_text(f"{len(file_paths)} {plural} ready", "Drop more PDFs or click to add")

    def convert(self):

        if not self.input_paths:
            return

        total = len(self.input_paths)
        self.convert_button.set_processing(True, "Preparing…")
        self.processing_bar.setRange(0, total)
        self.processing_bar.setValue(0)
        self.processing_bar.show()
        QApplication.processEvents()

        converted_pdfs = 0
        total_pages = 0
        failed = []
        last_output_root = None

        for index, input_path in enumerate(self.input_paths, start=1):
            plural = "PDF" if total == 1 else "PDFs"
            self.convert_button.set_processing(True, f"Converting {index} of {total} {plural}…")
            self.processing_bar.setValue(index - 1)
            QApplication.processEvents()

            try:
                output_paths = convert_pdf_to_jpg(input_path, MAX_QUALITY, MAX_DPI)
                converted_pdfs += 1
                total_pages += len(output_paths)
                last_output_root = os.path.dirname(os.path.dirname(output_paths[0]))

            except Exception as error:
                failed.append(f"{os.path.basename(input_path)}: {error}")

            self.processing_bar.setValue(index)
            QApplication.processEvents()

        self.convert_button.set_processing(False)
        self.processing_bar.hide()
        self._last_output_folder = last_output_root

        if converted_pdfs:
            page_plural = "page" if total_pages == 1 else "pages"
            CompletionDialog.success(
                self,
                "Processing complete",
                f"{total_pages} {page_plural} exported successfully.",
                open_folder=self._open_output_folder,
            )

        if failed:
            self._show_failures("Some PDFs Failed", failed)

    def _show_failures(self, title, failed):
        shown = failed[:_MAX_FAILURES_SHOWN]
        message = "\n".join(shown)
        remaining = len(failed) - len(shown)
        if remaining > 0:
            message += f"\n…and {remaining} more."
        CompletionDialog.error(self, title, message)

    def _open_output_folder(self):
        if self._last_output_folder and os.path.isdir(self._last_output_folder):
            os.startfile(self._last_output_folder)
