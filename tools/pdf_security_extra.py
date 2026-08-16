import difflib
import os

import pymupdf
from PIL import Image

from tools.image_resizer import get_output_folder

_MARGIN = 40
_BASE_SIGNATURE_FONT_SIZE = 22
_MAX_IMAGE_SIGNATURE_WIDTH_FRACTION = 0.4

_WINDOWS_FONTS_DIR = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")

# A few curated signature styles. "file" points at a font that ships with
# Windows by default (not Office-only), so no extra font needs to be
# bundled; if it's ever missing on a given machine, "fallback" is one of
# pymupdf's built-in base-14 fonts so signing never breaks.
SIGNATURE_FONTS = {
    "cursive": {
        "label": "Cursive",
        "file": os.path.join(_WINDOWS_FONTS_DIR, "segoesc.ttf"),
        "fallback": "heit",
    },
    "handwriting": {
        "label": "Handwriting",
        "file": os.path.join(_WINDOWS_FONTS_DIR, "Inkfree.ttf"),
        "fallback": "heit",
    },
    "italic": {
        "label": "Classic Italic",
        "file": None,
        "fallback": "heit",
    },
    "elegant": {
        "label": "Elegant",
        "file": None,
        "fallback": "tiit",
    },
}
DEFAULT_SIGNATURE_FONT = "cursive"


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


def sign_pdf(
    input_path,
    signer_name,
    page_target="last",
    position="bottom-right",
    scale_percent=100,
    font_key=DEFAULT_SIGNATURE_FONT,
):
    """
    Stamps a visual signature (name in a script/handwriting-style font, with
    a signature line) onto a PDF. This is a visual mark, not a
    legally-binding cryptographic digital signature.

    `scale_percent` (10-100) scales the signature text/line size; 100% is
    the largest, most legible size. `font_key` selects a style from
    SIGNATURE_FONTS.

    Returns:
        output_path
    """

    input_path = str(input_path)
    signer_name = (signer_name or "").strip()

    if not signer_name:
        raise ValueError("Please enter a name to sign with.")

    scale = max(10, min(int(scale_percent), 100)) / 100
    name_font_size = max(6, round(_BASE_SIGNATURE_FONT_SIZE * scale))
    caption_font_size = max(5, round(8 * scale))
    fontname, fontfile = _resolve_signature_font(font_key)

    with pymupdf.open(input_path) as document:

        for page in _target_pages(document, page_target):
            rect = page.rect
            name_width = _measure_text(signer_name, fontname, fontfile, name_font_size)
            line_width = max(name_width + 20, 140 * scale)

            if "left" in position:
                x = rect.x0 + _MARGIN
            elif "center" in position:
                x = (rect.x0 + rect.x1) / 2 - line_width / 2
            else:
                x = rect.x1 - _MARGIN - line_width

            y = rect.y1 - _MARGIN

            page.draw_line((x, y), (x + line_width, y), color=(0.4, 0.42, 0.48), width=0.8)
            page.insert_text(
                (x, y - 6),
                signer_name,
                fontname=fontname,
                fontfile=fontfile,
                fontsize=name_font_size,
                color=(0.1, 0.1, 0.15),
            )
            page.insert_text(
                (x, y + caption_font_size + 4),
                "Signed electronically",
                fontname="helv",
                fontsize=caption_font_size,
                color=(0.5, 0.52, 0.58),
            )

        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = _unique_path(get_output_folder(), base_name, "_signed", "pdf")
        document.save(output_path, garbage=4, deflate=True)

    return output_path


