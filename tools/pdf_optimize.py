import io
import os

import pymupdf
from PIL import Image

from tools.image_resizer import get_output_folder


def _flatten_to_rgb(image, background=(255, 255, 255)):
    """JPEG has no alpha channel, so flatten transparency onto a solid color."""

    if image.mode in ("RGBA", "LA", "P"):

        if image.mode == "P":
            image = image.convert("RGBA")

        if image.mode in ("RGBA", "LA"):
            flattened = Image.new("RGB", image.size, background)
            flattened.paste(image, mask=image.getchannel("A"))
            return flattened

        return image.convert("RGB")

    return image.convert("RGB")


def _unique_pdf_path(output_folder, base_name, suffix):
    output_path = os.path.join(output_folder, f"{base_name}{suffix}.pdf")
    counter = 1
    while os.path.exists(output_path):
        output_path = os.path.join(output_folder, f"{base_name}{suffix}_{counter}.pdf")
        counter += 1
    return output_path


def compress_pdf(input_path, image_quality=60):
    """
    Shrinks a PDF's file size by recompressing its embedded images as JPEGs
    at the given quality and rebuilding the document.

    Returns:
        output_path, original_bytes, compressed_bytes
    """

    input_path = str(input_path)
    original_bytes = os.path.getsize(input_path)
    image_quality = max(1, min(int(image_quality), 100))

    with pymupdf.open(input_path) as document:

        seen_xrefs = set()

        for page in document:
            for image_info in page.get_images(full=True):
                xref = image_info[0]
                if xref in seen_xrefs:
                    continue
                seen_xrefs.add(xref)

                try:
                    base_image = document.extract_image(xref)
                    with Image.open(io.BytesIO(base_image["image"])) as source:
                        rgb_image = _flatten_to_rgb(source)
                        buffer = io.BytesIO()
                        rgb_image.save(buffer, "JPEG", quality=image_quality, optimize=True)

                    if len(buffer.getvalue()) < len(base_image["image"]):
                        page.replace_image(xref, stream=buffer.getvalue())
                except Exception:
                    continue

        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = _unique_pdf_path(get_output_folder(), base_name, "_compressed")

        document.save(output_path, garbage=4, deflate=True, clean=True)

    compressed_bytes = os.path.getsize(output_path)

    return output_path, original_bytes, compressed_bytes


def repair_pdf(input_path):
    """
    Attempts to fix a corrupted or malformed PDF by re-parsing it with
    MuPDF's tolerant parser and rewriting a clean copy.

    Returns:
        output_path
    """

    input_path = str(input_path)

    with pymupdf.open(input_path) as document:

        if document.page_count == 0:
            raise ValueError("This PDF could not be read — it may be too badly damaged to repair.")

        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = _unique_pdf_path(get_output_folder(), base_name, "_repaired")

        document.save(output_path, garbage=4, deflate=True, clean=True)

    return output_path
