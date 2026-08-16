from tools.pdf_optimize import repair_pdf
from ui.components.batch_pdf_page import BatchPdfToolPage


class RepairPdfPage(BatchPdfToolPage):

    BUTTON_LABEL = "Repair PDFs"
    PROCESSING_VERB = "Repairing"
    NOTE_TEXT = "Re-parses and rebuilds each PDF to fix corrupted or malformed files."

    def process_one(self, input_path):
        return repair_pdf(input_path)

    def success_message(self, saved, total):
        plural = "PDF" if saved == 1 else "PDFs"
        return f"{saved} {plural} repaired successfully."
