import os

_VERSION_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "VERSION")


def _read_version():
    try:
        with open(_VERSION_PATH, "r", encoding="utf-8") as version_file:
            return version_file.read().strip()
    except OSError:
        return "0.0.0"


APP_VERSION = _read_version()
