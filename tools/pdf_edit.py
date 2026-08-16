import os

import pymupdf

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


def add_watermark(input_path, text, opacity=30, font_size=48, color="#999999"):
    """
    Overlays a diagonal, semi-transparent text watermark across every page.

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

            text_width = pymupdf.get_text_length(text, fontname="helv", fontsize=font_size)
            point = pymupdf.Point(center.x - text_width / 2, center.y + font_size * 0.35)

            page.insert_text(
                point,
                text,
                fontname="helv",
                fontsize=font_size,
                color=rgb,
                fill_opacity=fill_opacity,
                morph=morph,
            )

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
