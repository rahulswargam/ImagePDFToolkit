import os

from PySide6.QtCore import QSettings

_ORG = "RahulSwargam"
_APP = "ImagePDFToolkit"

THEME_SYSTEM = "system"
THEME_LIGHT = "light"
THEME_DARK = "dark"


def _settings():
    return QSettings(_ORG, _APP)


def get_theme_mode():
    mode = _settings().value("theme_mode", THEME_SYSTEM)
    return mode if mode in (THEME_SYSTEM, THEME_LIGHT, THEME_DARK) else THEME_SYSTEM


def set_theme_mode(mode):
    _settings().setValue("theme_mode", mode)


def get_output_folder():
    """
    Returns the user's configured output folder, or None if they haven't
    set a custom one (callers should fall back to the default location).
    """

    folder = _settings().value("output_folder", "")

    if folder and os.path.isdir(folder):
        return folder

    return None


def set_output_folder(path):
    _settings().setValue("output_folder", path)


def reset_output_folder():
    _settings().remove("output_folder")
