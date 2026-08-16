import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFileDialog, QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from tools.pdf_security_extra import sign_pdf, sign_pdf_with_image
from ui.components.batch_pdf_page import BatchPdfToolPage
from ui.components.feedback import CompletionDialog
from ui.components.inputs import LabeledComboBox, LabeledLineEdit, SegmentedControl
from ui.components.workspace import DropWorkspace

_PAGE_TARGETS = [("Last page", "last"), ("First page", "first"), ("Every page", "all")]
_POSITIONS = [("Bottom right", "bottom-right"), ("Bottom center", "bottom-center"), ("Bottom left", "bottom-left")]
_SIZE_OPTIONS = [(f"{percent}%", percent) for percent in range(10, 101, 10)]
_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
_ACCENT = "#ef4444"


class SignPdfPage(BatchPdfToolPage):

    BUTTON_LABEL = "Sign PDFs"
    PROCESSING_VERB = "Signing"
    NOTE_TEXT = (
        "Stamps a visual signature onto your PDF — a styled name or an uploaded "
        "image, not a legally-binding cryptographic digital signature."
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

        self.name_field = LabeledLineEdit("Your Name", "e.g. Ada Lovelace")
        card_layout.addWidget(self.name_field)

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

        self.image_preview = QLabel()
        self.image_preview.setObjectName("fileGridThumb")
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setFixedHeight(110)
        self.image_preview.hide()
        image_layout.addWidget(self.image_preview)

        self.image_widget.hide()
        card_layout.addWidget(self.image_widget)

        row = QHBoxLayout()
        row.setSpacing(16)

        self.page_field = LabeledComboBox("Apply To", _PAGE_TARGETS)
        row.addWidget(self.page_field, 1)

        self.position_field = LabeledComboBox("Position", _POSITIONS)
        row.addWidget(self.position_field, 1)

        self.size_field = LabeledComboBox("Size", _SIZE_OPTIONS, current_index=len(_SIZE_OPTIONS) - 1)
        row.addWidget(self.size_field, 1)

        card_layout.addLayout(row)
        layout.addWidget(card)

    def _on_mode_changed(self, index):
        self._mode_index = index
        is_image_mode = index == 1
        self.name_field.setVisible(not is_image_mode)
        self.image_widget.setVisible(is_image_mode)

    def _browse_signature_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Signature Image", "", "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if file_path:
            self._load_signature_image(file_path)

    def _load_signature_image(self, file_path):
        self.signature_image_path = file_path

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
            if not self.signature_image_path:
                CompletionDialog.warn(self, "Missing Image", "Please upload a signature image.")
                return
        else:
            if not self.name_field.text().strip():
                CompletionDialog.warn(self, "Missing Name", "Please enter a name to sign with.")
                return
        super().process_all()

    def process_one(self, input_path):
        if self._mode_index == 1:
            return sign_pdf_with_image(
                input_path,
                self.signature_image_path,
                self.page_field.value(),
                self.position_field.value(),
                self.size_field.value(),
            )
        return sign_pdf(
            input_path,
            self.name_field.text(),
            self.page_field.value(),
            self.position_field.value(),
            self.size_field.value(),
        )

    def success_message(self, saved, total):
        plural = "PDF" if saved == 1 else "PDFs"
        return f"{saved} {plural} signed successfully."
