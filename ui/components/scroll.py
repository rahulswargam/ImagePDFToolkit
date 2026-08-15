from PySide6.QtCore import QEasingCurve, QPropertyAnimation
from PySide6.QtWidgets import QScrollArea


class SmoothScrollArea(QScrollArea):
    """A QScrollArea whose mouse-wheel scrolling glides instead of jumping."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self._animation = None
        self._target = None

    def wheelEvent(self, event):
        scrollbar = self.verticalScrollBar()

        if not scrollbar.isVisible() or scrollbar.maximum() == 0:
            event.ignore()
            return

        delta = event.angleDelta().y()

        if delta == 0:
            event.ignore()
            return

        step = scrollbar.singleStep() * 6
        current = self._target if self._target is not None else scrollbar.value()
        target = current - (step if delta > 0 else -step)
        target = max(scrollbar.minimum(), min(scrollbar.maximum(), target))

        self._target = target

        if self._animation is not None:
            self._animation.stop()

        self._animation = QPropertyAnimation(scrollbar, b"value", self)
        self._animation.setDuration(260)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.setStartValue(scrollbar.value())
        self._animation.setEndValue(target)
        self._animation.finished.connect(lambda: setattr(self, "_target", None))
        self._animation.start()

        event.accept()
