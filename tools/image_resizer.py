import io
import os
from pathlib import Path

from PIL import Image

import settings_store


def get_output_folder():
    """
    Returns the user's configured output folder if they've set one in
    Settings, otherwise Desktop/Image & PDF Toolkit (created if missing).
    """
    custom_folder = settings_store.get_output_folder()

    if custom_folder:
        return custom_folder

    desktop = Path.home() / "Desktop"
    output_folder = desktop / "Image & PDF Toolkit"

    output_folder.mkdir(parents=True, exist_ok=True)

    return str(output_folder)


def get_image_size(file_path):
    """
    Returns the image dimensions as:
        (width, height)
    """
    with Image.open(file_path) as image:
        return image.size


def format_file_size(num_bytes):
    """Formats a byte count as a human-readable KB/MB string."""

    kb = num_bytes / 1024

    if kb < 1024:
        return f"{kb:.0f} KB"

    return f"{kb / 1024:.2f} MB"


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


def _encode_jpeg(image, quality):
    buffer = io.BytesIO()
    image.save(buffer, "JPEG", quality=quality, optimize=True, progressive=True)
    return buffer.getvalue()


def compress_to_target_size(input_path, target_kb, max_quality=90):
    """
    Compress an image to a JPG that fits within (approximately) the given
    target size in kilobytes.

    Strategy:
        1. Binary-search JPEG quality (5..max_quality) at the original
           resolution to find the highest quality that fits the target.
        2. If even the lowest quality is still too large, progressively
           downscale the image and repeat the quality search.

    Returns:
        output_path, achieved_kb, quality_used, width, height
    """

    target_bytes = int(target_kb) * 1024

    if target_bytes <= 0:
        raise ValueError("Target size must be greater than 0 KB.")

    max_quality = max(5, min(int(max_quality), 100))

    with Image.open(input_path) as source:
        base_image = _flatten_to_rgb(source)

    scale = 1.0
    best_bytes = None
    best_quality = None
    best_image = None

    for _ in range(8):

        width = max(1, round(base_image.width * scale))
        height = max(1, round(base_image.height * scale))

        candidate = (
            base_image
            if scale == 1.0
            else base_image.resize((width, height), Image.Resampling.LANCZOS)
        )

        low, high = 5, max_quality
        smallest_at_this_scale = None
        smallest_quality_at_this_scale = None

        while low <= high:
            mid = (low + high) // 2
            encoded = _encode_jpeg(candidate, mid)

            if smallest_at_this_scale is None or len(encoded) <= smallest_at_this_scale:
                smallest_at_this_scale = len(encoded)
                smallest_quality_at_this_scale = mid

            if len(encoded) <= target_bytes:
                best_bytes = encoded
                best_quality = mid
                low = mid + 1
            else:
                high = mid - 1

        if best_bytes is not None:
            break

        # Even the lowest quality at this scale doesn't fit; shrink further.
        if smallest_at_this_scale is not None and smallest_at_this_scale <= target_bytes:
            best_bytes = _encode_jpeg(candidate, smallest_quality_at_this_scale)
            best_quality = smallest_quality_at_this_scale
            break

        scale *= 0.85

        if width <= 64 or height <= 64:
            # Can't shrink further; accept the smallest result we found.
            best_bytes = _encode_jpeg(candidate, 5)
            best_quality = 5
            best_image = candidate
            break

    if best_bytes is None:
        best_bytes = _encode_jpeg(base_image, 5)
        best_quality = 5

    output_folder = get_output_folder()
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_folder, f"{base_name}_compressed.jpg")

    counter = 1
    while os.path.exists(output_path):
        output_path = os.path.join(output_folder, f"{base_name}_compressed_{counter}.jpg")
        counter += 1

    with open(output_path, "wb") as output_file:
        output_file.write(best_bytes)

    with Image.open(io.BytesIO(best_bytes)) as final_image:
        final_width, final_height = final_image.size

    achieved_kb = len(best_bytes) / 1024

    return output_path, achieved_kb, best_quality, final_width, final_height
