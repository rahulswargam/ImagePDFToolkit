import os

from xhtml2pdf import pisa

from tools.image_resizer import get_output_folder


def _unique_pdf_path(output_folder, base_name, suffix):
    output_path = os.path.join(output_folder, f"{base_name}{suffix}.pdf")
    counter = 1
    while os.path.exists(output_path):
        output_path = os.path.join(output_folder, f"{base_name}{suffix}_{counter}.pdf")
        counter += 1
    return output_path


def _resolve_local_resource(base_dir):
    def link_callback(uri, _rel):
        if uri.startswith(("http://", "https://", "data:")):
            return uri
        local_path = os.path.join(base_dir, uri.lstrip("/\\"))
        return local_path if os.path.isfile(local_path) else uri

    return link_callback


def convert_html_to_pdf(input_path):
    """
    Convert an HTML file into a PDF using xhtml2pdf (pure Python, no system
    dependencies). Relative links to local stylesheets/images next to the
    source file are resolved. CSS support is basic — modern layout (flexbox,
    grid) and JavaScript are not rendered.

    Returns:
        output_path
    """

    input_path = str(input_path)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = _unique_pdf_path(get_output_folder(), base_name, "")
    base_dir = os.path.dirname(os.path.abspath(input_path))

    with open(input_path, "r", encoding="utf-8", errors="replace") as html_file:
        html_source = html_file.read()

    with open(output_path, "wb") as output_file:
        result = pisa.CreatePDF(
            html_source,
            dest=output_file,
            link_callback=_resolve_local_resource(base_dir),
        )

    if result.err:
        raise ValueError("This HTML file could not be converted to PDF.")

    return output_path
