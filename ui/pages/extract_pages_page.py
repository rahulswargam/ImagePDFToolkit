from tools.pdf_organize import extract_pages
from ui.components.page_range_tool_page import PageRangeToolPage


class ExtractPagesPage(PageRangeToolPage):

    BUTTON_LABEL = "Extract Pages"
    PROCESSING_TEXT = "Extracting…"
    FIELD_LABEL = "Pages to Extract"
    PLACEHOLDER = "e.g. 1,3,5-8"
    NOTE_TEXT = "Only the listed pages are kept, as a new PDF, in the order you list them."

    def process(self, input_path, pages_zero_indexed):
        return extract_pages(input_path, pages_zero_indexed)

    def success_message(self, output_path):
        return "Pages extracted successfully."
