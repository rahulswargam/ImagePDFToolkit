from PySide6.QtCore import QEasingCurve, QPropertyAnimation
from PySide6.QtWidgets import QGraphicsOpacityEffect


def fade_in(widget, duration=180):
    """A one-shot opacity fade-in, used as the page-transition cue when
    navigating between tools.

    Only ever call this on a LEAF widget with no descendant that already
    carries its own QGraphicsEffect (a plain QLabel is safe). This app
    already hit a real, confirmed Qt bug where stacking QGraphicsOpacityEffect
    in an ancestor/descendant chain corrupts layout — AnimatedButton and
    DropWorkspace's icon each carry their own effect and appear on nearly
    every page, so fading a whole page container would re-trigger it. A
    fade on the page title alone (no children) sidesteps that entirely.
    """

    effect = QGraphicsOpacityEffect(widget)
    effect.setOpacity(0.0)
    widget.setGraphicsEffect(effect)

    animation = QPropertyAnimation(effect, b"opacity", widget)
    animation.setDuration(duration)
    animation.setStartValue(0.0)
    animation.setEndValue(1.0)
    animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
