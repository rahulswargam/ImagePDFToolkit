import os

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFileDialog, QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from tools.pdf_organize import get_page_count
from tools.pdf_security_extra import DEFAULT_SIGNATURE_FONT, SIGNATURE_FONTS, sign_pdf, sign_pdf_with_image
from ui.components.batch_pdf_page import BatchPdfToolPage
from ui.components.feedback import CompletionDialog
from ui.components.inputs import LabeledComboBox, LabeledLineEdit, NumberField, SegmentedControl
from ui.components.pdf_overlay_canvas import PdfOverlayCanvas
from ui.components.pdf_preview import render_pdf_page_thumbnail
from ui.components.workspace import DropWorkspace
from ui.font_registry import qt_family_for

_PAGE_TARGETS = [("Last page", "last"), ("First page", "first"), ("Every page", "all")]
_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
_ACCENT = "#ef4444"
_FONT_OPTIONS = [(spec["label"], key) for key, spec in SIGNATURE_FONTS.items()]
_DEFAULT_FONT_INDEX = [key for _, key in _FONT_OPTIONS].index(DEFAULT_SIGNATURE_FONT)
_CANVAS_PREVIEW_SIZE = 340


class SignPdfPage(BatchPdfToolPage):

    BUTTON_LABEL = "Sign PDFs"
    PROCESSING_VERB = "Signing"
    NOTE_TEXT = (
        "Drag the box on the preview to position your signature, and drag a corner to resize it — "
        "a visual mark, not a legally-binding cryptographic digital signature."
    )

    def build_settings(self, layout):

        self._mode_index = 0
        self.signature_image_path = None

        card = QFrame()
        card.setObjectName("toolCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(14)

        title = QLabel("Signature")
        title.setObjectName("toolTitle")
        card_layout.addWidget(title)

        self.mode_control = SegmentedControl(["Type Signature", "Upload Image"], current_index=0)
        self.mode_control.currentChanged.connect(self._on_mode_changed)
        card_layout.addWidget(self.mode_control)

        self.type_widget = QWidget()
        type_layout = QVBoxLayout(self.type_widget)
        type_layout.setContentsMargins(0, 0, 0, 0)
        type_layout.setSpacing(14)

        self.name_field = LabeledLineEdit("Your Name", "e.g. Ada Lovelace")
        self.name_field.edit.textChanged.connect(self._update_canvas_overlay)
        type_layout.addWidget(self.name_field)

        self.font_field = LabeledComboBox("Signature Style", _FONT_OPTIONS, current_index=_DEFAULT_FONT_INDEX)
        self.font_field.combo.currentIndexChanged.connect(self._update_canvas_overlay)
        type_layout.addWidget(self.font_field)

        card_layout.addWidget(self.type_widget)

        self.image_widget = QWidget()
        image_layout = QVBoxLayout(self.image_widget)
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.setSpacing(10)

        self.image_drop = DropWorkspace(
            _IMAGE_EXTENSIONS,
            _ACCENT,
            multiple=False,
            title="Drop a signature image",
            subtitle="PNG, JPG, or WebP — transparent PNG works best",
            hint="PNG · JPG · WEBP",
        )
        self.image_drop.setMinimumHeight(140)
        self.image_drop.filesDropped.connect(lambda paths: self._load_signature_image(paths[0]))
        self.image_drop.browseRequested.connect(self._browse_signature_image)
        image_layout.addWidget(self.image_drop)

        self.image_widget.hide()
        card_layout.addWidget(self.image_widget)

        row = QHBoxLayout()
        row.setSpacing(16)

        self.page_field = LabeledComboBox("Apply To", _PAGE_TARGETS)
        self.page_field.combo.currentIndexChanged.connect(self._refresh_canvas_page)
        row.addWidget(self.page_field, 1)

        self.size_field = NumberField("Size", 5, 100, 35, suffix="%")
        self.size_field.valueChanged.connect(self._on_size_field_changed)
        row.addWidget(self.size_field, 1)

        card_layout.addLayout(row)

        preview_label = QLabel("Drag to position, drag a corner to resize")
        preview_label.setObjectName("fieldLabel")
        card_layout.addWidget(preview_label)

        self.canvas = PdfOverlayCanvas()
        self.canvas.geometryChanged.connect(self._on_canvas_geometry_changed)
        card_layout.addWidget(self.canvas)

        layout.addWidget(card)

        self._update_canvas_overlay()

    def _on_mode_changed(self, index):
        self._mode_index = index
        is_image_mode = index == 1
        self.type_widget.setVisible(not is_image_mode)
        self.image_widget.setVisible(is_image_mode)
        self._update_canvas_overlay()

    def _browse_signature_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Signature Image", "", "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if file_path:
            self._load_signature_image(file_path)

    def _load_signature_image(self, file_path):
        self.signature_image_path = file_path
        self.image_drop.set_text(os.path.basename(file_path), "Drop a different image or click to replace")
        self._update_canvas_overlay()

    def _update_canvas_overlay(self):
        if self._mode_index == 1:
            if self.signature_image_path:
                pixmap = QPixmap(self.signature_image_path)
                if not pixmap.isNull():
                    self.canvas.set_overlay_image(pixmap)
        else:
            font_key = self.font_field.value()
            family = qt_family_for(SIGNATURE_FONTS[font_key]["file"])
            self.canvas.set_overlay_text(self.name_field.text() or "Your Name", font_family=family)

    def _on_size_field_changed(self, value):
        self.canvas.set_width_fraction(value / 100)

    def _on_canvas_geometry_changed(self, x, y, w, h):
        self.size_field.spin.blockSignals(True)
        self.size_field.setValue(round(w * 100))
        self.size_field.spin.blockSignals(False)

    def refresh_summary(self):
        super().refresh_summary()
        self._refresh_canvas_page()

    def _refresh_canvas_page(self):
        if not self.input_paths:
            self.canvas.set_page_pixmap(None)
            return

        path = self.input_paths[0]
        try:
            page_count = get_page_count(path)
        except Exception:
            page_count = 1

        target = self.page_field.value() if hasattr(self, "page_field") else "last"
        page_index = 0 if target in ("first", "all") else max(0, page_count - 1)
        pixmap = render_pdf_page_thumbnail(path, page_index, max_size=_CANVAS_PREVIEW_SIZE)
        self.canvas.set_page_pixmap(pixmap)

    def process_all(self):
        if self._mode_index == 1:
            if not self.signature_image_path:
                CompletionDialog.warn(self, "Missing Image", "Please upload a signature image.")
                return
        else:
            if not self.name_field.text().strip():
                CompletionDialog.warn(self, "Missing Name", "Please enter a name to sign with.")
                return
        super().process_all()

    def process_one(self, input_path):
        x, y, w, h = self.canvas.box()
        if self._mode_index == 1:
            return sign_pdf_with_image(
                input_path,
                self.signature_image_path,
                self.page_field.value(),
                x * 100,
                y * 100,
                w * 100,
            )
        return sign_pdf(
            input_path,
            self.name_field.text(),
            self.page_field.value(),
            x * 100,
            y * 100,
            w * 100,
            h * 100,
            self.font_field.value(),
        )

    def success_message(self, saved, total):
        plural = "PDF" if saved == 1 else "PDFs"
        return f"{saved} {plural} signed successfully."
