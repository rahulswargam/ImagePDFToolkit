from tools.pdf_to_pdfa import convert_pdf_to_pdfa
from ui.components.batch_pdf_page import BatchPdfToolPage

NOTE_TEXT = (
    "Best-effort PDF/A conversion for long-term archival — embeds a standard sRGB "
    "output intent and archival metadata. This is not a certified compliance tool, "
    "and fonts that aren't already embedded in the source PDF are not embedded here."
)


class PdfToPdfaPage(BatchPdfToolPage):

    BUTTON_LABEL = "Convert to PDF/A"
    PROCESSING_VERB = "Converting"
    NOTE_TEXT = NOTE_TEXT

    def process_one(self, input_path):
        return convert_pdf_to_pdfa(input_path)

    def success_message(self, saved, total):
        plural = "PDF" if saved == 1 else "PDFs"
        return f"{saved} {plural} converted to PDF/A."
