from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from tools.pdf_security_extra import redact_pdf
from ui.components.batch_pdf_page import BatchPdfToolPage
from ui.components.feedback import CompletionDialog
from ui.components.inputs import LabeledLineEdit


class RedactPdfPage(BatchPdfToolPage):

    BUTTON_LABEL = "Redact PDFs"
    PROCESSING_VERB = "Redacting"
    NOTE_TEXT = "Every occurrence of the text below is blacked out and permanently removed — not just hidden."

    def build_settings(self, layout):

        card = QFrame()
        card.setObjectName("toolCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(14)

        title = QLabel("Redaction")
        title.setObjectName("toolTitle")
        card_layout.addWidget(title)

        self.search_field = LabeledLineEdit("Text to Redact", "e.g. Account Number: 12345")
        card_layout.addWidget(self.search_field)

        layout.addWidget(card)
        self._occurrences_total = 0

    def process_all(self):
        if not self.search_field.text().strip():
            CompletionDialog.warn(self, "Missing Text", "Please enter the text you want to redact.")
            return
        self._occurrences_total = 0
        super().process_all()

    def process_one(self, input_path):
        output_path, occurrences = redact_pdf(input_path, self.search_field.text())
        self._occurrences_total += occurrences
        return output_path

    def success_message(self, saved, total):
        plural = "PDF" if saved == 1 else "PDFs"
        occurrence_plural = "occurrence" if self._occurrences_total == 1 else "occurrences"
        return f"{saved} {plural} redacted successfully ({self._occurrences_total} {occurrence_plural} removed)."
