import os

from PIL import Image

from tools.image_resizer import get_output_folder


def convert_images_to_pdf(input_paths, output_name="Converted"):
    """
    Combine one or more images (JPG/PNG/etc.) into a single multi-page PDF,
    in the given order.

    Returns:
        output_path
    """

    if not input_paths:
        raise ValueError("Please select at least one image.")

    pages = []
    opened_images = []

    try:
        for path in input_paths:

            image = Image.open(str(path))

            if image.mode != "RGB":
                image = image.convert("RGB")

            opened_images.append(image)
            pages.append(image)

        output_folder = get_output_folder()

        base_name = output_name or "Converted"

        output_path = os.path.join(output_folder, f"{base_name}.pdf")

        counter = 1
        while os.path.exists(output_path):
            output_path = os.path.join(output_folder, f"{base_name}_{counter}.pdf")
            counter += 1

        first_page, remaining_pages = pages[0], pages[1:]

        first_page.save(
            output_path,
            "PDF",
            save_all=True,
            append_images=remaining_pages,
        )

    finally:
        for image in opened_images:
            image.close()

    return output_path
