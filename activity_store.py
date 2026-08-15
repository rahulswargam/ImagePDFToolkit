import json
from datetime import datetime

from PySide6.QtCore import QSettings

_ORG = "RahulSwargam"
_APP = "ImagePDFToolkit"

_KEY = "recent_activity"
_MAX_ENTRIES = 20


def _settings():
    return QSettings(_ORG, _APP)


def record(kind, filename, detail, timestamp=None):
    """Adds one entry to the front of the recent-activity list, capped at 20.

    kind: short tag identifying the tool ("resize", "png_to_jpg", "jpg_to_pdf",
    "pdf_to_jpg", "lock", "unlock") — used by the UI to pick an icon.
    filename: basename only, never a full path — activity is shown in the UI,
    which should not expose local file-system paths.
    detail: short human-readable summary, e.g. "316 KB -> 198 KB" or
    "Converted to JPG".
    """

    entries = get_recent(limit=_MAX_ENTRIES)
    entries.insert(
        0,
        {
            "kind": kind,
            "filename": filename,
            "detail": detail,
            "timestamp": (timestamp or datetime.now()).isoformat(),
        },
    )
    _settings().setValue(_KEY, json.dumps(entries[:_MAX_ENTRIES]))


def get_recent(limit=8):
    raw = _settings().value(_KEY, "")
    if not raw:
        return []

    try:
        entries = json.loads(raw)
    except (TypeError, ValueError):
        return []

    if not isinstance(entries, list):
        return []

    return entries[:limit]


def clear():
    _settings().remove(_KEY)
