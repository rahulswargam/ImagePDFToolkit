import os

from pypdf import PdfReader, PdfWriter
from pypdf.errors import FileNotDecryptedError

from tools.image_resizer import get_output_folder


def unlock_pdf(input_path, password):
    """
    Remove password protection from a PDF and save an unprotected copy.

    Raises ValueError if the PDF isn't encrypted or the password is wrong.

    Returns:
        output_path
    """

    input_path = str(input_path)

    reader = PdfReader(input_path)

    if reader.is_encrypted:

        result = reader.decrypt(password or "")

        if result == 0:
            raise ValueError("Incorrect password.")

    else:
        raise ValueError("This PDF is not password protected.")

    writer = PdfWriter()

    try:
        for page in reader.pages:
            writer.add_page(page)
    except FileNotDecryptedError:
        raise ValueError("Incorrect password.")

    output_folder = get_output_folder()

    base_name = os.path.splitext(os.path.basename(input_path))[0]

    output_path = os.path.join(output_folder, f"{base_name}_unlocked.pdf")

    counter = 1
    while os.path.exists(output_path):
        output_path = os.path.join(output_folder, f"{base_name}_unlocked_{counter}.pdf")
        counter += 1

    with open(output_path, "wb") as output_file:
        writer.write(output_file)

    return output_path