def sign_pdf_with_image(input_path, image_path, page_target="last", position="bottom-right", scale_percent=100):
    """
    Stamps an uploaded signature image (e.g. a scanned handwritten
    signature) onto a PDF, preserving its aspect ratio and transparency.

    `scale_percent` (10-100) scales the signature's width as a fraction of
    the page width; 100% is the largest allowed size.

    Returns:
        output_path
    """

    input_path = str(input_path)
    scale = max(10, min(int(scale_percent), 100)) / 100

    with Image.open(image_path) as source:
        image_width, image_height = source.size

    if image_width <= 0 or image_height <= 0:
        raise ValueError("This image could not be read.")

    aspect_ratio = image_height / image_width

    with pymupdf.open(input_path) as document:

        for page in _target_pages(document, page_target):
            rect = page.rect
            target_width = rect.width * _MAX_IMAGE_SIGNATURE_WIDTH_FRACTION * scale
            target_height = target_width * aspect_ratio

            if "left" in position:
                x = rect.x0 + _MARGIN
            elif "center" in position:
                x = (rect.x0 + rect.x1) / 2 - target_width / 2
            else:
                x = rect.x1 - _MARGIN - target_width

            y = rect.y1 - _MARGIN - target_height

            image_rect = pymupdf.Rect(x, y, x + target_width, y + target_height)
            page.insert_image(image_rect, filename=image_path, keep_proportion=True)

        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = _unique_path(get_output_folder(), base_name, "_signed", "pdf")
        document.save(output_path, garbage=4, deflate=True)

    return output_path


def redact_pdf(input_path, search_text):
    """
    Finds every occurrence of `search_text` in a PDF, blacks it out, and
    permanently removes the underlying text/image content beneath it
    (true redaction, not just a visual cover).

    Returns:
        output_path, occurrences_removed
    """

    input_path = str(input_path)
    search_text = (search_text or "").strip()

    if not search_text:
        raise ValueError("Please enter the text you want to redact.")

    occurrences = 0

    with pymupdf.open(input_path) as document:

        for page in document:
            matches = page.search_for(search_text)
            for rect in matches:
                page.add_redact_annot(rect, fill=(0, 0, 0))
                occurrences += 1
            if matches:
                page.apply_redactions()

        if occurrences == 0:
            raise ValueError(f'"{search_text}" was not found in this PDF.')

        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = _unique_path(get_output_folder(), base_name, "_redacted", "pdf")
        document.save(output_path, garbage=4, deflate=True)

    return output_path, occurrences


def compare_pdfs(path_a, path_b):
    """
    Compares the text content of two PDFs page-by-page and writes a unified
    diff report.

    Returns:
        report_path, differing_page_count, total_pages_compared
    """

    path_a, path_b = str(path_a), str(path_b)

    with pymupdf.open(path_a) as doc_a, pymupdf.open(path_b) as doc_b:
        pages_a = [page.get_text() for page in doc_a]
        pages_b = [page.get_text() for page in doc_b]

    total_pages = max(len(pages_a), len(pages_b))
    differing_pages = 0
    report_lines = [
        f"Comparing:\n  A: {os.path.basename(path_a)} ({len(pages_a)} pages)\n"
        f"  B: {os.path.basename(path_b)} ({len(pages_b)} pages)\n"
    ]

    for index in range(total_pages):
        text_a = pages_a[index] if index < len(pages_a) else ""
        text_b = pages_b[index] if index < len(pages_b) else ""

        if text_a == text_b:
            continue

        differing_pages += 1
        diff = list(
            difflib.unified_diff(
                text_a.splitlines(),
                text_b.splitlines(),
                fromfile=f"A page {index + 1}",
                tofile=f"B page {index + 1}",
                lineterm="",
            )
        )
        report_lines.append(f"\n{'=' * 60}\nPage {index + 1} differs\n{'=' * 60}")
        report_lines.extend(diff if diff else ["(page present in only one document)"])

    if differing_pages == 0:
        report_lines.append("\nNo text differences found — both PDFs contain the same text.")

    base_name_a = os.path.splitext(os.path.basename(path_a))[0]
    output_path = _unique_path(get_output_folder(), base_name_a, "_compare_report", "txt")

    with open(output_path, "w", encoding="utf-8") as report_file:
        report_file.write("\n".join(report_lines))

    return output_path, differing_pages, total_pages
