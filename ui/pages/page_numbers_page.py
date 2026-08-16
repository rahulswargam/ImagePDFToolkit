from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from tools.pdf_edit import add_page_numbers
from ui.components.batch_pdf_page import BatchPdfToolPage
from ui.components.inputs import LabeledComboBox, NumberField

_POSITIONS = [
    ("Bottom center", "bottom-center"),
    ("Bottom left", "bottom-left"),
    ("Bottom right", "bottom-right"),
    ("Top center", "top-center"),
    ("Top left", "top-left"),
    ("Top right", "top-right"),
]


class PageNumbersPage(BatchPdfToolPage):

    BUTTON_LABEL = "Add Page Numbers"
    PROCESSING_VERB = "Numbering"

    def build_settings(self, layout):

        card = QFrame()
        card.setObjectName("toolCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(14)

        title = QLabel("Page Number Settings")
        title.setObjectName("toolTitle")
        card_layout.addWidget(title)

        row = QHBoxLayout()
        row.setSpacing(16)

        self.position_field = LabeledComboBox("Position", _POSITIONS)
        row.addWidget(self.position_field, 1)

        self.start_field = NumberField("Start At", 1, 9999, 1)
        row.addWidget(self.start_field, 1)

        card_layout.addLayout(row)
        layout.addWidget(card)

    def process_one(self, input_path):
        return add_page_numbers(input_path, self.position_field.value(), self.start_field.value())

    def success_message(self, saved, total):
        plural = "PDF" if saved == 1 else "PDFs"
        return f"{saved} {plural} numbered successfully."
