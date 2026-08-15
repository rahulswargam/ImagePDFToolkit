import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

ICON_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "icons", "svg")

_pixmap_cache = {}


def get_pixmap(name, color, size):
    """Renders a hand-authored line icon from assets/icons/svg, tinted to `color`.

    Icons are authored as monochrome (black) SVGs; tinting recolors every
    non-transparent pixel via CompositionMode_SourceIn, so a single icon file
    serves any semantic color token (muted nav icon, bright active icon,
    accent, on-accent, etc.) without pre-baking per-color/per-theme variants.
    """

    key = (name, color, size)
    cached = _pixmap_cache.get(key)
    if cached is not None:
        return cached

    svg_path = os.path.join(ICON_DIR, f"{name}.svg")
    renderer = QSvgRenderer(svg_path)

    render_size = size * 2  # render at 2x for crisp scaling on high-DPI displays
    raw = QPixmap(render_size, render_size)
    raw.fill(Qt.GlobalColor.transparent)

    painter = QPainter(raw)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(painter)
    painter.end()

    tinted = QPixmap(raw.size())
    tinted.fill(Qt.GlobalColor.transparent)

    painter = QPainter(tinted)
    painter.drawPixmap(0, 0, raw)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(tinted.rect(), QColor(color))
    painter.end()

    tinted.setDevicePixelRatio(2.0)

    _pixmap_cache[key] = tinted
    return tinted


def get_icon(name, color, size):
    return QIcon(get_pixmap(name, color, size))
