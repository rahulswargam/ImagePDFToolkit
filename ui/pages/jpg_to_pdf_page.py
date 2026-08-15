import os

from PySide6.QtWidgets import QApplication, QFileDialog, QLabel, QVBoxLayout, QWidget

import activity_store
from tools.image_resizer import format_file_size, get_image_size
from tools.jpg_to_pdf import convert_images_to_pdf
from ui.components.buttons import AnimatedButton, ProcessingBar
from ui.components.feedback import CompletionDialog
from ui.components.workspace import MAX_BATCH_FILES, DropWorkspace, FileGrid, clip_to_max_files

EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")
_ACCENT = "#ef4444"


class JpgToPdfPage(QWidget):

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
            title="Drop images here",
            subtitle=f"Drag & drop up to {MAX_BATCH_FILES} images — order becomes page order",
            hint="JPG · PNG · BMP · WEBP",
        )
        self.drop_workspace.filesDropped.connect(self.load_images)
        self.drop_workspace.browseRequested.connect(self.select_images)
        main_layout.addWidget(self.drop_workspace)

        self.summary_label = QLabel("")
        self.summary_label.setObjectName("pageSubtitle")
        self.summary_label.hide()
        main_layout.addWidget(self.summary_label)

        self.file_grid = FileGrid(lambda path: "image", self._image_meta)
        self.file_grid.filesChanged.connect(self.on_files_changed)
        main_layout.addWidget(self.file_grid)

        self.convert_button = AnimatedButton("Convert to PDF")
        self.convert_button.setObjectName("toolButton")
        self.convert_button.setMinimumHeight(45)
        self.convert_button.setEnabled(False)
        self.convert_button.clicked.connect(self.convert)
        main_layout.addWidget(self.convert_button)

        self.processing_bar = ProcessingBar()
        main_layout.addWidget(self.processing_bar)

        main_layout.addStretch()

    def _image_meta(self, path):
        try:
            size_text = format_file_size(os.path.getsize(path))
            width, height = get_image_size(path)
            return f"{size_text} · {width}×{height}"
        except Exception:
            return ""

    def select_images(self):

        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Images",
            "",
            "Images (*.jpg *.jpeg *.png *.bmp *.webp)",
        )

        if file_paths:
            self.load_images(file_paths)

    def load_images(self, file_paths):

        file_paths, truncated = clip_to_max_files(list(self.input_paths) + list(file_paths))

        self.input_paths = file_paths
        self.file_grid.set_files(file_paths)
        self.refresh_summary()

        if truncated:
            CompletionDialog.warn(
                self,
                "Too Many Images",
                f"Only the first {MAX_BATCH_FILES} images were kept "
                f"({truncated} extra image(s) were not added).",
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
                "Drop images here",
                f"Drag & drop up to {MAX_BATCH_FILES} images — order becomes page order",
            )
            return

        plural = "image" if len(file_paths) == 1 else "images"
        self.summary_label.setText(f"{len(file_paths)} {plural} selected — order = page order")
        self.summary_label.show()

        self.convert_button.setEnabled(True)
        self.drop_workspace.set_text(f"{len(file_paths)} {plural} ready", "Drop more images or click to add")

    def convert(self):

        if not self.input_paths:
            return

        self.convert_button.set_processing(True, "Converting…")
        self.processing_bar.show()
        QApplication.processEvents()

        try:
            output_name = os.path.splitext(os.path.basename(self.input_paths[0]))[0]
            output_path = convert_images_to_pdf(self.input_paths, output_name)
            self._last_output_path = output_path

            activity_store.record(
                "jpg_to_pdf",
                os.path.basename(output_path),
                f"Combined {len(self.input_paths)} image(s) into a PDF",
            )

            self.convert_button.set_processing(False)
            self.processing_bar.hide()

            count = len(self.input_paths)
            plural = "image" if count == 1 else "images"
            CompletionDialog.success(
                self,
                "Processing complete",
                f"{count} {plural} converted into a PDF.",
                open_folder=self._open_output_folder,
            )
            return

        except Exception as error:
            self.convert_button.set_processing(False)
            self.processing_bar.hide()
            CompletionDialog.error(self, "Processing Failed", f"Could not create the PDF.\n\n{error}")

    def _open_output_folder(self):
        if self._last_output_path and os.path.isdir(os.path.dirname(self._last_output_path)):
            os.startfile(os.path.dirname(self._last_output_path))
