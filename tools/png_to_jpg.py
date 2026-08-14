import os

from PIL import Image

from tools.image_resizer import get_output_folder


def convert_png_to_jpg(input_path, quality=95, background=(255, 255, 255)):
    """
    Convert a PNG (or any Pillow-readable image) into a JPG.

    Transparency is flattened onto a solid background before saving,
    since JPEG has no alpha channel.

    Returns:
        output_path
    """

    input_path = str(input_path)

    with Image.open(input_path) as image:

        if image.mode in ("RGBA", "LA", "P"):

            if image.mode == "P":
                image = image.convert("RGBA")

            if image.mode in ("RGBA", "LA"):
                flattened = Image.new("RGB", image.size, background)
                flattened.paste(image, mask=image.getchannel("A"))
                image = flattened
            else:
                image = image.convert("RGB")
        else:
            image = image.convert("RGB")

        output_folder = get_output_folder()

        base_name = os.path.splitext(os.path.basename(input_path))[0]

        output_path = os.path.join(output_folder, f"{base_name}.jpg")

        counter = 1
        while os.path.exists(output_path):
            output_path = os.path.join(output_folder, f"{base_name}_{counter}.jpg")
            counter += 1

        quality = max(1, min(int(quality), 100))

        image.save(
            output_path,
            "JPEG",
            quality=quality,
            optimize=True,
            progressive=True,
        )

    return output_path
