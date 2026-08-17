import logging
import os

from pdf2docx import Converter

from tools.image_resizer import get_output_folder

logging.getLogger("pdf2docx").setLevel(logging.WARNING)


def _unique_docx_path(output_folder, base_name, suffix):
    output_path = os.path.join(output_folder, f"{base_name}{suffix}.docx")
    counter = 1
    while os.path.exists(output_path):
        output_path = os.path.join(output_folder, f"{base_name}{suffix}_{counter}.docx")
        counter += 1
    return output_path


def convert_pdf_to_word(input_path):
    """
    Convert a PDF into an editable Word document, reconstructing text,
    tables, and images page by page.

    Returns:
        output_path
    """

    input_path = str(input_path)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = _unique_docx_path(get_output_folder(), base_name, "")

    converter = Converter(input_path)
    try:
        converter.convert(output_path)
    finally:
        converter.close()

    return output_path
