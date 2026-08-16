from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen
from PySide6.QtWidgets import QWidget

_HANDLE_RADIUS = 5
_HANDLE_HIT_RADIUS = 9
_MIN_WIDTH_FRAC = 0.05
_MIN_HEIGHT_FRAC = 0.03
_ACCENT = "#ef4444"


class PdfOverlayCanvas(QWidget):
    """An interactive PDF-page preview: the target page renders as a
    static background, with a draggable, corner-resizable box on top
    representing where a signature or watermark will be placed — drag
    inside the box to move it, drag a corner to resize it, exactly like
    cropping an image.

    All geometry is exposed/accepted as fractions of the page's own
    width/height (0..1), independent of whatever pixel size this widget
    happens to be drawn at. For image overlays, corner-dragging preserves
    the image's aspect ratio (set via set_overlay_image); for text
    overlays, the box resizes freely and the text is drawn to fit it.
    """

    geometryChanged = Signal(float, float, float, float)  # x, y, w, h fractions

    def __init__(self, parent=None):
        super().__init__(parent)

        self._page_pixmap = None
        self._overlay_kind = None  # None | "image" | "text"
        self._overlay_pixmap = None
        self._overlay_text = ""
        self._overlay_font_family = None
        self._overlay_color = "#14161f"

        self._box = QRectF(0.3, 0.75, 0.4, 0.12)
        self._aspect_locked = False
        self._aspect_ratio = None

        self._drag_mode = None
        self._drag_start_pos = None
        self._drag_start_box = None

        self.setMinimumSize(240, 300)
        self.setMouseTracking(True)

    # --- content ---

    def set_page_pixmap(self, pixmap):
        self._page_pixmap = pixmap
        if pixmap and not pixmap.isNull():
            self.setFixedSize(pixmap.size())
        self.update()

    def set_overlay_image(self, pixmap):
        self._overlay_kind = "image"
        self._overlay_pixmap = pixmap
        if pixmap and not pixmap.isNull() and pixmap.width() > 0:
            self._aspect_ratio = pixmap.height() / pixmap.width()
            self._aspect_locked = True
            self._apply_aspect_lock()
        self.update()

    def set_overlay_text(self, text, font_family=None, color="#14161f"):
        self._overlay_kind = "text"
        self._overlay_text = text
        self._overlay_font_family = font_family
        self._overlay_color = color
        self._aspect_locked = False
        self.update()

    # --- geometry ---

    def set_box(self, x, y, w, h, emit=True):
        w = max(_MIN_WIDTH_FRAC, min(1.0, w))
        h = max(_MIN_HEIGHT_FRAC, min(1.0, h))
        x = max(0.0, min(1.0 - w, x))
        y = max(0.0, min(1.0 - h, y))
        self._box = QRectF(x, y, w, h)
        self.update()
        if emit:
            self.geometryChanged.emit(x, y, w, h)

    def box(self):
        return self._box.x(), self._box.y(), self._box.width(), self._box.height()

    def set_width_fraction(self, width_frac):
        """Drives the box's width from an external Size % field, keeping
        its top-left corner fixed. Height follows the aspect ratio when
        locked (image overlays); otherwise it's left unchanged."""

        x, y, _, h = self.box()
        if self._aspect_locked and self._aspect_ratio:
            h = width_frac * self._aspect_ratio
        self.set_box(x, y, width_frac, h)

    def _apply_aspect_lock(self):
        x, y, w, _ = self.box()
        self.set_box(x, y, w, w * self._aspect_ratio, emit=False)

    # --- painting ---

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self._page_pixmap and not self._page_pixmap.isNull():
            painter.drawPixmap(0, 0, self._page_pixmap)
        else:
            painter.fillRect(self.rect(), QColor("#14161f"))

        box_px = self._box_to_pixels()
        self._paint_overlay_content(painter, box_px)

        pen = QPen(QColor(_ACCENT))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(box_px)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(_ACCENT))
        for point in self._corner_points(box_px).values():
            painter.drawEllipse(point, _HANDLE_RADIUS, _HANDLE_RADIUS)

    def _paint_overlay_content(self, painter, box_px):
        if self._overlay_kind == "image" and self._overlay_pixmap and not self._overlay_pixmap.isNull():
            scaled = self._overlay_pixmap.scaled(
                max(1, int(box_px.width())),
                max(1, int(box_px.height())),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            painter.drawPixmap(box_px.topLeft().toPoint(), scaled)

        elif self._overlay_kind == "text" and self._overlay_text.strip():
            font = QFont(self._overlay_font_family) if self._overlay_font_family else QFont()
            pixel_size = max(6, int(box_px.height() * 0.6))
            font.setPixelSize(pixel_size)
            metrics = QFontMetrics(font)
            text_width = metrics.horizontalAdvance(self._overlay_text)
            if text_width > box_px.width() and text_width > 0:
                font.setPixelSize(max(6, int(pixel_size * box_px.width() / text_width)))
            painter.setFont(font)
            painter.setPen(QColor(self._overlay_color))
            painter.drawText(box_px, Qt.AlignmentFlag.AlignCenter, self._overlay_text)

    def _box_to_pixels(self):
        w, h = self.width(), self.height()
        return QRectF(self._box.x() * w, self._box.y() * h, self._box.width() * w, self._box.height() * h)

    def _corner_points(self, box_px):
        return {
            "tl": box_px.topLeft(),
            "tr": box_px.topRight(),
            "bl": box_px.bottomLeft(),
            "br": box_px.bottomRight(),
        }

    # --- mouse interaction ---

    def _handle_at(self, pos):
        box_px = self._box_to_pixels()
        for name, point in self._corner_points(box_px).items():
            if (pos - point).manhattanLength() < _HANDLE_HIT_RADIUS * 1.8:
                return name
        if box_px.contains(pos):
            return "move"
        return None

    def mousePressEvent(self, event):
        mode = self._handle_at(event.position())
        if mode:
            self._drag_mode = mode
            self._drag_start_pos = event.position()
            self._drag_start_box = QRectF(self._box)

    def mouseMoveEvent(self, event):
        pos = event.position()

        if not self._drag_mode:
            self._update_hover_cursor(pos)
            return

        w, h = max(1, self.width()), max(1, self.height())
        dx = (pos.x() - self._drag_start_pos.x()) / w
        dy = (pos.y() - self._drag_start_pos.y()) / h
        box = self._drag_start_box

        if self._drag_mode == "move":
            self.set_box(box.x() + dx, box.y() + dy, box.width(), box.height())
        elif self._aspect_locked and self._aspect_ratio:
            self._resize_aspect_locked(box, dx)
        else:
            self._resize_free(box, dx, dy)

    def _resize_aspect_locked(self, box, dx):
        if self._drag_mode == "br":
            new_w = max(_MIN_WIDTH_FRAC, box.width() + dx)
            self.set_box(box.x(), box.y(), new_w, new_w * self._aspect_ratio)
        elif self._drag_mode == "tl":
            new_w = max(_MIN_WIDTH_FRAC, box.width() - dx)
            new_h = new_w * self._aspect_ratio
            self.set_box(box.right() - new_w, box.bottom() - new_h, new_w, new_h)
        elif self._drag_mode == "tr":
            new_w = max(_MIN_WIDTH_FRAC, box.width() + dx)
            new_h = new_w * self._aspect_ratio
            self.set_box(box.left(), box.bottom() - new_h, new_w, new_h)
        elif self._drag_mode == "bl":
            new_w = max(_MIN_WIDTH_FRAC, box.width() - dx)
            new_h = new_w * self._aspect_ratio
            self.set_box(box.right() - new_w, box.top(), new_w, new_h)

    def _resize_free(self, box, dx, dy):
        if self._drag_mode == "br":
            self.set_box(box.x(), box.y(), box.width() + dx, box.height() + dy)
        elif self._drag_mode == "tl":
            self.set_box(box.x() + dx, box.y() + dy, box.width() - dx, box.height() - dy)
        elif self._drag_mode == "tr":
            self.set_box(box.x(), box.y() + dy, box.width() + dx, box.height() - dy)
        elif self._drag_mode == "bl":
            self.set_box(box.x() + dx, box.y(), box.width() - dx, box.height() + dy)

    def _update_hover_cursor(self, pos):
        mode = self._handle_at(pos)
        if mode in ("tl", "br"):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif mode in ("tr", "bl"):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif mode == "move":
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def mouseReleaseEvent(self, event):
        self._drag_mode = None
