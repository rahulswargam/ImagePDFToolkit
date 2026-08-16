from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from tools.pdf_edit import rotate_pdf
from ui.components.batch_pdf_page import BatchPdfToolPage
from ui.components.inputs import LabeledComboBox

_ROTATIONS = [
    ("Rotate 90° clockwise", 90),
    ("Rotate 180°", 180),
    ("Rotate 90° counter-clockwise", 270),
]


class RotatePdfPage(BatchPdfToolPage):

    BUTTON_LABEL = "Rotate PDFs"
    PROCESSING_VERB = "Rotating"

    def build_settings(self, layout):

        card = QFrame()
        card.setObjectName("toolCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(14)

        title = QLabel("Rotation")
        title.setObjectName("toolTitle")
        card_layout.addWidget(title)

        self.rotation_field = LabeledComboBox("Direction", _ROTATIONS)
        card_layout.addWidget(self.rotation_field)

        layout.addWidget(card)

    def process_one(self, input_path):
        return rotate_pdf(input_path, self.rotation_field.value())

    def success_message(self, saved, total):
        plural = "PDF" if saved == 1 else "PDFs"
        return f"{saved} {plural} rotated successfully."
