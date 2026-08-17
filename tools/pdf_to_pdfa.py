import os

import pikepdf
from pikepdf import Name

from tools.image_resizer import get_output_folder

_ASSETS_ICC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "icc")
_ICC_PATH = os.path.join(_ASSETS_ICC_DIR, "sRGB2014.icc")


def _unique_pdf_path(output_folder, base_name, suffix):
    output_path = os.path.join(output_folder, f"{base_name}{suffix}.pdf")
    counter = 1
    while os.path.exists(output_path):
        output_path = os.path.join(output_folder, f"{base_name}{suffix}_{counter}.pdf")
        counter += 1
    return output_path


def convert_pdf_to_pdfa(input_path, conformance_level="2b"):
    """
    Best-effort conversion of a PDF toward PDF/A archival format: embeds a
    standard sRGB ICC output intent and sets the pdfaid XMP metadata fields.
    This is NOT a certified-compliant PDF/A converter — there's no bundled
    validator (like veraPDF) to confirm the output actually satisfies the
    full ISO 19005 rule set, and fonts that weren't already embedded in the
    source PDF are not embedded here.

    Returns:
        output_path
    """

    input_path = str(input_path)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = _unique_pdf_path(get_output_folder(), base_name, "_pdfa")

    with pikepdf.Pdf.open(input_path) as pdf:

        with open(_ICC_PATH, "rb") as icc_file:
            icc_stream = pikepdf.Stream(pdf, icc_file.read())
        icc_stream.N = 3
        icc_stream.Alternate = Name("/DeviceRGB")

        output_intent = pdf.make_indirect(pikepdf.Dictionary(
            Type=Name.OutputIntent,
            S=Name("/GTS_PDFA1"),
            OutputConditionIdentifier="sRGB IEC61966-2.1",
            Info="sRGB IEC61966-2.1",
            DestOutputProfile=icc_stream,
        ))
        pdf.Root.OutputIntents = pdf.make_indirect(pikepdf.Array([output_intent]))

        with pdf.open_metadata() as meta:
            meta["pdfaid:part"] = conformance_level[0]
            meta["pdfaid:conformance"] = conformance_level[1].upper()

        pdf.save(output_path)

    return output_path
