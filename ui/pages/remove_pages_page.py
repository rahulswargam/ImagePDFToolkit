from tools.pdf_organize import remove_pages
from ui.components.page_range_tool_page import PageRangeToolPage


class RemovePagesPage(PageRangeToolPage):

    BUTTON_LABEL = "Remove Pages"
    PROCESSING_TEXT = "Removing…"
    FIELD_LABEL = "Pages to Remove"
    PLACEHOLDER = "e.g. 2,4-6"
    NOTE_TEXT = "The listed pages are removed; everything else is kept, in order."

    def process(self, input_path, pages_zero_indexed):
        return remove_pages(input_path, pages_zero_indexed)

    def success_message(self, output_path):
        return "Pages removed successfully."
