from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

ICON_BADGE_SIZE = 52


class AnimatedButton(QPushButton):
    """A QPushButton with a subtle press/release opacity dip for tactile feedback."""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)

        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity_effect)

        self._animation = QPropertyAnimation(self._opacity_effect, b"opacity", self)

    def mousePressEvent(self, event):
        self._animate_to(0.72, 90)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._animate_to(1.0, 150)
        super().mouseReleaseEvent(event)

    def _animate_to(self, value, duration):
        self._animation.stop()
        self._animation.setDuration(duration)
        self._animation.setStartValue(self._opacity_effect.opacity())
        self._animation.setEndValue(value)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.start()


class RevealButton(QPushButton):
    """Press-and-hold to show the plaintext of the given password field(s); release to mask again."""

    def __init__(self, fields, parent=None):
        super().__init__("Show", parent)

        self.fields = list(fields) if isinstance(fields, (list, tuple)) else [fields]

        self.setObjectName("revealButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.pressed.connect(self._reveal)
        self.released.connect(self._mask)

    def _reveal(self):
        for field in self.fields:
            field.setEchoMode(QLineEdit.EchoMode.Normal)

    def _mask(self):
        for field in self.fields:
            field.setEchoMode(QLineEdit.EchoMode.Password)


class ToolCard(QFrame):

    def __init__(self, icon_path, title, description, callback=None):
        super().__init__()

        self.setObjectName("toolCard")
        self.setMinimumHeight(165)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(8)

        icon_label = QLabel()
        icon_label.setFixedSize(ICON_BADGE_SIZE, ICON_BADGE_SIZE)
        pixmap = QPixmap(icon_path).scaled(
            ICON_BADGE_SIZE,
            ICON_BADGE_SIZE,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        icon_label.setPixmap(pixmap)

        title_label = QLabel(title)
        title_label.setObjectName("toolTitle")

        description_label = QLabel(description)
        description_label.setObjectName("toolDescription")
        description_label.setWordWrap(True)

        button = AnimatedButton("Open Tool")
        button.setObjectName("toolButton")
        button.setCursor(Qt.CursorShape.PointingHandCursor)

        if callback:
            button.clicked.connect(callback)

        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addStretch()
        layout.addWidget(button)


class DropArea(QLabel):
    """A preview/drop target that accepts drag-and-drop of matching files."""

    filesDropped = Signal(list)

    def __init__(self, extensions, multiple=False, placeholder="Drop file here", parent=None):
        super().__init__(parent)

        self.extensions = tuple(extension.lower() for extension in extensions)
        self.multiple = multiple
        self.placeholder = placeholder

        self.setObjectName("previewFrame")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setScaledContents(False)
        self.setWordWrap(True)
        self.setText(placeholder)
        self.setAcceptDrops(True)

    def reset(self):
        self.setPixmap(self.pixmap().__class__())
        self.setText(self.placeholder)

    def _matching_paths(self, event):
        if not event.mimeData().hasUrls():
            return []

        return [
            url.toLocalFile()
            for url in event.mimeData().urls()
            if url.toLocalFile().lower().endswith(self.extensions)
        ]

    def _set_drag_active(self, active):
        self.setProperty("dragActive", active)
        self.style().unpolish(self)
        self.style().polish(self)

    def dragEnterEvent(self, event):
        if self._matching_paths(event):
            self._set_drag_active(True)
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self._set_drag_active(False)

    def dropEvent(self, event):
        paths = self._matching_paths(event)
        self._set_drag_active(False)

        if not paths:
            event.ignore()
            return

        if not self.multiple:
            paths = paths[:1]

        self.filesDropped.emit(paths)
        event.acceptProposedAction()


class Toast(QFrame):
    """A small, non-blocking notification that fades in, then auto-dismisses."""

    def __init__(self, parent):
        super().__init__(parent)

        self.setObjectName("toast")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(10)

        self.icon_label = QLabel()
        self.icon_label.setObjectName("toastIcon")

        self.message_label = QLabel()
        self.message_label.setObjectName("toastMessage")
        self.message_label.setWordWrap(True)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.message_label)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self.opacity_effect)

        self.setMaximumWidth(380)
        self.hide()

        self._animation = None

        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self._fade_out)

    def show_message(self, message, kind="success", duration_ms=3200):
        icon = "✓" if kind == "success" else "⚠"

        self.setProperty("kind", kind)
        self.style().unpolish(self)
        self.style().polish(self)

        self.icon_label.setText(icon)
        self.message_label.setText(message)

        self.adjustSize()
        self._reposition()
        self.show()
        self.raise_()

        self._animate(0.0, 1.0, 220, QEasingCurve.Type.OutCubic)
        self._hide_timer.start(duration_ms)

    def _reposition(self):
        parent = self.parentWidget()
        if not parent:
            return

        x = (parent.width() - self.width()) // 2
        y = parent.height() - self.height() - 30
        self.move(max(12, x), max(12, y))

    def _animate(self, start, end, duration, easing):
        self._animation = QPropertyAnimation(self.opacity_effect, b"opacity", self)
        self._animation.setDuration(duration)
        self._animation.setStartValue(start)
        self._animation.setEndValue(end)
        self._animation.setEasingCurve(easing)
        self._animation.start()

    def _fade_out(self):
        self._animation = QPropertyAnimation(self.opacity_effect, b"opacity", self)
        self._animation.setDuration(280)
        self._animation.setStartValue(1.0)
        self._animation.setEndValue(0.0)
        self._animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self._animation.finished.connect(self.hide)
        self._animation.start()
