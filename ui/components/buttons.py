from PySide6.QtCore import QEasingCurve, QPropertyAnimation
from PySide6.QtWidgets import QGraphicsOpacityEffect, QProgressBar, QPushButton


class AnimatedButton(QPushButton):
    """A QPushButton with a subtle press/release opacity dip, plus a processing state."""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)

        self._idle_text = text

        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity_effect)

        self._animation = QPropertyAnimation(self._opacity_effect, b"opacity", self)

    def mousePressEvent(self, event):
        if self.isEnabled():
            self._animate_to(0.72, 90)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.isEnabled():
            self._animate_to(1.0, 150)
        super().mouseReleaseEvent(event)

    def _animate_to(self, value, duration):
        self._animation.stop()
        self._animation.setDuration(duration)
        self._animation.setStartValue(self._opacity_effect.opacity())
        self._animation.setEndValue(value)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.start()

    def set_processing(self, processing, processing_text="Working…"):
        """Swaps to a disabled/processing label, or restores the original text."""

        if processing:
            self.setEnabled(False)
            self.setText(processing_text)
        else:
            self.setEnabled(True)
            self.setText(self._idle_text)


class ProcessingBar(QProgressBar):
    """A thin indeterminate progress bar shown alongside a button's processing state."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 0)
        self.setTextVisible(False)
        self.setFixedHeight(6)
        self.hide()
