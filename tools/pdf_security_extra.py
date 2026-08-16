import difflib
import os

import pymupdf

from tools.image_resizer import get_output_folder

_MARGIN = 40


def _unique_path(output_folder, base_name, suffix, ext):
    output_path = os.path.join(output_folder, f"{base_name}{suffix}.{ext}")
    counter = 1
    while os.path.exists(output_path):
        output_path = os.path.join(output_folder, f"{base_name}{suffix}_{counter}.{ext}")
        counter += 1
    return output_path


def sign_pdf(input_path, signer_name, page_target="last", position="bottom-right"):
    """
    Stamps a visual signature (name in an italic script-style font, with a
    signature line) onto a PDF. This is a visual mark, not a legally-binding
    cryptographic digital signature.

    Returns:
        output_path
    """

    input_path = str(input_path)
    signer_name = (signer_name or "").strip()

    if not signer_name:
        raise ValueError("Please enter a name to sign with.")

    with pymupdf.open(input_path) as document:

        if page_target == "first":
            targets = [document[0]]
        elif page_target == "all":
            targets = list(document)
        else:
            targets = [document[-1]]

        for page in targets:
            rect = page.rect
            name_width = pymupdf.get_text_length(signer_name, fontname="heit", fontsize=22)
            line_width = max(name_width + 20, 140)

            if "left" in position:
                x = rect.x0 + _MARGIN
            elif "center" in position:
                x = (rect.x0 + rect.x1) / 2 - line_width / 2
            else:
                x = rect.x1 - _MARGIN - line_width

            y = rect.y1 - _MARGIN

            page.draw_line((x, y), (x + line_width, y), color=(0.4, 0.42, 0.48), width=0.8)
            page.insert_text((x, y - 6), signer_name, fontname="heit", fontsize=22, color=(0.1, 0.1, 0.15))
            page.insert_text((x, y + 12), "Signed electronically", fontname="helv", fontsize=8, color=(0.5, 0.52, 0.58))

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
