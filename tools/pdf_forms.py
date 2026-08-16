import os

from pypdf import PdfReader, PdfWriter

from tools.image_resizer import get_output_folder


def get_form_fields(input_path):
    """
    Reads the fillable fields from a PDF's AcroForm.

    Returns:
        list of {"name", "type", "value"} dicts — type is "text" or "checkbox".
        Choice/radio/signature fields are skipped (unsupported by this tool).
    """

    reader = PdfReader(str(input_path))
    fields = reader.get_fields()

    if not fields:
        raise ValueError("This PDF has no fillable form fields.")

    result = []
    for name, field in fields.items():
        field_type = field.field_type

        if field_type == "/Tx":
            result.append({"name": name, "type": "text", "value": str(field.value or "")})
        elif field_type == "/Btn":
            result.append({"name": name, "type": "checkbox", "value": bool(field.value and field.value != "/Off")})

    if not result:
        raise ValueError("This PDF's form fields aren't a supported type (text or checkbox).")

    return result


def fill_form(input_path, values):
    """
    Fills a PDF's form fields with the given {name: value} map (str for text
    fields, bool for checkboxes) and saves a new copy.

    Returns:
        output_path
    """

    input_path = str(input_path)
    reader = PdfReader(input_path)
    writer = PdfWriter()
    writer.append(reader)

    field_values = {}
    for name, value in values.items():
        field_values[name] = "/Yes" if value is True else ("/Off" if value is False else str(value))

    for page in writer.pages:
        writer.update_page_form_field_values(page, field_values, auto_regenerate=False)

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_folder = get_output_folder()
    output_path = os.path.join(output_folder, f"{base_name}_filled.pdf")
    counter = 1
    while os.path.exists(output_path):
        output_path = os.path.join(output_folder, f"{base_name}_filled_{counter}.pdf")
        counter += 1

    with open(output_path, "wb") as output_file:
        writer.write(output_file)

    return output_path
