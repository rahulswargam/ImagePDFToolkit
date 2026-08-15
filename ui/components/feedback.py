from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer, Signal
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


class SuccessPanel(QFrame):
    """Inline success confirmation: check icon, title, detail, Open Folder / Done."""

    doneClicked = Signal()
    openFolderClicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("successPanel")
        self.hide()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setSpacing(10)

        icon_badge = QLabel()
        icon_badge.setObjectName("successIcon")
        icon_badge.setFixedSize(26, 26)
        icon_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_badge.setPixmap(icon_lib.get_pixmap("check", "#ffffff", 15))
        header.addWidget(icon_badge)

        self._title_label = QLabel("")
        self._title_label.setObjectName("panelTitle")
        header.addWidget(self._title_label)
        header.addStretch()
        layout.addLayout(header)

        self._detail_label = QLabel("")
        self._detail_label.setObjectName("panelDetail")
        self._detail_label.setWordWrap(True)
        layout.addWidget(self._detail_label)

        button_row = QHBoxLayout()
        button_row.setSpacing(10)

        self._open_button = AnimatedButton("Open Folder")
        self._open_button.setObjectName("secondaryButton")
        self._open_button.clicked.connect(self.openFolderClicked.emit)

        done_button = AnimatedButton("Done")
        done_button.setObjectName("toolButton")
        done_button.clicked.connect(self._on_done)

        button_row.addWidget(self._open_button)
        button_row.addWidget(done_button)
        button_row.addStretch()
        layout.addLayout(button_row)

    def show_success(self, title, detail):
        self._title_label.setText(title)
        self._detail_label.setText(detail)
        self.show()

    def _on_done(self):
        self.hide()
        self.doneClicked.emit()


class Modal(QDialog):
    """A themed replacement for QMessageBox, used for error/warning summaries."""

    def __init__(self, title, message, kind="error", parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setModal(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(380)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("modalCard")
        outer.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()
        header.setSpacing(10)

        icon_name = "check" if kind == "success" else "alert-triangle"
        icon_color = "#16a34a" if kind == "success" else "#f97316"
        icon_label = QLabel()
        icon_label.setPixmap(icon_lib.get_pixmap(icon_name, icon_color, 22))
        header.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setObjectName("panelTitle")
        header.addWidget(title_label)
        header.addStretch()
        layout.addLayout(header)

        message_label = QLabel(message)
        message_label.setObjectName("panelDetail")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        close_button = AnimatedButton("OK")
        close_button.setObjectName("toolButton")
        close_button.clicked.connect(self.accept)

        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addWidget(close_button)
        layout.addLayout(button_row)

    @staticmethod
    def warn(parent, title, message):
        Modal(title, message, kind="error", parent=parent).exec()

    @staticmethod
    def info(parent, title, message):
        Modal(title, message, kind="success", parent=parent).exec()
