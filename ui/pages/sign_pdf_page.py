from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from tools.pdf_security_extra import sign_pdf
from ui.components.batch_pdf_page import BatchPdfToolPage
from ui.components.feedback import CompletionDialog
from ui.components.inputs import LabeledComboBox, LabeledLineEdit

_PAGE_TARGETS = [("Last page", "last"), ("First page", "first"), ("Every page", "all")]
_POSITIONS = [("Bottom right", "bottom-right"), ("Bottom center", "bottom-center"), ("Bottom left", "bottom-left")]


class SignPdfPage(BatchPdfToolPage):

    BUTTON_LABEL = "Sign PDFs"
    PROCESSING_VERB = "Signing"
    NOTE_TEXT = (
        "Stamps a visual signature onto your PDF — a styled name, not a "
        "legally-binding cryptographic digital signature."
    )

    def build_settings(self, layout):

        card = QFrame()
        card.setObjectName("toolCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(14)

        title = QLabel("Signature")
        title.setObjectName("toolTitle")
        card_layout.addWidget(title)

        self.name_field = LabeledLineEdit("Your Name", "e.g. Ada Lovelace")
        card_layout.addWidget(self.name_field)

        row = QHBoxLayout()
        row.setSpacing(16)

        self.page_field = LabeledComboBox("Apply To", _PAGE_TARGETS)
        row.addWidget(self.page_field, 1)

        self.position_field = LabeledComboBox("Position", _POSITIONS)
        row.addWidget(self.position_field, 1)

        card_layout.addLayout(row)
        layout.addWidget(card)

    def process_all(self):
        if not self.name_field.text().strip():
            CompletionDialog.warn(self, "Missing Name", "Please enter a name to sign with.")
            return
        super().process_all()

    def process_one(self, input_path):
        return sign_pdf(input_path, self.name_field.text(), self.page_field.value(), self.position_field.value())

    def success_message(self, saved, total):
        plural = "PDF" if saved == 1 else "PDFs"
        return f"{saved} {plural} signed successfully."
