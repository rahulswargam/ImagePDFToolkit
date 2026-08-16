import os

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFileDialog, QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from tools.pdf_edit import DEFAULT_WATERMARK_FONT, WATERMARK_FONTS, add_image_watermark, add_watermark
from ui.components.batch_pdf_page import BatchPdfToolPage
from ui.components.feedback import CompletionDialog
from ui.components.inputs import LabeledComboBox, LabeledLineEdit, NumberField, SegmentedControl
from ui.components.pdf_overlay_canvas import PdfOverlayCanvas
from ui.components.pdf_preview import render_pdf_page_thumbnail
from ui.components.workspace import DropWorkspace
from ui.font_registry import qt_family_for

_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
_ACCENT = "#ef4444"
_FONT_OPTIONS = [(spec["label"], key) for key, spec in WATERMARK_FONTS.items()]
_DEFAULT_FONT_INDEX = [key for _, key in _FONT_OPTIONS].index(DEFAULT_WATERMARK_FONT)
_CANVAS_PREVIEW_SIZE = 340


class WatermarkPage(BatchPdfToolPage):

    BUTTON_LABEL = "Add Watermark"
    PROCESSING_VERB = "Watermarking"
    NOTE_TEXT = (
        "Drag the box on the preview to position the watermark, drag a corner to resize it, "
        "and drag the handle above it to rotate — or type an exact angle below."
    )

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
        self.text_field.edit.textChanged.connect(self._update_canvas_overlay)
        text_layout.addWidget(self.text_field)

        self.font_field = LabeledComboBox("Font", _FONT_OPTIONS, current_index=_DEFAULT_FONT_INDEX)
        self.font_field.combo.currentIndexChanged.connect(self._update_canvas_overlay)
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

        self.image_widget.hide()
        card_layout.addWidget(self.image_widget)

        # --- Shared ---
        row = QHBoxLayout()
        row.setSpacing(16)

        self.rotation_field = NumberField("Rotation", 0, 359, 0, suffix="°")
        self.rotation_field.valueChanged.connect(self._on_rotation_field_changed)
        row.addWidget(self.rotation_field, 1)

        self.size_field = NumberField("Size", 5, 100, 40, suffix="%")
        self.size_field.valueChanged.connect(self._on_size_field_changed)
        row.addWidget(self.size_field, 1)

        self.opacity_field = NumberField("Opacity", 5, 100, 30, suffix="%")
        row.addWidget(self.opacity_field, 1)

        card_layout.addLayout(row)

        preview_label = QLabel("Drag to position, drag a corner to resize, drag the handle to rotate")
        preview_label.setObjectName("fieldLabel")
        card_layout.addWidget(preview_label)

        self.canvas = PdfOverlayCanvas()
        self.canvas.set_rotation_enabled(True)
        self.canvas.geometryChanged.connect(self._on_canvas_geometry_changed)
        self.canvas.rotationChanged.connect(self._on_canvas_rotation_changed)
        card_layout.addWidget(self.canvas)

        layout.addWidget(card)

        self._update_canvas_overlay()

    def _on_mode_changed(self, index):
        self._mode_index = index
        is_image_mode = index == 1
        self.text_widget.setVisible(not is_image_mode)
        self.image_widget.setVisible(is_image_mode)
        self._update_canvas_overlay()

    def _browse_watermark_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Watermark Image", "", "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if file_path:
            self._load_watermark_image(file_path)

    def _load_watermark_image(self, file_path):
        self.watermark_image_path = file_path
        self.image_drop.set_text(os.path.basename(file_path), "Drop a different image or click to replace")
        self._update_canvas_overlay()

    def _update_canvas_overlay(self):
        if self._mode_index == 1:
            if self.watermark_image_path:
                pixmap = QPixmap(self.watermark_image_path)
                if not pixmap.isNull():
                    self.canvas.set_overlay_image(pixmap)
        else:
            font_key = self.font_field.value()
            family = qt_family_for(WATERMARK_FONTS[font_key]["file"])
            self.canvas.set_overlay_text(self.text_field.text() or "WATERMARK", font_family=family)

    def _on_size_field_changed(self, value):
        self.canvas.set_width_fraction(value / 100)

    def _on_canvas_geometry_changed(self, x, y, w, h):
        self.size_field.spin.blockSignals(True)
        self.size_field.setValue(round(w * 100))
        self.size_field.spin.blockSignals(False)

    def _on_rotation_field_changed(self, value):
        self.canvas.set_rotation(value)

    def _on_canvas_rotation_changed(self, degrees):
        self.rotation_field.spin.blockSignals(True)
        self.rotation_field.setValue(round(degrees))
        self.rotation_field.spin.blockSignals(False)

    def refresh_summary(self):
        super().refresh_summary()
        self._refresh_canvas_page()

    def _refresh_canvas_page(self):
        if not self.input_paths:
            self.canvas.set_page_pixmap(None)
            return

        pixmap = render_pdf_page_thumbnail(self.input_paths[0], 0, max_size=_CANVAS_PREVIEW_SIZE)
        self.canvas.set_page_pixmap(pixmap)

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
        x, y, w, h = self.canvas.box()
        rotation = self.canvas.rotation()
        if self._mode_index == 1:
            return add_image_watermark(
                input_path,
                self.watermark_image_path,
                self.opacity_field.value(),
                x * 100,
                y * 100,
                w * 100,
                rotation,
            )
        return add_watermark(
            input_path,
            self.text_field.text(),
            self.opacity_field.value(),
            font_key=self.font_field.value(),
            x_percent=x * 100,
            y_percent=y * 100,
            width_percent=w * 100,
            height_percent=h * 100,
            rotation_degrees=rotation,
        )

    def success_message(self, saved, total):
        plural = "PDF" if saved == 1 else "PDFs"
        return f"{saved} {plural} watermarked successfully."
