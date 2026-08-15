import os

from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from tools.jpg_to_pdf import convert_images_to_pdf
from ui.widgets import (
    MAX_BATCH_FILES,
    AnimatedButton,
    DropArea,
    FileListWidget,
    clip_to_max_files,
)

EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


class JpgToPdfPage(QWidget):

    def __init__(self, notify, parent=None):
        super().__init__(parent)

        self.notify = notify
        self.input_paths = []

        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 15, 0, 0)
        main_layout.setSpacing(15)

        file_card = QFrame()
        file_card.setObjectName("toolCard")

        file_layout = QHBoxLayout(file_card)
        file_layout.setContentsMargins(20, 20, 20, 20)
        file_layout.setSpacing(20)

        self.drop_area = DropArea(
            EXTENSIONS,
            multiple=True,
            placeholder=f"Drag & drop up to {MAX_BATCH_FILES} images here\n(order = page order)",
        )
        self.drop_area.setFixedSize(280, 210)
        self.drop_area.filesDropped.connect(self.load_images)

        file_layout.addWidget(self.drop_area)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(10)

        select_button = AnimatedButton("Select Images")
        select_button.setObjectName("toolButton")
        select_button.clicked.connect(self.select_images)

        self.files_label = QLabel("No images selected")
        self.files_label.setObjectName("toolDescription")
        self.files_label.setWordWrap(True)

        self.output_folder_label = QLabel("Output: Desktop\\Image & PDF Toolkit")
        self.output_folder_label.setObjectName("toolDescription")
        self.output_folder_label.setWordWrap(True)

        info_layout.addWidget(select_button)
        info_layout.addWidget(self.files_label)
        info_layout.addStretch()
        info_layout.addWidget(self.output_folder_label)

        file_layout.addLayout(info_layout)

        main_layout.addWidget(file_card)

        self.file_list = FileListWidget(icon_glyph="🖼")
        main_layout.addWidget(self.file_list)

        convert_button = AnimatedButton("Convert to PDF")
        convert_button.setObjectName("toolButton")
        convert_button.setMinimumHeight(45)
        convert_button.clicked.connect(self.convert)

        main_layout.addWidget(convert_button)
        main_layout.addStretch()

        self.file_list.filesChanged.connect(self.on_files_changed)

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
        self.file_list.set_files(file_paths)
        self.refresh_summary()

        if truncated:
            QMessageBox.warning(
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
            self.files_label.setText("No images selected")
            self.drop_area.reset()
            return

        plural = "image" if len(file_paths) == 1 else "images"
        self.files_label.setText(f"{len(file_paths)} {plural} selected — order = page order")
        self.drop_area.setText(f"{len(file_paths)} {plural} ready")

    def convert(self):

        if not self.input_paths:
            QMessageBox.warning(self, "No Images", "Please select at least one image.")
            return

        try:
            output_name = os.path.splitext(os.path.basename(self.input_paths[0]))[0]
            output_path = convert_images_to_pdf(self.input_paths, output_name)
            self.notify(f"Saved to {output_path}")

        except Exception as error:
            QMessageBox.critical(self, "Error", f"Could not create PDF.\n\n{error}")
