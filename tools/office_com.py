import winreg

_PROG_IDS = {
    "word": "Word.Application",
    "powerpoint": "PowerPoint.Application",
    "excel": "Excel.Application",
}


def is_office_app_installed(app_key):
    """
    Cheap registry check for whether an Office app's COM ProgID is
    registered — used to decide whether to show a fallback-converter
    warning in the UI before conversion even starts. A registered ProgID
    doesn't guarantee a working install; the actual conversion call is
    still wrapped in try/except and falls back on any failure regardless
    of what this returns.
    """
    prog_id = _PROG_IDS[app_key]

    try:
        winreg.QueryValue(winreg.HKEY_CLASSES_ROOT, prog_id)
        return True
    except OSError:
        return False
