import os

from pypdf import PdfReader, PdfWriter

from tools.image_resizer import get_output_folder


def _unique_path(output_folder, base_name, suffix, ext=".pdf"):
    output_path = os.path.join(output_folder, f"{base_name}{suffix}{ext}")
    counter = 1
    while os.path.exists(output_path):
        output_path = os.path.join(output_folder, f"{base_name}{suffix}_{counter}{ext}")
        counter += 1
    return output_path


def get_page_count(input_path):
    return len(PdfReader(str(input_path)).pages)


def parse_page_range(spec, page_count):
    """
    Parses a 1-indexed page range string like "1,3,5-8" into a sorted list
    of 0-indexed page numbers, validated against page_count.
    """

    spec = (spec or "").strip()

    if not spec:
        raise ValueError("Please enter at least one page number.")

    pages = set()

    for token in spec.split(","):
        token = token.strip()

        if not token:
            continue

        if "-" in token:
            parts = token.split("-")
            if len(parts) != 2:
                raise ValueError(f"'{token}' is not a valid page or range.")
            start_text, end_text = parts
            if not (start_text.strip().isdigit() and end_text.strip().isdigit()):
                raise ValueError(f"'{token}' is not a valid page or range.")
            start, end = int(start_text), int(end_text)
            if start > end:
                start, end = end, start
            for page in range(start, end + 1):
                pages.add(page)
        else:
            if not token.isdigit():
                raise ValueError(f"'{token}' is not a valid page number.")
            pages.add(int(token))

    if not pages:
        raise ValueError("Please enter at least one page number.")

    for page in pages:
        if page < 1 or page > page_count:
            raise ValueError(f"Page {page} is out of range (this PDF has {page_count} pages).")

    return sorted(page - 1 for page in pages)


def merge_pdfs(input_paths):
    """
    Combines multiple PDFs into one, in the given order.

    Returns:
        output_path
    """

    if len(input_paths) < 2:
        raise ValueError("Select at least 2 PDFs to merge.")

    writer = PdfWriter()

    for input_path in input_paths:
        reader = PdfReader(str(input_path))
        for page in reader.pages:
            writer.add_page(page)

    output_path = _unique_path(get_output_folder(), "merged", "")

    with open(output_path, "wb") as output_file:
        writer.write(output_file)

    return output_path


def remove_pages(input_path, pages_zero_indexed):
    """
    Writes a copy of the PDF with the given 0-indexed pages removed.

    Returns:
        output_path
    """

    input_path = str(input_path)
    reader = PdfReader(input_path)
    to_remove = set(pages_zero_indexed)

    if len(to_remove) >= len(reader.pages):
        raise ValueError("Cannot remove every page — the result would be empty.")

    writer = PdfWriter()
    for index, page in enumerate(reader.pages):
        if index not in to_remove:
            writer.add_page(page)

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = _unique_path(get_output_folder(), base_name, "_edited")

    with open(output_path, "wb") as output_file:
        writer.write(output_file)

    return output_path


def reorder_multi_pdf(page_entries, rotations=None, output_base_name="organized"):
    """
    Writes one new PDF assembled from pages potentially drawn from several
    source PDFs, in the given final order — this is how both cross-document
    combining and single-document reorder/delete are expressed.

    Args:
        page_entries: list of (source_path, page_index) tuples, 0-indexed,
            in the desired final order. A page simply not being listed is
            how deletion is expressed.
        rotations: optional dict of {(source_path, page_index): degrees} —
            extra rotation applied on top of that page's current rotation.
        output_base_name: filename stem for the output PDF.

    Returns:
        output_path
    """

    if not page_entries:
        raise ValueError("At least one page must remain.")

    rotations = rotations or {}
    readers = {}
    writer = PdfWriter()

    for source_path, page_index in page_entries:
        source_path = str(source_path)

        if source_path not in readers:
            readers[source_path] = PdfReader(source_path)

        new_page = writer.add_page(readers[source_path].pages[page_index])
        angle = rotations.get((source_path, page_index), 0)
        if angle:
            new_page.rotate(angle)

    output_path = _unique_path(get_output_folder(), output_base_name, "_organized")

    with open(output_path, "wb") as output_file:
        writer.write(output_file)

    return output_path
