from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from ui import icons as icon_lib

_ICON_MUTED = "#9397a8"


class SliderInput(QWidget):
    """A labeled QSlider with a live numeric readout (e.g. "Target Size  200 KB")."""

    valueChanged = Signal(int)

    def __init__(self, label, minimum, maximum, value, suffix="", parent=None):
        super().__init__(parent)

        self._suffix = suffix

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        label_row = QHBoxLayout()
        label_widget = QLabel(label)
        label_widget.setObjectName("fieldLabel")
        self._value_label = QLabel(f"{value}{suffix}")
        self._value_label.setObjectName("fieldLabel")
        label_row.addWidget(label_widget)
        label_row.addStretch()
        label_row.addWidget(self._value_label)
        layout.addLayout(label_row)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(minimum, maximum)
        self.slider.setValue(value)
        self.slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self.slider)

    def _on_slider_changed(self, value):
        self._value_label.setText(f"{value}{self._suffix}")
        self.valueChanged.emit(value)

    def value(self):
        return self.slider.value()

    def setValue(self, value):
        self.slider.setValue(value)


class PasswordField(QWidget):
    """A password QLineEdit with a click-to-toggle visibility icon, and an
    optional simple length-based strength meter for new-password fields."""

    def __init__(self, placeholder="Password", show_strength=False, parent=None):
        super().__init__(parent)

        self._revealed = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        row = QHBoxLayout()
        row.setSpacing(6)

        self.edit = QLineEdit()
        self.edit.setPlaceholderText(placeholder)
        self.edit.setEchoMode(QLineEdit.EchoMode.Password)
        row.addWidget(self.edit)

        self._toggle = QPushButton()
        self._toggle.setObjectName("iconButton")
        self._toggle.setFixedSize(38, 38)
        self._toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle.setIconSize(QSize(18, 18))
        self._toggle.setIcon(icon_lib.get_icon("eye", _ICON_MUTED, 18))
        self._toggle.clicked.connect(self._toggle_reveal)
        row.addWidget(self._toggle)

        layout.addLayout(row)

        self._segments = []
        self._strength_label = None
        if show_strength:
            self._build_strength_row(layout)
            self.edit.textChanged.connect(self._update_strength)

    def _toggle_reveal(self):
        self._revealed = not self._revealed
        self.edit.setEchoMode(
            QLineEdit.EchoMode.Normal if self._revealed else QLineEdit.EchoMode.Password
        )
        icon_name = "eye-off" if self._revealed else "eye"
        self._toggle.setIcon(icon_lib.get_icon(icon_name, _ICON_MUTED, 18))

    def text(self):
        return self.edit.text()

    def clear(self):
        self.edit.clear()
        self._revealed = False
        self.edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._toggle.setIcon(icon_lib.get_icon("eye", _ICON_MUTED, 18))

    def _build_strength_row(self, layout):
        segments_row = QHBoxLayout()
        segments_row.setSpacing(4)
        for _ in range(4):
            segment = QFrame()
            segment.setObjectName("strengthSegment")
            segment.setFixedHeight(4)
            segments_row.addWidget(segment)
            self._segments.append(segment)
        layout.addLayout(segments_row)

        self._strength_label = QLabel("")
        self._strength_label.setObjectName("strengthLabel")
        layout.addWidget(self._strength_label)

    def _update_strength(self, text):
        length = len(text)

        if length == 0:
            level, filled, label_text = None, 0, ""
        elif length < 6:
            level, filled, label_text = "weak", 1, "Weak"
        elif length < 10:
            level, filled, label_text = "medium", 2, "Fair"
        elif length < 14:
            level, filled, label_text = "medium", 3, "Good"
        else:
            level, filled, label_text = "strong", 4, "Strong"

        for index, segment in enumerate(self._segments):
            segment.setProperty("level", level if index < filled else None)
            segment.style().unpolish(segment)
            segment.style().polish(segment)

        self._strength_label.setText(label_text)


class SegmentedControl(QWidget):
    """A pill-shaped multi-option toggle, e.g. System / Light / Dark."""

    currentChanged = Signal(int)

    def __init__(self, options, current_index=0, parent=None):
        super().__init__(parent)

        track = QFrame()
        track.setObjectName("segmentTrack")
        track_layout = QHBoxLayout(track)
        track_layout.setContentsMargins(3, 3, 3, 3)
        track_layout.setSpacing(3)

        self._buttons = []
        for index, label in enumerate(options):
            button = QPushButton(label)
            button.setObjectName("segmentOption")
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda checked=False, i=index: self._select(i))
            track_layout.addWidget(button)
            self._buttons.append(button)

        if self._buttons:
            self._buttons[current_index].setChecked(True)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(track)

    def _select(self, index):
        for i, button in enumerate(self._buttons):
            button.setChecked(i == index)
        self.currentChanged.emit(index)
