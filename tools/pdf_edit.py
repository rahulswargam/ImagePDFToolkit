import io
import os

import pymupdf
from PIL import Image

from tools.image_resizer import get_output_folder

_ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fonts")
_WATERMARK_FONTS_DIR = os.path.join(_ASSETS_DIR, "watermark")
_ROBOTO_FONT_PATH = os.path.join(_ASSETS_DIR, "Roboto-Variable.ttf")

# Exactly the five fonts requested for watermarks. "Helvetica Neue" and
# "Futura" are proprietary (Monotype/Linotype) and can't legally be
# bundled or redistributed — pymupdf's built-in base-14 Helvetica ("helv")
# stands in for Helvetica Neue, and Poppins (a well-known free
# geometric-sans, Google Fonts/OFL) stands in for Futura. "Garamond" uses
# EB Garamond, the standard free equivalent of the classic typeface.
WATERMARK_FONTS = {
    "montserrat": {
        "label": "Montserrat",
        "file": os.path.join(_WATERMARK_FONTS_DIR, "Montserrat-Regular.ttf"),
        "fallback": "helv",
    },
    "helvetica_neue": {
        "label": "Helvetica Neue",
        "file": None,
        "fallback": "helv",
    },
    "garamond": {
        "label": "Garamond",
        "file": os.path.join(_WATERMARK_FONTS_DIR, "EBGaramond-Regular.ttf"),
        "fallback": "tiro",
    },
    "roboto": {
        "label": "Roboto",
        "file": _ROBOTO_FONT_PATH,
        "fallback": "helv",
    },
    "futura": {
        "label": "Futura",
        "file": os.path.join(_WATERMARK_FONTS_DIR, "Poppins-Regular.ttf"),
        "fallback": "helv",
    },
}
DEFAULT_WATERMARK_FONT = "montserrat"


def _resolve_watermark_font(font_key):
    spec = WATERMARK_FONTS.get(font_key, WATERMARK_FONTS[DEFAULT_WATERMARK_FONT])
    file_path = spec.get("file")

    if file_path and os.path.exists(file_path):
        return font_key, file_path

    return spec["fallback"], None


def _measure_text(text, fontname, fontfile, fontsize):
    if fontfile:
        return pymupdf.Font(fontfile=fontfile).text_length(text, fontsize=fontsize)
    return pymupdf.get_text_length(text, fontname=fontname, fontsize=fontsize)


def _clamp_fraction(percent, minimum=0, maximum=100):
    return max(minimum, min(maximum, float(percent))) / 100


def _unique_pdf_path(output_folder, base_name, suffix):
    output_path = os.path.join(output_folder, f"{base_name}{suffix}.pdf")
    counter = 1
    while os.path.exists(output_path):
        output_path = os.path.join(output_folder, f"{base_name}{suffix}_{counter}.pdf")
        counter += 1
    return output_path


def _hex_to_rgb01(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) / 255 for i in (0, 2, 4))


def rotate_pdf(input_path, angle):
    """
    Rotates every page of a PDF by the given angle (90, 180, or 270 degrees,
    clockwise) relative to its current rotation.

    Returns:
        output_path
    """

    input_path = str(input_path)

    with pymupdf.open(input_path) as document:

        for page in document:
            page.set_rotation((page.rotation + angle) % 360)

        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = _unique_pdf_path(get_output_folder(), base_name, "_rotated")
        document.save(output_path, garbage=4, deflate=True)

    return output_path


