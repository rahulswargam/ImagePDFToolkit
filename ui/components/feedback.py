from PySide6.QtCore import QEasingCurve, QParallelAnimationGroup, QPropertyAnimation, QRect, Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
)

from ui import icons as icon_lib
from ui.components.buttons import AnimatedButton


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


_KIND_ICON = {
    "success": ("check", "#ffffff", "#16a34a"),
    "error": ("x", "#ffffff", "#f97316"),
    "warning": ("alert-triangle", "#ffffff", "#f97316"),
    "info": ("check", "#ffffff", "#565c6d"),
}


class CompletionDialog(QDialog):
    """The single global result surface for every tool: success, error, warning,
    or info. Replaces both the old inline SuccessPanel and ad-hoc QMessageBox use.

    A big centered icon badge, a short title, a short human-readable summary
    (never a filesystem path), a primary OK button, and an optional secondary
    action (e.g. Open File) that closes the dialog before running.
    """

    def __init__(self, title, message, kind="success", secondary_label=None, parent=None):
        super().__init__(parent)

        self._secondary_action = None

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setModal(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(400)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("modalCard")
        outer.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 32, 32, 26)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        icon_name, icon_color, badge_color = _KIND_ICON.get(kind, _KIND_ICON["info"])

        badge = QLabel()
        badge.setObjectName("completionBadge")
        badge.setProperty("kind", kind)
        badge.setFixedSize(56, 56)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setPixmap(icon_lib.get_pixmap(icon_name, icon_color, 26))
        layout.addWidget(badge, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(16)

        title_label = QLabel(title)
        title_label.setObjectName("completionTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        layout.addSpacing(6)

        message_label = QLabel(message)
        message_label.setObjectName("completionMessage")
        message_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        layout.addSpacing(22)

        button_row = QHBoxLayout()
        button_row.setSpacing(10)
        button_row.addStretch()

        if secondary_label:
            secondary_button = AnimatedButton(secondary_label)
            secondary_button.setObjectName("secondaryButton")
            secondary_button.clicked.connect(self._run_secondary)
            button_row.addWidget(secondary_button)

        ok_button = AnimatedButton("OK")
        ok_button.setObjectName("toolButton")
        ok_button.setMinimumWidth(96)
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        button_row.addWidget(ok_button)
        button_row.addStretch()

        layout.addLayout(button_row)

        self._card = card
        self._entrance_animation = None

    def set_secondary_action(self, callback):
        self._secondary_action = callback

    def _run_secondary(self):
        # Close the dialog before running the action: it's a frameless,
        # always-on-top modal, so if it stays open while e.g. Explorer
        # spawns, Windows' foreground-lock keeps the new window from
        # stealing focus and the dialog (this app) just stays in front —
        # looking like "Open Folder" reopened the app instead of the folder.
        self.accept()
        if self._secondary_action:
            self._secondary_action()

    def showEvent(self, event):
        super().showEvent(event)
        self._play_entrance()

    def _play_entrance(self):
        # Top-level window properties (windowOpacity, geometry) — not a
        # QGraphicsEffect, so this cannot trigger the nested-effect layout
        # corruption that AnimatedButton's own opacity effect is prone to.
        final_rect = self.geometry()
        start_rect = QRect(final_rect)
        shrink = 10
        start_rect.adjust(shrink, shrink, -shrink, -shrink)

        self.setWindowOpacity(0.0)

        opacity_anim = QPropertyAnimation(self, b"windowOpacity", self)
        opacity_anim.setDuration(160)
        opacity_anim.setStartValue(0.0)
        opacity_anim.setEndValue(1.0)
        opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        geometry_anim = QPropertyAnimation(self, b"geometry", self)
        geometry_anim.setDuration(180)
        geometry_anim.setStartValue(start_rect)
        geometry_anim.setEndValue(final_rect)
        geometry_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._entrance_animation = QParallelAnimationGroup(self)
        self._entrance_animation.addAnimation(opacity_anim)
        self._entrance_animation.addAnimation(geometry_anim)
        self._entrance_animation.start()

    @staticmethod
    def success(parent, title, message, open_file=None):
        dialog = CompletionDialog(
            title, message, kind="success",
            secondary_label="Open File" if open_file else None,
            parent=parent,
        )
        if open_file:
            dialog.set_secondary_action(open_file)
        dialog.exec()

    @staticmethod
    def error(parent, title, message):
        CompletionDialog(title, message, kind="error", parent=parent).exec()

    @staticmethod
    def warn(parent, title, message):
        CompletionDialog(title, message, kind="warning", parent=parent).exec()
