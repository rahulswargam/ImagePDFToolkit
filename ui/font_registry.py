from PySide6.QtGui import QFontDatabase

_registered = {}


def qt_family_for(file_path):
    """
    Registers a bundled font file with Qt's application font database
    (once, cached thereafter) and returns the family name Qt assigned to
    it — for live UI preview only. The actual PDF output always goes
    through pymupdf with the same file, independently of Qt.

    Returns None if file_path is falsy or the font couldn't be loaded.
    """

    if not file_path:
        return None

    if file_path in _registered:
        return _registered[file_path]

    font_id = QFontDatabase.addApplicationFont(file_path)
    families = QFontDatabase.applicationFontFamilies(font_id)
    family = families[0] if families else None

    _registered[file_path] = family
    return family
