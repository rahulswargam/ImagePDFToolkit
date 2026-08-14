import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from tools.image_resizer import compress_to_target_size, format_file_size, get_image_size
from ui.widgets import AnimatedButton, DropArea

EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".bmp")


class ImageResizerPage(QWidget):

    def __init__(self, notify, parent=None):
        super().__init__(parent)

        self.notify = notify
        self.input_path = None

        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 15, 0, 0)
        main_layout.setSpacing(15)

        # =========================
        # FILE / PREVIEW AREA
        # =========================

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

        self.size_label = QLabel("Original file size: --")
        self.size_label.setObjectName("toolDescription")

        self.output_folder_label = QLabel("Output: Desktop\\Image & PDF Toolkit")
        self.output_folder_label.setObjectName("toolDescription")
        self.output_folder_label.setWordWrap(True)

        info_layout.addWidget(select_button)
        info_layout.addWidget(self.file_label)
        info_layout.addWidget(self.size_label)
        info_layout.addStretch()
        info_layout.addWidget(self.output_folder_label)

        file_layout.addLayout(info_layout)

        main_layout.addWidget(file_card)

        # =========================
        # COMPRESSION SETTINGS
        # =========================

        settings_card = QFrame()
        settings_card.setObjectName("toolCard")

        settings_layout = QVBoxLayout(settings_card)
        settings_layout.setContentsMargins(20, 18, 20, 18)
        settings_layout.setSpacing(14)

        settings_title = QLabel("Compression Settings")
        settings_title.setObjectName("toolTitle")
        settings_layout.addWidget(settings_title)

        description = QLabel(
            "Choose a target file size. Quality is reduced automatically "
            "(and the image is downscaled only if needed) to fit it."
        )
        description.setObjectName("toolDescription")
        description.setWordWrap(True)
        settings_layout.addWidget(description)

        options_layout = QHBoxLayout()
        options_layout.setSpacing(16)

        target_layout = QVBoxLayout()
        target_layout.setSpacing(6)
        target_label = QLabel("Target Size")
        target_label.setObjectName("fieldLabel")
        self.target_kb_spin = QSpinBox()
        self.target_kb_spin.setMinimumHeight(40)
        self.target_kb_spin.setRange(5, 51200)
        self.target_kb_spin.setValue(200)
        self.target_kb_spin.setSuffix(" KB")
        target_layout.addWidget(target_label)
        target_layout.addWidget(self.target_kb_spin)

        quality_layout = QVBoxLayout()
        quality_layout.setSpacing(6)
        quality_label = QLabel("Maximum JPG Quality")
        quality_label.setObjectName("fieldLabel")
        self.quality_spin = QSpinBox()
        self.quality_spin.setMinimumHeight(40)
        self.quality_spin.setRange(5, 100)
        self.quality_spin.setValue(90)
        self.quality_spin.setSuffix("%")
        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.quality_spin)

        options_layout.addLayout(target_layout)
        options_layout.addLayout(quality_layout)
        settings_layout.addLayout(options_layout)

        main_layout.addWidget(settings_card)

        # =========================
        # COMPRESS BUTTON
        # =========================

        compress_button = AnimatedButton("Compress and Save")
        compress_button.setObjectName("toolButton")
        compress_button.setMinimumHeight(45)
        compress_button.clicked.connect(self.compress_and_save)

        main_layout.addWidget(compress_button)
        main_layout.addStretch()

    def select_image(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.jpg *.jpeg *.png *.webp *.bmp)",
        )

        if file_path:
            self.load_image(file_path)

    def load_image(self, file_path):

        try:
            width, height = get_image_size(file_path)
            file_size = format_file_size(os.path.getsize(file_path))

            self.input_path = file_path

            self.file_label.setText(os.path.basename(file_path))
            self.size_label.setText(f"Original file size: {file_size} ({width} × {height} px)")

            self.show_preview(file_path)

        except Exception as error:
            QMessageBox.critical(self, "Error", f"Could not open image.\n\n{error}")

    def show_preview(self, file_path):

        pixmap = QPixmap(file_path)

        if pixmap.isNull():
            return

        scaled = pixmap.scaled(
            self.preview.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.preview.setPixmap(scaled)

    def compress_and_save(self):

        if not self.input_path:
            QMessageBox.warning(self, "No Image", "Please select an image first.")
            return

        target_kb = self.target_kb_spin.value()
        max_quality = self.quality_spin.value()

        try:
            output_path, achieved_kb, quality_used, width, height = compress_to_target_size(
                self.input_path,
                target_kb,
                max_quality,
            )

            self.notify(
                f"Saved {achieved_kb:.0f} KB ({width} × {height} px, quality {quality_used}) "
                f"to {output_path}"
            )

        except Exception as error:
            QMessageBox.critical(self, "Error", f"Could not compress image.\n\n{error}")
