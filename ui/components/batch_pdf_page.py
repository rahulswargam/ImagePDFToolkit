import os

from PySide6.QtWidgets import QApplication, QFileDialog, QLabel, QVBoxLayout, QWidget

from tools.image_resizer import format_file_size
from ui.components.buttons import AnimatedButton, ProcessingBar
from ui.components.feedback import CompletionDialog
from ui.components.workspace import MAX_BATCH_FILES, DropWorkspace, FileGrid, clip_to_max_files

_MAX_FAILURES_SHOWN = 3


class BatchPdfToolPage(QWidget):
    """Base page for tools that apply the same operation independently to a
    batch of PDFs: drop zone, optional settings card, a process button with
    determinate progress, and a CompletionDialog on completion.

    Subclasses set the class-level labels/accent and override
    `build_settings(layout)` (optional — insert a settings card before the
    button) and `process_one(input_path)` (required — process a single file
    and return its output path, or raise to report a per-file failure).
    """

    ACCENT = "#ef4444"
    DROP_TITLE = "Drop PDFs here"
    DROP_SUBTITLE = f"Drag & drop up to {MAX_BATCH_FILES} PDFs, or click to browse"
    DROP_HINT = "PDF"
    BUTTON_LABEL = "Process"
    PROCESSING_VERB = "Processing"
    NOTE_TEXT = None

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
            (".pdf",),
            self.ACCENT,
            multiple=True,
            title=self.DROP_TITLE,
            subtitle=self.DROP_SUBTITLE,
            hint=self.DROP_HINT,
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

        self.build_settings(main_layout)

        if self.NOTE_TEXT:
            note = QLabel(self.NOTE_TEXT)
            note.setObjectName("toolDescription")
            note.setWordWrap(True)
            main_layout.addWidget(note)

        self.process_button = AnimatedButton(self.BUTTON_LABEL)
        self.process_button.setObjectName("toolButton")
        self.process_button.setMinimumHeight(45)
        self.process_button.setEnabled(False)
        self.process_button.clicked.connect(self.process_all)
        main_layout.addWidget(self.process_button)

        self.processing_bar = ProcessingBar()
        main_layout.addWidget(self.processing_bar)

        main_layout.addStretch()

    def build_settings(self, layout):
        """Override to insert a settings card (widgets) above the process button."""

    def process_one(self, input_path):
        """Override: process a single input path, return its output path."""
        raise NotImplementedError

    def success_message(self, saved, total):
        plural = "PDF" if saved == 1 else "PDFs"
        return f"{saved} {plural} processed successfully."

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
            self.process_button.setEnabled(False)
            self.drop_workspace.set_text(self.DROP_TITLE, self.DROP_SUBTITLE)
            return

        plural = "PDF" if len(file_paths) == 1 else "PDFs"
        self.summary_label.setText(f"{len(file_paths)} {plural} selected")
        self.summary_label.show()

        self.process_button.setEnabled(True)
        self.drop_workspace.set_text(f"{len(file_paths)} {plural} ready", "Drop more PDFs or click to add")

    def process_all(self):

        if not self.input_paths:
            return

        total = len(self.input_paths)
        self.process_button.set_processing(True, "Preparing…")
        self.processing_bar.setRange(0, total)
        self.processing_bar.setValue(0)
        self.processing_bar.show()
        QApplication.processEvents()

        saved = 0
        failed = []
        last_output_folder = None

        for index, input_path in enumerate(self.input_paths, start=1):
            self.process_button.set_processing(True, f"{self.PROCESSING_VERB} {index} of {total}…")
            self.processing_bar.setValue(index - 1)
            QApplication.processEvents()

            try:
                output_path = self.process_one(input_path)
                saved += 1
                last_output_folder = os.path.dirname(output_path)

            except Exception as error:
                failed.append(f"{os.path.basename(input_path)}: {error}")

            self.processing_bar.setValue(index)
            QApplication.processEvents()

        self.process_button.set_processing(False)
        self.processing_bar.hide()
        self._last_output_folder = last_output_folder

        if saved:
            CompletionDialog.success(
                self,
                "Processing complete",
                self.success_message(saved, total),
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
