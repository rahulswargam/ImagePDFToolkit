import os

import pymupdf

from tools.image_resizer import get_output_folder


def convert_pdf_to_jpg(input_path, quality=95, dpi=200):
    """
    Render every page of a PDF into a separate high-quality JPG,
    saved into its own subfolder (named after the PDF) inside the
    shared output folder.

    Returns:
        list of output file paths, in page order
    """

    input_path = str(input_path)

    base_name = os.path.splitext(os.path.basename(input_path))[0]

    output_folder = os.path.join(get_output_folder(), base_name)
    os.makedirs(output_folder, exist_ok=True)

    quality = max(1, min(int(quality), 100))
    zoom = dpi / 72.0
    matrix = pymupdf.Matrix(zoom, zoom)

    output_paths = []

    with pymupdf.open(input_path) as document:

        if document.page_count == 0:
            raise ValueError("This PDF has no pages.")

        page_number_width = len(str(document.page_count))

        for index, page in enumerate(document, start=1):

            pixmap = page.get_pixmap(matrix=matrix, alpha=False)

            output_path = os.path.join(
                output_folder,
                f"{base_name}_page_{index:0{page_number_width}}.jpg",
            )

            counter = 1
            while os.path.exists(output_path):
                output_path = os.path.join(
                    output_folder,
                    f"{base_name}_page_{index:0{page_number_width}}_{counter}.jpg",
                )
                counter += 1

            pixmap.save(output_path, jpg_quality=quality)

            output_paths.append(output_path)

    return output_paths
