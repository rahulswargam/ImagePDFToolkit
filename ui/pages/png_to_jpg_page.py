import os

from PySide6.QtWidgets import QApplication, QFileDialog, QLabel, QVBoxLayout, QWidget

from tools.image_resizer import format_file_size, get_image_size
from tools.png_to_jpg import convert_png_to_jpg
from ui.components.buttons import AnimatedButton, ProcessingBar
from ui.components.feedback import CompletionDialog
from ui.components.workspace import DropWorkspace, FileGrid

EXTENSIONS = (".png", ".webp", ".bmp", ".gif", ".tiff")
_ACCENT = "#ef4444"


class PngToJpgPage(QWidget):

    def __init__(self, notify, parent=None):
        super().__init__(parent)

        self.notify = notify
        self.input_path = None
        self._last_output_folder = None

        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 15, 0, 0)
        main_layout.setSpacing(16)

        self.drop_workspace = DropWorkspace(
            EXTENSIONS,
            _ACCENT,
            multiple=False,
            title="Drop an image here",
            subtitle="Drag & drop an image, or click to browse",
            hint="PNG · WEBP · BMP · GIF · TIFF",
        )
        self.drop_workspace.filesDropped.connect(lambda paths: self.load_image(paths[0]))
        self.drop_workspace.browseRequested.connect(self.select_image)
        main_layout.addWidget(self.drop_workspace)

        note = QLabel("Transparent areas will be filled with white.")
        note.setObjectName("pageSubtitle")
        main_layout.addWidget(note)

        self.file_grid = FileGrid(lambda path: "image", self._image_meta)
        self.file_grid.filesChanged.connect(self._on_files_changed)
        main_layout.addWidget(self.file_grid)

        self.convert_button = AnimatedButton("Convert to JPG")
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

    def select_image(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.webp *.bmp *.gif *.tiff)",
        )

        if file_path:
            self.load_image(file_path)

    def load_image(self, file_path):
        self.input_path = file_path
        self.file_grid.set_files([file_path])
        self._refresh()

    def _on_files_changed(self, file_paths):
        self.input_path = file_paths[0] if file_paths else None
        self._refresh()

    def _refresh(self):
        if not self.input_path:
            self.convert_button.setEnabled(False)
            self.drop_workspace.set_text("Drop an image here", "Drag & drop an image, or click to browse")
            return

        self.convert_button.setEnabled(True)
        self.drop_workspace.set_text(os.path.basename(self.input_path), "Drop a different image or click to replace")

    def convert(self):

        if not self.input_path:
            return

        self.convert_button.set_processing(True, "Converting…")
        self.processing_bar.show()
        QApplication.processEvents()

        try:
            output_path = convert_png_to_jpg(self.input_path)
            self._last_output_folder = os.path.dirname(output_path)

            self.convert_button.set_processing(False)
            self.processing_bar.hide()

            CompletionDialog.success(
                self,
                "Processing complete",
                "1 image converted successfully.",
                open_folder=self._open_output_folder,
            )
            return

        except Exception as error:
            self.convert_button.set_processing(False)
            self.processing_bar.hide()
            CompletionDialog.error(self, "Processing Failed", f"Could not convert this image.\n\n{error}")

    def _open_output_folder(self):
        if self._last_output_folder and os.path.isdir(self._last_output_folder):
            os.startfile(self._last_output_folder)
