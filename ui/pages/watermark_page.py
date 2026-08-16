import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFileDialog, QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from tools.pdf_edit import add_image_watermark, add_watermark
from ui.components.batch_pdf_page import BatchPdfToolPage
from ui.components.feedback import CompletionDialog
from ui.components.inputs import LabeledComboBox, LabeledLineEdit, NumberField, SegmentedControl
from ui.components.workspace import DropWorkspace

_FONTS = [
    ("Helvetica", "helv"),
    ("Helvetica Bold", "hebo"),
    ("Times Roman", "tiro"),
    ("Times Bold", "tibo"),
    ("Courier", "cour"),
]
_POSITIONS = [
    ("Center", "center"),
    ("Top left", "top-left"),
    ("Top right", "top-right"),
    ("Bottom left", "bottom-left"),
    ("Bottom right", "bottom-right"),
]
_ROTATIONS = [("0°", 0), ("45°", 45), ("-45° (315°)", 315), ("90°", 90), ("180°", 180), ("270°", 270)]
_SIZE_OPTIONS = [(f"{percent}%", percent) for percent in range(10, 101, 10)]
_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
_ACCENT = "#ef4444"


class WatermarkPage(BatchPdfToolPage):

    BUTTON_LABEL = "Add Watermark"
    PROCESSING_VERB = "Watermarking"

    def build_settings(self, layout):

        self._mode_index = 0
        self.watermark_image_path = None

        card = QFrame()
        card.setObjectName("toolCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(14)

        title = QLabel("Watermark Settings")
        title.setObjectName("toolTitle")
        card_layout.addWidget(title)

        self.mode_control = SegmentedControl(["Text Watermark", "Image Watermark"], current_index=0)
        self.mode_control.currentChanged.connect(self._on_mode_changed)
        card_layout.addWidget(self.mode_control)

        # --- Text mode ---
        self.text_widget = QWidget()
        text_layout = QVBoxLayout(self.text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(14)

        self.text_field = LabeledLineEdit("Watermark Text", "e.g. CONFIDENTIAL")
        text_layout.addWidget(self.text_field)

        self.font_field = LabeledComboBox("Font", _FONTS)
        text_layout.addWidget(self.font_field)

        card_layout.addWidget(self.text_widget)

        # --- Image mode ---
        self.image_widget = QWidget()
        image_layout = QVBoxLayout(self.image_widget)
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.setSpacing(10)

        self.image_drop = DropWorkspace(
            _IMAGE_EXTENSIONS,
            _ACCENT,
            multiple=False,
            title="Drop a logo or image",
            subtitle="PNG, JPG, or WebP — transparent PNG works best",
            hint="PNG · JPG · WEBP",
        )
        self.image_drop.setMinimumHeight(140)
        self.image_drop.filesDropped.connect(lambda paths: self._load_watermark_image(paths[0]))
        self.image_drop.browseRequested.connect(self._browse_watermark_image)
        image_layout.addWidget(self.image_drop)

        self.image_preview = QLabel()
        self.image_preview.setObjectName("fileGridThumb")
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setFixedHeight(110)
        self.image_preview.hide()
        image_layout.addWidget(self.image_preview)

        image_row = QHBoxLayout()
        image_row.setSpacing(16)

        self.position_field = LabeledComboBox("Position", _POSITIONS)
        image_row.addWidget(self.position_field, 1)

        self.rotation_field = LabeledComboBox("Rotation", _ROTATIONS)
        image_row.addWidget(self.rotation_field, 1)

        self.size_field = LabeledComboBox("Size", _SIZE_OPTIONS, current_index=4)
        image_row.addWidget(self.size_field, 1)

        image_layout.addLayout(image_row)

        self.image_widget.hide()
        card_layout.addWidget(self.image_widget)

        # --- Shared ---
        self.opacity_field = NumberField("Opacity", 5, 100, 30, suffix="%")
        card_layout.addWidget(self.opacity_field)

        layout.addWidget(card)

    def _on_mode_changed(self, index):
        self._mode_index = index
        is_image_mode = index == 1
        self.text_widget.setVisible(not is_image_mode)
        self.image_widget.setVisible(is_image_mode)

    def _browse_watermark_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Watermark Image", "", "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if file_path:
            self._load_watermark_image(file_path)

    def _load_watermark_image(self, file_path):
        self.watermark_image_path = file_path

        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                220, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            self.image_preview.setPixmap(scaled)
            self.image_preview.show()

        self.image_drop.set_text(os.path.basename(file_path), "Drop a different image or click to replace")

    def process_all(self):
        if self._mode_index == 1:
            if not self.watermark_image_path:
                CompletionDialog.warn(self, "Missing Image", "Please upload a logo or image.")
                return
        else:
            if not self.text_field.text().strip():
                CompletionDialog.warn(self, "Missing Text", "Please enter watermark text.")
                return
        super().process_all()

    def process_one(self, input_path):
        if self._mode_index == 1:
            return add_image_watermark(
                input_path,
                self.watermark_image_path,
                self.opacity_field.value(),
                self.size_field.value(),
                self.position_field.value(),
                self.rotation_field.value(),
            )
        return add_watermark(
            input_path,
            self.text_field.text(),
            self.opacity_field.value(),
            fontname=self.font_field.value(),
        )

    def success_message(self, saved, total):
        plural = "PDF" if saved == 1 else "PDFs"
        return f"{saved} {plural} watermarked successfully."
