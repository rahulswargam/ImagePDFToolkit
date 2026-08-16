from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from tools.pdf_edit import add_watermark
from ui.components.batch_pdf_page import BatchPdfToolPage
from ui.components.feedback import CompletionDialog
from ui.components.inputs import LabeledLineEdit, NumberField


class WatermarkPage(BatchPdfToolPage):

    BUTTON_LABEL = "Add Watermark"
    PROCESSING_VERB = "Watermarking"

    def build_settings(self, layout):

        card = QFrame()
        card.setObjectName("toolCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(14)

        title = QLabel("Watermark Settings")
        title.setObjectName("toolTitle")
        card_layout.addWidget(title)

        row = QHBoxLayout()
        row.setSpacing(16)

        self.text_field = LabeledLineEdit("Watermark Text", "e.g. CONFIDENTIAL")
        row.addWidget(self.text_field, 2)

        self.opacity_field = NumberField("Opacity", 5, 100, 30, suffix="%")
        row.addWidget(self.opacity_field, 1)

        card_layout.addLayout(row)
        layout.addWidget(card)

    def process_all(self):
        if not self.text_field.text().strip():
            CompletionDialog.warn(self, "Missing Text", "Please enter watermark text.")
            return
        super().process_all()

    def process_one(self, input_path):
        return add_watermark(input_path, self.text_field.text(), self.opacity_field.value())

    def success_message(self, saved, total):
        plural = "PDF" if saved == 1 else "PDFs"
        return f"{saved} {plural} watermarked successfully."
