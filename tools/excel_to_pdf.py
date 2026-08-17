import os

from tools.image_resizer import get_output_folder
from tools.office_com import is_office_app_installed

_XL_TYPE_PDF = 0


def _unique_pdf_path(output_folder, base_name, suffix):
    output_path = os.path.join(output_folder, f"{base_name}{suffix}.pdf")
    counter = 1
    while os.path.exists(output_path):
        output_path = os.path.join(output_folder, f"{base_name}{suffix}_{counter}.pdf")
        counter += 1
    return output_path


def _convert_via_com(input_path, output_path):
    import pythoncom
    import win32com.client

    pythoncom.CoInitialize()
    excel = None
    try:
        excel = win32com.client.DispatchEx("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        workbook = excel.Workbooks.Open(os.path.abspath(input_path), ReadOnly=True)
        try:
            workbook.ExportAsFixedFormat(_XL_TYPE_PDF, output_path)
        finally:
            workbook.Close(False)
    finally:
        if excel is not None:
            excel.Quit()
        pythoncom.CoUninitialize()


def _convert_via_fallback(input_path, output_path):
    if input_path.lower().endswith(".xls"):
        raise ValueError("Legacy .xls files need Microsoft Excel installed to convert.")

    import openpyxl
    from reportlab.lib.pagesizes import LETTER, landscape
    from reportlab.platypus import PageBreak, SimpleDocTemplate, Table, TableStyle

    workbook = openpyxl.load_workbook(input_path, data_only=True)
    story = []

    for sheet in workbook.worksheets:
        rows = [
            [("" if cell.value is None else str(cell.value)) for cell in row]
            for row in sheet.iter_rows()
        ]
        if rows:
            table = Table(rows)
            table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, "#999999")]))
            story.append(table)
        story.append(PageBreak())

    if not story:
        raise ValueError("This workbook has no readable content.")

    SimpleDocTemplate(output_path, pagesize=landscape(LETTER)).build(story)


def convert_excel_to_pdf(input_path):
    """
    Convert an Excel workbook into a PDF. Uses Microsoft Excel (COM
    automation) when it's installed, for exact fidelity. Falls back to a
    simplified table renderer (no print areas, page breaks, or formatting)
    when Excel isn't available or the COM call fails.

    Returns:
        (output_path, method) where method is "com" or "fallback"
    """

    input_path = str(input_path)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = _unique_pdf_path(get_output_folder(), base_name, "")

    if is_office_app_installed("excel"):
        try:
            _convert_via_com(input_path, output_path)
            return output_path, "com"
        except Exception:
            pass

    _convert_via_fallback(input_path, output_path)
    return output_path, "fallback"
