import io
import os

import pymupdf
from PIL import Image

from tools.image_resizer import get_output_folder

_MARGIN = 28


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


def add_page_numbers(input_path, position="bottom-center", start_at=1, font_size=11):
    """
    Stamps a page number onto every page of a PDF.

    Returns:
        output_path
    """

    input_path = str(input_path)

    with pymupdf.open(input_path) as document:

        for index, page in enumerate(document):
            text = str(start_at + index)
            rect = page.rect
            text_width = pymupdf.get_text_length(text, fontname="helv", fontsize=font_size)

            if "left" in position:
                x = rect.x0 + _MARGIN
            elif "right" in position:
                x = rect.x1 - _MARGIN - text_width
            else:
                x = (rect.x0 + rect.x1) / 2 - text_width / 2

            y = rect.y1 - _MARGIN if "bottom" in position else rect.y0 + _MARGIN + font_size

            page.insert_text((x, y), text, fontname="helv", fontsize=font_size, color=(0.35, 0.37, 0.42))

        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = _unique_pdf_path(get_output_folder(), base_name, "_numbered")
        document.save(output_path, garbage=4, deflate=True)

    return output_path


def add_watermark(input_path, text, opacity=30, font_size=48, color="#999999", fontname="helv"):
    """
    Overlays a diagonal, semi-transparent text watermark across every page.

    `fontname` is one of pymupdf's built-in base-14 font shorthands
    (e.g. "helv", "hebo", "tiro", "tibo", "cour").

    Returns:
        output_path
    """

    input_path = str(input_path)
    text = (text or "").strip()

    if not text:
        raise ValueError("Please enter watermark text.")

    fill_opacity = max(1, min(int(opacity), 100)) / 100
    rgb = _hex_to_rgb01(color)

    with pymupdf.open(input_path) as document:

        for page in document:
            rect = page.rect
            center = rect.tl + (rect.br - rect.tl) / 2
            morph = (center, pymupdf.Matrix(45))

            text_width = pymupdf.get_text_length(text, fontname=fontname, fontsize=font_size)
            point = pymupdf.Point(center.x - text_width / 2, center.y + font_size * 0.35)

            page.insert_text(
                point,
                text,
                fontname=fontname,
                fontsize=font_size,
                color=rgb,
                fill_opacity=fill_opacity,
                morph=morph,
            )

        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = _unique_pdf_path(get_output_folder(), base_name, "_watermarked")
        document.save(output_path, garbage=4, deflate=True)

    return output_path


def add_image_watermark(input_path, image_path, opacity=30, scale_percent=50, position="center", rotation_degrees=0):
    """
    Overlays a semi-transparent image/logo watermark onto every page,
    preserving aspect ratio and any existing transparency in the source
    image (opacity is applied on top of it, not instead of it).

    `scale_percent` (5-100) scales the watermark's width as a fraction of
    the page width; 100% is the largest allowed size. `position` is one of
    "center", "top-left", "top-right", "bottom-left", "bottom-right".

    Returns:
        output_path
    """

    input_path = str(input_path)
    fill_opacity = max(1, min(int(opacity), 100)) / 100
    scale = max(5, min(int(scale_percent), 100)) / 100
    rotation_degrees = int(rotation_degrees) % 360

    with Image.open(image_path) as source:
        rgba = source.convert("RGBA")
        alpha = rgba.getchannel("A").point(lambda value: int(value * fill_opacity))
        rgba.putalpha(alpha)

        if rotation_degrees:
            rgba = rgba.rotate(rotation_degrees, expand=True, resample=Image.BICUBIC)

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
            target_width = rect.width * 0.5 * scale
            target_height = target_width * aspect_ratio

            if position == "top-left":
                x, y = rect.x0 + _MARGIN, rect.y0 + _MARGIN
            elif position == "top-right":
                x, y = rect.x1 - _MARGIN - target_width, rect.y0 + _MARGIN
            elif position == "bottom-left":
                x, y = rect.x0 + _MARGIN, rect.y1 - _MARGIN - target_height
            elif position == "bottom-right":
                x, y = rect.x1 - _MARGIN - target_width, rect.y1 - _MARGIN - target_height
            else:
                x = (rect.x0 + rect.x1) / 2 - target_width / 2
                y = (rect.y0 + rect.y1) / 2 - target_height / 2

            image_rect = pymupdf.Rect(x, y, x + target_width, y + target_height)
            page.insert_image(image_rect, stream=image_bytes, keep_proportion=True)

        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = _unique_pdf_path(get_output_folder(), base_name, "_watermarked")
        document.save(output_path, garbage=4, deflate=True)

    return output_path


def crop_pdf(input_path, margin_pt=36):
    """
    Crops every page inward by the given margin, in points (72pt = 1in).

    Returns:
        output_path
    """

    input_path = str(input_path)
    margin_pt = max(0, float(margin_pt))

    with pymupdf.open(input_path) as document:

        for page in document:
            rect = page.rect

            if margin_pt * 2 >= min(rect.width, rect.height):
                raise ValueError("Crop margin is too large for this page size.")

            new_rect = pymupdf.Rect(
                rect.x0 + margin_pt,
                rect.y0 + margin_pt,
                rect.x1 - margin_pt,
                rect.y1 - margin_pt,
            )
            page.set_cropbox(new_rect)

        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = _unique_pdf_path(get_output_folder(), base_name, "_cropped")
        document.save(output_path, garbage=4, deflate=True)

    return output_path
