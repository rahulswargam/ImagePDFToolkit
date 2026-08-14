import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from tools.png_to_jpg import convert_png_to_jpg
from ui.widgets import AnimatedButton, DropArea

EXTENSIONS = (".png", ".webp", ".bmp", ".gif", ".tiff")


class PngToJpgPage(QWidget):

    def __init__(self, notify, parent=None):
        super().__init__(parent)

        self.notify = notify
        self.input_path = None

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

        self.preview = DropArea(
            EXTENSIONS,
            multiple=False,
            placeholder="Drag & drop an image here\nor click Select Image",
        )
        self.preview.setFixedSize(280, 210)
        self.preview.filesDropped.connect(lambda paths: self.load_image(paths[0]))

        file_layout.addWidget(self.preview)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(10)

        select_button = AnimatedButton("Select Image")
        select_button.setObjectName("toolButton")
        select_button.clicked.connect(self.select_image)

        self.file_label = QLabel("No image selected")
        self.file_label.setObjectName("toolDescription")
        self.file_label.setWordWrap(True)

        self.output_folder_label = QLabel("Output: Desktop\\Image & PDF Toolkit")
        self.output_folder_label.setObjectName("toolDescription")
        self.output_folder_label.setWordWrap(True)

        info_layout.addWidget(select_button)
        info_layout.addWidget(self.file_label)
        info_layout.addStretch()
        info_layout.addWidget(self.output_folder_label)

        file_layout.addLayout(info_layout)

        main_layout.addWidget(file_card)

        note = QLabel("Transparent areas will be filled with white.")
        note.setObjectName("toolDescription")
        note.setWordWrap(True)
        main_layout.addWidget(note)

        convert_button = AnimatedButton("Convert to JPG")
        convert_button.setObjectName("toolButton")
        convert_button.setMinimumHeight(45)
        convert_button.clicked.connect(self.convert)

        main_layout.addWidget(convert_button)
        main_layout.addStretch()

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

        try:
            pixmap = QPixmap(file_path)

            if pixmap.isNull():
                raise ValueError("Could not read this image.")

            self.input_path = file_path
            self.file_label.setText(os.path.basename(file_path))

            scaled = pixmap.scaled(
                self.preview.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.preview.setPixmap(scaled)

        except Exception as error:
            QMessageBox.critical(self, "Error", f"Could not open image.\n\n{error}")

    def convert(self):

        if not self.input_path:
            QMessageBox.warning(self, "No Image", "Please select an image first.")
            return

        try:
            output_path = convert_png_to_jpg(self.input_path)
            self.notify(f"Saved to {output_path}")

        except Exception as error:
            QMessageBox.critical(self, "Error", f"Could not convert image.\n\n{error}")
