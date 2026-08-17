import os

import pymupdf
from PIL import Image

from tools.image_resizer import get_output_folder

_ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fonts")
_SIGNATURE_FONTS_DIR = os.path.join(_ASSETS_DIR, "signatures")

# Every entry here is a genuinely free, redistributable font (Google Fonts,
# SIL Open Font License) bundled in assets/fonts/signatures/. Several fonts
# requested alongside these — Brittany Signature, Amsterdam Four, Black
# Jack, Billion Dreams, Brittany, Playlist Script — are commercial/paid
# fonts sold on marketplaces (Creative Fabrica, Fontspring, etc.); they
# can't legally be bundled or redistributed with this app, so they're
# deliberately not included here rather than faked with a substitute.
SIGNATURE_FONTS = {
    "great_vibes": {
        "label": "Great Vibes",
        "file": os.path.join(_SIGNATURE_FONTS_DIR, "GreatVibes-Regular.ttf"),
        "fallback": "heit",
    },
    "alex_brush": {
        "label": "Alex Brush",
        "file": os.path.join(_SIGNATURE_FONTS_DIR, "AlexBrush-Regular.ttf"),
        "fallback": "heit",
    },
    "allura": {
        "label": "Allura",
        "file": os.path.join(_SIGNATURE_FONTS_DIR, "Allura-Regular.ttf"),
        "fallback": "heit",
    },
    "sacramento": {
        "label": "Sacramento",
        "file": os.path.join(_SIGNATURE_FONTS_DIR, "Sacramento-Regular.ttf"),
        "fallback": "heit",
    },
    "dancing_script": {
        "label": "Dancing Script",
        "file": os.path.join(_SIGNATURE_FONTS_DIR, "DancingScript-Regular.ttf"),
        "fallback": "heit",
    },
    "mr_dafoe": {
        "label": "Mr Dafoe",
        "file": os.path.join(_SIGNATURE_FONTS_DIR, "MrDafoe-Regular.ttf"),
        "fallback": "heit",
    },
    "satisfy": {
        "label": "Satisfy",
        "file": os.path.join(_SIGNATURE_FONTS_DIR, "Satisfy-Regular.ttf"),
        "fallback": "heit",
    },
    "pacifico": {
        "label": "Pacifico",
        "file": os.path.join(_SIGNATURE_FONTS_DIR, "Pacifico-Regular.ttf"),
        "fallback": "heit",
    },
    "yellowtail": {
        "label": "Yellowtail",
        "file": os.path.join(_SIGNATURE_FONTS_DIR, "Yellowtail-Regular.ttf"),
        "fallback": "heit",
    },
    "marck_script": {
        "label": "Marck Script",
        "file": os.path.join(_SIGNATURE_FONTS_DIR, "MarckScript-Regular.ttf"),
        "fallback": "heit",
    },
    "parisienne": {
        "label": "Parisienne",
        "file": os.path.join(_SIGNATURE_FONTS_DIR, "Parisienne-Regular.ttf"),
        "fallback": "heit",
    },
    "tangerine": {
        "label": "Tangerine",
        "file": os.path.join(_SIGNATURE_FONTS_DIR, "Tangerine-Regular.ttf"),
        "fallback": "heit",
    },
    "herr_von_muellerhoff": {
        "label": "Herr Von Muellerhoff",
        "file": os.path.join(_SIGNATURE_FONTS_DIR, "HerrVonMuellerhoff-Regular.ttf"),
        "fallback": "heit",
    },
    "rouge_script": {
        "label": "Rouge Script",
        "file": os.path.join(_SIGNATURE_FONTS_DIR, "RougeScript-Regular.ttf"),
        "fallback": "heit",
    },
    "norican": {
        "label": "Norican",
        "file": os.path.join(_SIGNATURE_FONTS_DIR, "Norican-Regular.ttf"),
        "fallback": "heit",
    },
    "meddon": {
        "label": "Meddon",
        "file": os.path.join(_SIGNATURE_FONTS_DIR, "Meddon-Regular.ttf"),
        "fallback": "heit",
    },
    "kristi": {
        "label": "Kristi",
        "file": os.path.join(_SIGNATURE_FONTS_DIR, "Kristi-Regular.ttf"),
        "fallback": "heit",
    },
}
DEFAULT_SIGNATURE_FONT = "great_vibes"


def _resolve_signature_font(font_key):
    """
    Returns (fontname, fontfile) for use with pymupdf's insert_text /
    pymupdf.Font — fontfile is an absolute path when a real font file is
    available, or None to fall back to a built-in base-14 font.
    """

    spec = SIGNATURE_FONTS.get(font_key, SIGNATURE_FONTS[DEFAULT_SIGNATURE_FONT])
    file_path = spec.get("file")

    if file_path and os.path.exists(file_path):
        return font_key, file_path

    return spec["fallback"], None


def _measure_text(text, fontname, fontfile, fontsize):
    if fontfile:
        return pymupdf.Font(fontfile=fontfile).text_length(text, fontsize=fontsize)
    return pymupdf.get_text_length(text, fontname=fontname, fontsize=fontsize)


