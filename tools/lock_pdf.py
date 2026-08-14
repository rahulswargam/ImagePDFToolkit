import os

from pypdf import PdfReader, PdfWriter

from tools.image_resizer import get_output_folder


def lock_pdf(input_path, password):
    """
    Add password protection to a PDF and save a new copy.

    Returns:
        output_path
    """

    if not password:
        raise ValueError("Please enter a password.")

    input_path = str(input_path)

    reader = PdfReader(input_path)

    if reader.is_encrypted:
        raise ValueError("This PDF is already password protected.")

    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(password)

    output_folder = get_output_folder()

    base_name = os.path.splitext(os.path.basename(input_path))[0]

    output_path = os.path.join(output_folder, f"{base_name}_locked.pdf")

    counter = 1
    while os.path.exists(output_path):
        output_path = os.path.join(output_folder, f"{base_name}_locked_{counter}.pdf")
        counter += 1

    with open(output_path, "wb") as output_file:
        writer.write(output_file)

    return output_path
