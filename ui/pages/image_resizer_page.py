import os

from PySide6.QtWidgets import QApplication, QFileDialog, QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

import settings_store
from tools.image_resizer import compress_to_target_size, format_file_size, get_image_size
from ui.components.buttons import AnimatedButton, ProcessingBar
from ui.components.feedback import CompletionDialog
from ui.components.inputs import NumberField
from ui.components.workspace import MAX_BATCH_FILES, DropWorkspace, FileGrid, clip_to_max_files

EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".bmp")
_ACCENT = "#ef4444"
_MAX_FAILURES_SHOWN = 3


class ImageResizerPage(QWidget):

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

        # =========================
        # DROP WORKSPACE
        # =========================

        self.drop_workspace = DropWorkspace(
            EXTENSIONS,
            _ACCENT,
            multiple=True,
            title="Drop images here",
            subtitle=f"Drag & drop up to {MAX_BATCH_FILES} images, or click to browse",
            hint="JPG · PNG · WEBP · BMP",
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

        # =========================
        # COMPRESSION SETTINGS
        # =========================

        settings_card = QFrame()
        settings_card.setObjectName("toolCard")

        settings_layout = QVBoxLayout(settings_card)
        settings_layout.setContentsMargins(20, 18, 20, 18)
        settings_layout.setSpacing(16)

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
        options_layout.setSpacing(28)

        self.target_field = NumberField(
            "Target Size", 5, 5000, settings_store.get_default_target_kb(), suffix=" KB"
        )
        self.quality_field = NumberField(
            "Maximum JPG Quality", 5, 100, settings_store.get_default_quality(), suffix="%"
        )
        options_layout.addWidget(self.target_field)
        options_layout.addWidget(self.quality_field)
        settings_layout.addLayout(options_layout)

        main_layout.addWidget(settings_card)

        # =========================
        # ACTION
        # =========================

        self.compress_button = AnimatedButton("Compress Images")
        self.compress_button.setObjectName("toolButton")
        self.compress_button.setMinimumHeight(45)
        self.compress_button.setEnabled(False)
        self.compress_button.clicked.connect(self.compress_and_save)
        main_layout.addWidget(self.compress_button)

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
            "Images (*.jpg *.jpeg *.png *.webp *.bmp)",
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
            self.compress_button.setEnabled(False)
            self.drop_workspace.set_text(
                "Drop images here",
                f"Drag & drop up to {MAX_BATCH_FILES} images, or click to browse",
            )
            return

        plural = "image" if len(file_paths) == 1 else "images"
        total_bytes = sum(os.path.getsize(path) for path in file_paths if os.path.exists(path))
        self.summary_label.setText(f"{len(file_paths)} {plural} selected · {format_file_size(total_bytes)} total")
        self.summary_label.show()

        self.compress_button.setEnabled(True)
        self.drop_workspace.set_text(f"{len(file_paths)} {plural} ready", "Drop more images or click to add")

    def compress_and_save(self):

        if not self.input_paths:
            return

        target_kb = self.target_field.value()
        max_quality = self.quality_field.value()
        total = len(self.input_paths)

        self.compress_button.set_processing(True, "Preparing…")
        self.processing_bar.setRange(0, total)
        self.processing_bar.setValue(0)
        self.processing_bar.show()
        QApplication.processEvents()

        saved = 0
        failed = []
        last_output_folder = None
        original_total_bytes = 0
        achieved_total_bytes = 0

        for index, input_path in enumerate(self.input_paths, start=1):
            plural = "image" if total == 1 else "images"
            self.compress_button.set_processing(True, f"Compressing {index} of {total} {plural}…")
            self.processing_bar.setValue(index - 1)
            QApplication.processEvents()

            try:
                original_bytes = os.path.getsize(input_path)
                original_total_bytes += original_bytes
                output_path, achieved_kb, _quality_used, _width, _height = compress_to_target_size(
                    input_path,
                    target_kb,
                    max_quality,
                )
                achieved_bytes = achieved_kb * 1024
                achieved_total_bytes += achieved_bytes
                saved += 1
                last_output_folder = os.path.dirname(output_path)

            except Exception as error:
                failed.append(f"{os.path.basename(input_path)}: {error}")

            self.processing_bar.setValue(index)
            QApplication.processEvents()

        self.compress_button.set_processing(False)
        self.processing_bar.hide()
        self._last_output_folder = last_output_folder

        if saved:
            plural = "image" if saved == 1 else "images"
            CompletionDialog.success(
                self,
                "Processing complete",
                f"{saved} {plural} compressed successfully.",
                open_folder=self._open_output_folder,
            )

        if failed:
            self._show_failures("Some Images Failed", failed)

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