def add_watermark(
    input_path,
    text,
    opacity=30,
    color="#999999",
    font_key=DEFAULT_WATERMARK_FONT,
    x_percent=25,
    y_percent=45,
    width_percent=50,
    height_percent=10,
    rotation_degrees=0,
):
    """
    Overlays a semi-transparent text watermark onto every page, at an
    exact position, size, and rotation — matching a box the user
    dragged/resized on a page preview.

    `x_percent`/`y_percent` place the box's top-left corner as a fraction
    of the page's width/height; `width_percent`/`height_percent` size it
    the same way. The watermark text is sized to fit within that box
    (shrinking to whichever dimension is tighter), then rotated around the
    box's center by `rotation_degrees`. `font_key` selects a style from
    WATERMARK_FONTS.

    Returns:
        output_path
    """

    input_path = str(input_path)
    text = (text or "").strip()

    if not text:
        raise ValueError("Please enter watermark text.")

    fill_opacity = max(1, min(int(opacity), 100)) / 100
    rgb = _hex_to_rgb01(color)
    fontname, fontfile = _resolve_watermark_font(font_key)
    rotation_degrees = int(rotation_degrees) % 360

    x_frac = _clamp_fraction(x_percent)
    y_frac = _clamp_fraction(y_percent)
    width_frac = _clamp_fraction(width_percent, minimum=5)
    height_frac = _clamp_fraction(height_percent, minimum=3)

    with pymupdf.open(input_path) as document:

        for page in document:
            rect = page.rect
            box_x = rect.x0 + x_frac * rect.width
            box_y = rect.y0 + y_frac * rect.height
            box_width = width_frac * rect.width
            box_height = height_frac * rect.height

            reference_size = 100
            reference_width = _measure_text(text, fontname, fontfile, reference_size)
            width_based_size = (box_width / reference_width * reference_size) if reference_width > 0 else 24
            font_size = max(6, min(width_based_size, box_height))

            text_width = _measure_text(text, fontname, fontfile, font_size)
            center = pymupdf.Point(box_x + box_width / 2, box_y + box_height / 2)
            point = pymupdf.Point(center.x - text_width / 2, center.y + font_size * 0.35)
            # pymupdf.Matrix(theta) rotates counterclockwise for this
            # insert_text/morph usage while the on-screen preview rotates
            # clockwise for the same positive angle — negate to match what
            # the user actually dragged.
            morph = (center, pymupdf.Matrix(-rotation_degrees)) if rotation_degrees else None

            page.insert_text(
                point,
                text,
                fontname=fontname,
                fontfile=fontfile,
                fontsize=font_size,
                color=rgb,
                fill_opacity=fill_opacity,
                morph=morph,
            )

        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = _unique_pdf_path(get_output_folder(), base_name, "_watermarked")
        document.save(output_path, garbage=4, deflate=True)

    return output_path


def add_image_watermark(input_path, image_path, opacity=30, x_percent=25, y_percent=40, width_percent=50, rotation_degrees=0):
    """
    Overlays a semi-transparent image/logo watermark onto every page, at
    an exact position and size — matching a box the user dragged/resized
    on a page preview. Preserves aspect ratio (height is always derived
    from the image's own aspect ratio, not dragged independently) and any
    existing transparency in the source image (opacity is applied on top
    of it, not instead of it).

    Returns:
        output_path
    """

    input_path = str(input_path)
    fill_opacity = max(1, min(int(opacity), 100)) / 100
    rotation_degrees = int(rotation_degrees) % 360
    x_frac = _clamp_fraction(x_percent)
    y_frac = _clamp_fraction(y_percent)
    width_frac = _clamp_fraction(width_percent, minimum=5)

    with Image.open(image_path) as source:
        rgba = source.convert("RGBA")
        alpha = rgba.getchannel("A").point(lambda value: int(value * fill_opacity))
        rgba.putalpha(alpha)

        if rotation_degrees:
            # PIL's rotate() is counterclockwise-positive while the on-screen
            # preview rotates clockwise for the same positive angle — negate
            # to match what the user actually dragged.
            rgba = rgba.rotate(-rotation_degrees, expand=True, resample=Image.BICUBIC)

        buffer = io.BytesIO()
        rgba.save(buffer, "PNG")
        image_bytes = buffer.getvalue()
        image_width, image_height = rgba.size

    if image_width <= 0 or image_height <= 0:
        raise ValueError("This image could not be read.")

    aspect_ratio = image_height / image_width

    with pymupdf.open(input_path) as document:

        for page in document:
            rect = page.rect
            box_x = rect.x0 + x_frac * rect.width
            box_y = rect.y0 + y_frac * rect.height
            target_width = width_frac * rect.width
            target_height = target_width * aspect_ratio

            image_rect = pymupdf.Rect(box_x, box_y, box_x + target_width, box_y + target_height)
            page.insert_image(image_rect, stream=image_bytes, keep_proportion=True)

        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = _unique_pdf_path(get_output_folder(), base_name, "_watermarked")
        document.save(output_path, garbage=4, deflate=True)

    return output_path
