import os

from PySide6.QtWidgets import QApplication, QFileDialog, QLabel, QVBoxLayout, QWidget

from tools.image_resizer import format_file_size
from tools.office_com import is_office_app_installed
from tools.powerpoint_to_pdf import convert_powerpoint_to_pdf
from ui.components.buttons import AnimatedButton, ProcessingBar
from ui.components.feedback import CompletionDialog
from ui.components.workspace import MAX_BATCH_FILES, DropWorkspace, FileGrid, clip_to_max_files

EXTENSIONS = (".pptx", ".ppt")
_ACCENT = "#ef4444"
_MAX_FAILURES_SHOWN = 3
_FALLBACK_WARNING = (
    "Microsoft PowerPoint isn't detected on this machine — using a simplified fallback "
    "converter. It can only extract plain text, one page per slide. Images, layout, "
    "colors, and design are not preserved at all."
)


class PowerpointToPdfPage(QWidget):

    def __init__(self, notify, parent=None):
        super().__init__(parent)

        self.notify = notify
        self.input_paths = []
        self._last_output_path = None

        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 15, 0, 0)
        main_layout.setSpacing(16)

        self.drop_workspace = DropWorkspace(
            EXTENSIONS,
            _ACCENT,
            multiple=True,
            title="Drop presentations here",
            subtitle=f"Drag & drop up to {MAX_BATCH_FILES} .pptx/.ppt files, or click to browse",
            hint="PPTX · PPT",
        )
        self.drop_workspace.filesDropped.connect(self.load_files)
        self.drop_workspace.browseRequested.connect(self.select_files)
        main_layout.addWidget(self.drop_workspace)

        self.summary_label = QLabel("")
        self.summary_label.setObjectName("pageSubtitle")
        self.summary_label.hide()
        main_layout.addWidget(self.summary_label)

        self.file_grid = FileGrid(lambda path: "file", self._file_meta)
        self.file_grid.filesChanged.connect(self.on_files_changed)
        main_layout.addWidget(self.file_grid)

        self.fallback_note = QLabel(_FALLBACK_WARNING)
        self.fallback_note.setObjectName("toolDescription")
        self.fallback_note.setWordWrap(True)
        self.fallback_note.setVisible(not is_office_app_installed("powerpoint"))
        main_layout.addWidget(self.fallback_note)

        self.convert_button = AnimatedButton("Convert to PDF")
        self.convert_button.setObjectName("toolButton")
        self.convert_button.setMinimumHeight(45)
        self.convert_button.setEnabled(False)
        self.convert_button.clicked.connect(self.convert)
        main_layout.addWidget(self.convert_button)

        self.processing_bar = ProcessingBar()
        main_layout.addWidget(self.processing_bar)

        main_layout.addStretch()

    def _file_meta(self, path):
        try:
            return format_file_size(os.path.getsize(path))
        except OSError:
            return ""

    def select_files(self):

        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Presentations", "", "PowerPoint Presentations (*.pptx *.ppt)"
        )

        if file_paths:
            self.load_files(file_paths)

    def load_files(self, file_paths):

        file_paths, truncated = clip_to_max_files(list(self.input_paths) + list(file_paths))

        self.input_paths = file_paths
        self.file_grid.set_files(file_paths)
        self.refresh_summary()

        if truncated:
            CompletionDialog.warn(
                self,
                "Too Many Files",
                f"Only the first {MAX_BATCH_FILES} presentations were kept "
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
                "Drop presentations here",
                f"Drag & drop up to {MAX_BATCH_FILES} .pptx/.ppt files, or click to browse",
            )
            return

        plural = "presentation" if len(file_paths) == 1 else "presentations"
        self.summary_label.setText(f"{len(file_paths)} {plural} selected")
        self.summary_label.show()

        self.convert_button.setEnabled(True)
        self.drop_workspace.set_text(f"{len(file_paths)} {plural} ready", "Drop more presentations or click to add")

    def convert(self):

        if not self.input_paths:
            return

        total = len(self.input_paths)
        self.convert_button.set_processing(True, "Preparing…")
        self.processing_bar.setRange(0, total)
        self.processing_bar.setValue(0)
        self.processing_bar.show()
        QApplication.processEvents()

        saved = 0
        fallback_count = 0
        failed = []

        for index, input_path in enumerate(self.input_paths, start=1):
            plural = "file" if total == 1 else "files"
            self.convert_button.set_processing(True, f"Converting {index} of {total} {plural}…")
            self.processing_bar.setValue(index - 1)
            QApplication.processEvents()

            try:
                self._last_output_path, method = convert_powerpoint_to_pdf(input_path)
                saved += 1
                if method == "fallback":
                    fallback_count += 1

            except Exception as error:
                failed.append(f"{os.path.basename(input_path)}: {error}")

            self.processing_bar.setValue(index)
            QApplication.processEvents()

        self.convert_button.set_processing(False)
        self.processing_bar.hide()

        if saved:
            plural = "presentation" if saved == 1 else "presentations"
            if fallback_count:
                dialog = CompletionDialog(
                    "Processing complete",
                    f"{saved} {plural} converted, but {fallback_count} of them used the "
                    "text-only fallback converter (no images or layout) because "
                    "Microsoft PowerPoint isn't installed.",
                    kind="warning",
                    secondary_label="Open File",
                    parent=self,
                )
                dialog.set_secondary_action(self._open_output_file)
                dialog.exec()
            else:
                CompletionDialog.success(
                    self,
                    "Processing complete",
                    f"{saved} {plural} converted into PDF.",
                    open_file=self._open_output_file,
                )

        if failed:
            self._show_failures("Some Files Failed", failed)

    def _show_failures(self, title, failed):
        shown = failed[:_MAX_FAILURES_SHOWN]
        message = "\n".join(shown)
        remaining = len(failed) - len(shown)
        if remaining > 0:
            message += f"\n…and {remaining} more."
        CompletionDialog.error(self, title, message)

    def _open_output_file(self):
        if self._last_output_path and os.path.isfile(self._last_output_path):
            os.startfile(self._last_output_path)