def _unique_path(output_folder, base_name, suffix, ext):
    output_path = os.path.join(output_folder, f"{base_name}{suffix}.{ext}")
    counter = 1
    while os.path.exists(output_path):
        output_path = os.path.join(output_folder, f"{base_name}{suffix}_{counter}.{ext}")
        counter += 1
    return output_path


def _target_pages(document, page_target):
    if page_target == "first":
        return [document[0]]
    if page_target == "all":
        return list(document)
    return [document[-1]]


def _clamp_fraction(percent, minimum=0, maximum=100):
    return max(minimum, min(maximum, float(percent))) / 100


def sign_pdf(
    input_path,
    signer_name,
    page_target="last",
    x_percent=30,
    y_percent=78,
    width_percent=35,
    height_percent=10,
    font_key=DEFAULT_SIGNATURE_FONT,
):
    """
    Stamps a visual signature (name in a script/handwriting-style font, with
    a signature line) onto a PDF, at an exact position and size — matching
    a box the user dragged/resized on a page preview. This is a visual
    mark, not a legally-binding cryptographic digital signature.

    `x_percent`/`y_percent` place the box's top-left corner as a fraction
    of the page's width/height; `width_percent`/`height_percent` size it
    the same way. The signature text is sized to fit within that box
    (shrinking to whichever dimension — width or height — is tighter).
    `font_key` selects a style from SIGNATURE_FONTS.

    Returns:
        output_path
    """

    input_path = str(input_path)
    signer_name = (signer_name or "").strip()

    if not signer_name:
        raise ValueError("Please enter a name to sign with.")

    x_frac = _clamp_fraction(x_percent)
    y_frac = _clamp_fraction(y_percent)
    width_frac = _clamp_fraction(width_percent, minimum=5)
    height_frac = _clamp_fraction(height_percent, minimum=3)
    fontname, fontfile = _resolve_signature_font(font_key)

    with pymupdf.open(input_path) as document:

        for page in _target_pages(document, page_target):
            rect = page.rect
            box_x = rect.x0 + x_frac * rect.width
            box_y = rect.y0 + y_frac * rect.height
            box_width = width_frac * rect.width
            box_height = height_frac * rect.height

            reference_size = 100
            reference_width = _measure_text(signer_name, fontname, fontfile, reference_size)
            width_based_size = (box_width / reference_width * reference_size) if reference_width > 0 else 24
            # The name line + caption line together take roughly 1.5x the
            # name's own font size in vertical space.
            height_based_size = box_height / 1.5
            name_font_size = max(6, min(width_based_size, height_based_size))
            caption_font_size = max(5, name_font_size * 0.3)

            actual_text_width = _measure_text(signer_name, fontname, fontfile, name_font_size)
            line_width = actual_text_width + 6
            baseline_y = box_y + name_font_size

            page.draw_line((box_x, baseline_y), (box_x + line_width, baseline_y), color=(0.4, 0.42, 0.48), width=0.8)
            page.insert_text(
                (box_x, baseline_y - 6),
                signer_name,
                fontname=fontname,
                fontfile=fontfile,
                fontsize=name_font_size,
                color=(0.1, 0.1, 0.15),
            )
            page.insert_text(
                (box_x, baseline_y + caption_font_size + 4),
                "Signed electronically",
                fontname="helv",
                fontsize=caption_font_size,
                color=(0.5, 0.52, 0.58),
            )

        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = _unique_path(get_output_folder(), base_name, "_signed", "pdf")
        document.save(output_path, garbage=4, deflate=True)

    return output_path


def sign_pdf_with_image(input_path, image_path, page_target="last", x_percent=30, y_percent=78, width_percent=35):
    """
    Stamps an uploaded signature image (e.g. a scanned handwritten
    signature) onto a PDF, at an exact position and size — matching a box
    the user dragged/resized on a page preview. Aspect ratio and
    transparency are preserved (height is always derived from the image's
    own aspect ratio, not dragged independently, so the signature never
    looks stretched).

    Returns:
        output_path
    """

    input_path = str(input_path)
    x_frac = _clamp_fraction(x_percent)
    y_frac = _clamp_fraction(y_percent)
    width_frac = _clamp_fraction(width_percent, minimum=5)

    with Image.open(image_path) as source:
        image_width, image_height = source.size

    if image_width <= 0 or image_height <= 0:
        raise ValueError("This image could not be read.")

    aspect_ratio = image_height / image_width

    with pymupdf.open(input_path) as document:

        for page in _target_pages(document, page_target):
            rect = page.rect
            box_x = rect.x0 + x_frac * rect.width
            box_y = rect.y0 + y_frac * rect.height
            target_width = width_frac * rect.width
            target_height = target_width * aspect_ratio

            image_rect = pymupdf.Rect(box_x, box_y, box_x + target_width, box_y + target_height)
            page.insert_image(image_rect, filename=image_path, keep_proportion=True)

        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = _unique_path(get_output_folder(), base_name, "_signed", "pdf")
        document.save(output_path, garbage=4, deflate=True)

    return output_path
