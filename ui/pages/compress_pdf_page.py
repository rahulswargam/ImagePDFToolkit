from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from tools.pdf_optimize import compress_pdf
from ui.components.batch_pdf_page import BatchPdfToolPage
from ui.components.inputs import NumberField


class CompressPdfPage(BatchPdfToolPage):

    BUTTON_LABEL = "Compress PDFs"
    PROCESSING_VERB = "Compressing"
    NOTE_TEXT = "Shrinks file size by recompressing embedded images. Text and layout stay crisp."

    def build_settings(self, layout):

        card = QFrame()
        card.setObjectName("toolCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(14)

        title = QLabel("Compression Settings")
        title.setObjectName("toolTitle")
        card_layout.addWidget(title)

        self.quality_field = NumberField("Image Quality", 10, 100, 60, suffix="%")
        card_layout.addWidget(self.quality_field)

        layout.addWidget(card)

        self._original_total = 0
        self._compressed_total = 0

    def process_all(self):
        self._original_total = 0
        self._compressed_total = 0
        super().process_all()

    def process_one(self, input_path):
        output_path, original_bytes, compressed_bytes = compress_pdf(input_path, self.quality_field.value())
        self._original_total += original_bytes
        self._compressed_total += compressed_bytes
        return output_path

    def success_message(self, saved, total):
        plural = "PDF" if saved == 1 else "PDFs"
        if self._original_total > 0 and self._compressed_total < self._original_total:
            percent = round((1 - self._compressed_total / self._original_total) * 100)
            return f"{saved} {plural} compressed successfully ({percent}% smaller)."
        return f"{saved} {plural} compressed successfully."
