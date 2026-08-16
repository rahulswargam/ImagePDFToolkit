from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from tools.pdf_edit import crop_pdf
from ui.components.batch_pdf_page import BatchPdfToolPage
from ui.components.inputs import NumberField


class CropPdfPage(BatchPdfToolPage):

    BUTTON_LABEL = "Crop PDFs"
    PROCESSING_VERB = "Cropping"
    NOTE_TEXT = "Crops every page inward by the same margin on all four sides."

    def build_settings(self, layout):

        card = QFrame()
        card.setObjectName("toolCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(14)

        title = QLabel("Crop Settings")
        title.setObjectName("toolTitle")
        card_layout.addWidget(title)

        self.margin_field = NumberField("Margin", 0, 300, 36, suffix="pt")
        card_layout.addWidget(self.margin_field)

        layout.addWidget(card)

    def process_one(self, input_path):
        return crop_pdf(input_path, self.margin_field.value())

    def success_message(self, saved, total):
        plural = "PDF" if saved == 1 else "PDFs"
        return f"{saved} {plural} cropped successfully."
