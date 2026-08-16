import math

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen, QTransform
from PySide6.QtWidgets import QWidget

_HANDLE_RADIUS = 5
_HANDLE_HIT_RADIUS = 9
_ROTATE_HANDLE_OFFSET = 28
_MIN_WIDTH_FRAC = 0.05
_MIN_HEIGHT_FRAC = 0.03
_ACCENT = "#ef4444"


class PdfOverlayCanvas(QWidget):
    """An interactive PDF-page preview: the target page renders as a
    static background, with a draggable, corner-resizable box on top
    representing where a signature or watermark will be placed — drag
    inside the box to move it, drag a corner to resize it, exactly like
    cropping an image. When rotation is enabled, a handle above the box
    lets you drag to rotate it around its own center.

    All geometry is exposed/accepted as fractions of the page's own
    width/height (0..1), independent of whatever pixel size this widget
    happens to be drawn at. For image overlays, corner-dragging preserves
    the image's aspect ratio (set via set_overlay_image); for text
    overlays, the box resizes freely and the text is drawn to fit it.
    Resizing and hit-testing both operate in the box's own (rotated)
    local frame, so a rotated box still resizes along its own edges.
    """

    geometryChanged = Signal(float, float, float, float)  # x, y, w, h fractions
    rotationChanged = Signal(float)  # degrees, 0-359

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

        self._rotation = 0.0
        self._rotation_enabled = False

        self._drag_mode = None
        self._drag_start_pos = None
        self._drag_start_box = None
        self._drag_start_rotation = 0.0
        self._drag_center_px = None

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

    # --- rotation ---

    def set_rotation_enabled(self, enabled):
        self._rotation_enabled = enabled
        self.update()

    def set_rotation(self, degrees, emit=True):
        self._rotation = float(degrees) % 360
        self.update()
        if emit:
            self.rotationChanged.emit(self._rotation)

    def rotation(self):
        return self._rotation

    # --- painting ---

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self._page_pixmap and not self._page_pixmap.isNull():
            painter.drawPixmap(0, 0, self._page_pixmap)
        else:
            painter.fillRect(self.rect(), QColor("#14161f"))

        box_px = self._box_to_pixels()
        center = box_px.center()

        painter.save()
        if self._rotation:
            painter.translate(center)
            painter.rotate(self._rotation)
            painter.translate(-center)

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

        if self._rotation_enabled:
            handle_point = self._rotation_handle_point(box_px)
            stem_pen = QPen(QColor(_ACCENT))
            stem_pen.setWidth(1)
            painter.setPen(stem_pen)
            painter.drawLine(QPointF(center.x(), box_px.top()), handle_point)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(_ACCENT))
            painter.drawEllipse(handle_point, _HANDLE_RADIUS, _HANDLE_RADIUS)

        painter.restore()

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

    def _rotation_handle_point(self, box_px):
        return QPointF(box_px.center().x(), box_px.top() - _ROTATE_HANDLE_OFFSET)

    @staticmethod
    def _rotate_point(point, center, degrees):
        if not degrees:
            return QPointF(point)
        transform = QTransform()
        transform.translate(center.x(), center.y())
        transform.rotate(degrees)
        transform.translate(-center.x(), -center.y())
        return transform.map(point)

    # --- mouse interaction ---

    def _corner_or_move_at(self, local_pos, box_px):
        for name, point in self._corner_points(box_px).items():
            if (local_pos - point).manhattanLength() < _HANDLE_HIT_RADIUS * 1.8:
                return name
        if box_px.contains(local_pos):
            return "move"
        return None

    def mousePressEvent(self, event):
        box_px = self._box_to_pixels()
        center = box_px.center()
        pos = event.position()
        local_pos = self._rotate_point(pos, center, -self._rotation)

        if self._rotation_enabled:
            handle_point = self._rotation_handle_point(box_px)
            if (local_pos - handle_point).manhattanLength() < _HANDLE_HIT_RADIUS * 2:
                self._drag_mode = "rotate"
                self._drag_start_pos = pos
                self._drag_start_box = QRectF(self._box)
                self._drag_start_rotation = self._rotation
                self._drag_center_px = center
                return

        mode = self._corner_or_move_at(local_pos, box_px)
        if mode:
            self._drag_mode = mode
            self._drag_start_pos = local_pos
            self._drag_start_box = QRectF(self._box)
            self._drag_start_rotation = self._rotation
            self._drag_center_px = center

    def mouseMoveEvent(self, event):
        pos = event.position()

        if not self._drag_mode:
            self._update_hover_cursor(pos)
            return

        if self._drag_mode == "rotate":
            self._handle_rotate_drag(pos)
            return

        local_pos = self._rotate_point(pos, self._drag_center_px, -self._drag_start_rotation)
        w, h = max(1, self.width()), max(1, self.height())
        dx = (local_pos.x() - self._drag_start_pos.x()) / w
        dy = (local_pos.y() - self._drag_start_pos.y()) / h
        box = self._drag_start_box

        if self._drag_mode == "move":
            self.set_box(box.x() + dx, box.y() + dy, box.width(), box.height())
        elif self._aspect_locked and self._aspect_ratio:
            self._resize_aspect_locked(box, dx)
        else:
            self._resize_free(box, dx, dy)

    def _handle_rotate_drag(self, pos):
        center = self._drag_center_px
        start_angle = math.degrees(
            math.atan2(self._drag_start_pos.y() - center.y(), self._drag_start_pos.x() - center.x())
        )
        current_angle = math.degrees(math.atan2(pos.y() - center.y(), pos.x() - center.x()))
        self.set_rotation(round(self._drag_start_rotation + (current_angle - start_angle)))

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
        box_px = self._box_to_pixels()
        center = box_px.center()
        local_pos = self._rotate_point(pos, center, -self._rotation)

        if self._rotation_enabled:
            handle_point = self._rotation_handle_point(box_px)
            if (local_pos - handle_point).manhattanLength() < _HANDLE_HIT_RADIUS * 2:
                self.setCursor(Qt.CursorShape.CrossCursor)
                return

        mode = self._corner_or_move_at(local_pos, box_px)
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
