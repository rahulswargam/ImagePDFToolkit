import os

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
from ui.widgets import MAX_BATCH_FILES, AnimatedButton, DropArea, clip_to_max_files

EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".bmp")


class ImageResizerPage(QWidget):

    def __init__(self, notify, parent=None):
        super().__init__(parent)

        self.notify = notify
        self.input_paths = []

        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 15, 0, 0)
        main_layout.setSpacing(15)

        # =========================
        # FILE SELECTION
        # =========================

        file_card = QFrame()
        file_card.setObjectName("toolCard")

        file_layout = QHBoxLayout(file_card)
        file_layout.setContentsMargins(20, 20, 20, 20)
        file_layout.setSpacing(20)

        self.drop_area = DropArea(
            EXTENSIONS,
            multiple=True,
            placeholder=f"Drag & drop up to {MAX_BATCH_FILES} images here\nor click Select Images",
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

        self.size_label = QLabel("")
        self.size_label.setObjectName("toolDescription")

        self.output_folder_label = QLabel("Output: Desktop\\Image & PDF Toolkit")
        self.output_folder_label.setObjectName("toolDescription")
        self.output_folder_label.setWordWrap(True)

        info_layout.addWidget(select_button)
        info_layout.addWidget(self.files_label)
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
            "Choose a target file size. It's applied to every selected image — "
            "quality is reduced automatically (and each image downscaled only "
            "if needed) to fit it."
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

    def select_images(self):

        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Images",
            "",
            "Images (*.jpg *.jpeg *.png *.webp *.bmp)",
        )

        if file_paths:
            self.load_images(file_paths)

    def load_images(self, file_paths):

        file_paths, truncated = clip_to_max_files(file_paths)

        self.input_paths = file_paths

        names = "\n".join(os.path.basename(path) for path in file_paths)
        self.files_label.setText(f"{len(file_paths)} image(s) selected:\n{names}")

        try:
            total_bytes = sum(os.path.getsize(path) for path in file_paths)
            self.size_label.setText(f"Total original size: {format_file_size(total_bytes)}")
        except OSError:
            self.size_label.setText("")

        self.drop_area.setText(f"{len(file_paths)} image(s) ready")

        if truncated:
            QMessageBox.warning(
                self,
                "Too Many Images",
                f"Only the first {MAX_BATCH_FILES} images were kept "
                f"({truncated} extra image(s) were not added).",
            )

    def compress_and_save(self):

        if not self.input_paths:
            QMessageBox.warning(self, "No Images", "Please select at least one image.")
            return

        target_kb = self.target_kb_spin.value()
        max_quality = self.quality_spin.value()

        saved = 0
        failed = []
        last_output_folder = None

        for input_path in self.input_paths:
            try:
                output_path, _achieved_kb, _quality_used, _width, _height = compress_to_target_size(
                    input_path,
                    target_kb,
                    max_quality,
                )
                saved += 1
                last_output_folder = os.path.dirname(output_path)

            except Exception as error:
                failed.append(f"{os.path.basename(input_path)}: {error}")

        if saved:
            plural = "image" if saved == 1 else "images"
            self.notify(f"Compressed {saved} {plural} — saved to {last_output_folder}")

        if failed:
            QMessageBox.critical(
                self,
                "Some Images Failed",
                "Could not compress:\n\n" + "\n".join(failed),
            )
