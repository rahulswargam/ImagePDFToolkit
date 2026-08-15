import os

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QSize, Qt, Signal
from PySide6.QtGui import QFontMetrics, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ui import icons as icon_lib

MAX_BATCH_FILES = 10


def clip_to_max_files(paths, max_files=MAX_BATCH_FILES):
    """Caps a file list at max_files. Returns (clipped_paths, truncated_count)."""

    if len(paths) <= max_files:
        return paths, 0

    return paths[:max_files], len(paths) - max_files


class DropWorkspace(QFrame):
    """Large drag-and-drop workspace: icon + title + subtitle + optional format hint.

    Click anywhere to request a browse dialog (via `browseRequested`); drag
    matching files anywhere onto it to drop them (via `filesDropped`).
    """

    filesDropped = Signal(list)
    browseRequested = Signal()

    def __init__(
        self,
        extensions,
        icon_color,
        multiple=True,
        title="Drop files here",
        subtitle="Drag & drop or click to browse",
        hint="",
        parent=None,
    ):
        super().__init__(parent)

        self.extensions = tuple(extension.lower() for extension in extensions)
        self.multiple = multiple

        self.setObjectName("dropWorkspace")
        self.setAcceptDrops(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(220)
        self.setAccessibleName(f"{title} — {subtitle}")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        self._icon_label = QLabel()
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_label.setPixmap(icon_lib.get_pixmap("upload-cloud", icon_color, 40))
        self._icon_opacity = QGraphicsOpacityEffect(self._icon_label)
        self._icon_opacity.setOpacity(1.0)
        self._icon_label.setGraphicsEffect(self._icon_opacity)
        self._icon_animation = QPropertyAnimation(self._icon_opacity, b"opacity", self)
        layout.addWidget(self._icon_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self._title_label = QLabel(title)
        self._title_label.setObjectName("dropWorkspaceTitle")
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._title_label)

        self._subtitle_label = QLabel(subtitle)
        self._subtitle_label.setObjectName("dropWorkspaceSubtitle")
        self._subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._subtitle_label)

        if hint:
            hint_label = QLabel(hint)
            hint_label.setObjectName("dropWorkspaceHint")
            hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(hint_label)

        self._resting_title = title
        self._resting_subtitle = subtitle

    def set_text(self, title, subtitle=None):
        self._resting_title = title
        self._title_label.setText(title)
        if subtitle is not None:
            self._resting_subtitle = subtitle
            self._subtitle_label.setText(subtitle)

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

        if active:
            self._title_label.setText("Release to add file")
            self._subtitle_label.setText("Drop it anywhere in this area")
            self._pulse_icon()
        else:
            self._title_label.setText(self._resting_title)
            self._subtitle_label.setText(self._resting_subtitle)

    def _pulse_icon(self):
        self._icon_animation.stop()
        self._icon_animation.setDuration(260)
        self._icon_animation.setStartValue(0.2)
        self._icon_animation.setEndValue(1.0)
        self._icon_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._icon_animation.start()

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

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.browseRequested.emit()
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self.browseRequested.emit()
        else:
            super().keyPressEvent(event)


class FileGridItem(QFrame):
    """A single removable card in a FileGrid: thumbnail/type icon, name, meta, remove."""

    removed = Signal(str)

    THUMB_SIZE = 96
    CARD_WIDTH = 140

    def __init__(self, file_path, kind="file", meta_text="", parent=None):
        super().__init__(parent)

        self.file_path = file_path
        self.setObjectName("fileGridItem")
        self.setFixedWidth(self.CARD_WIDTH)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 10)
        layout.setSpacing(6)

        top_row = QHBoxLayout()
        top_row.addStretch()
        remove_button = QPushButton()
        remove_button.setObjectName("iconButton")
        remove_button.setIcon(icon_lib.get_icon("x", "#9397a8", 13))
        remove_button.setIconSize(QSize(13, 13))
        remove_button.setFixedSize(22, 22)
        remove_button.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_button.setToolTip(f"Remove {os.path.basename(file_path)}")
        remove_button.setAccessibleName(f"Remove {os.path.basename(file_path)}")
        remove_button.clicked.connect(lambda: self.removed.emit(self.file_path))
        top_row.addWidget(remove_button)
        layout.addLayout(top_row)

        thumb = QLabel()
        thumb.setObjectName("fileGridThumb")
        thumb.setFixedSize(self.THUMB_SIZE, self.THUMB_SIZE)
        thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if kind == "image":
            source = QPixmap(file_path)
            if not source.isNull():
                scaled = source.scaled(
                    self.THUMB_SIZE - 12,
                    self.THUMB_SIZE - 12,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                thumb.setPixmap(scaled)
            else:
                thumb.setPixmap(icon_lib.get_pixmap("image", "#9397a8", 32))
        else:
            icon_name = "file-text" if kind == "pdf" else "file"
            thumb.setPixmap(icon_lib.get_pixmap(icon_name, "#9397a8", 32))

        layout.addWidget(thumb, alignment=Qt.AlignmentFlag.AlignCenter)

        name_label = QLabel(self._elided_name(file_path))
        name_label.setObjectName("fileGridName")
        name_label.setToolTip(os.path.basename(file_path))
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)

        meta_label = QLabel(meta_text)
        meta_label.setObjectName("fileGridMeta")
        meta_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(meta_label)

    @staticmethod
    def _elided_name(file_path):
        name = os.path.basename(file_path)
        metrics = QFontMetrics(QLabel().font())
        return metrics.elidedText(name, Qt.TextElideMode.ElideMiddle, FileGridItem.CARD_WIDTH - 20)


class FileGrid(QWidget):
    """A responsive grid of removable FileGridItem cards.

    `kind_resolver(path) -> "image"|"pdf"|"file"` and `meta_resolver(path) -> str`
    let each page decide what thumbnail style and metadata line to show,
    keeping this widget free of any business logic.
    """

    filesChanged = Signal(list)

    ITEM_SLOT = FileGridItem.CARD_WIDTH + 12

    def __init__(self, kind_resolver, meta_resolver, parent=None):
        super().__init__(parent)

        self._paths = []
        self._kind_resolver = kind_resolver
        self._meta_resolver = meta_resolver
        self._columns = 1

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(12)

    def set_files(self, paths):
        self._paths = list(paths)
        self._rebuild()

    def paths(self):
        return list(self._paths)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        columns = max(1, self.width() // self.ITEM_SLOT)
        if columns != self._columns:
            self._columns = columns
            self._rebuild()

    def _rebuild(self):
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        columns = max(1, self._columns)
        for index, path in enumerate(self._paths):
            row, col = divmod(index, columns)
            grid_item = FileGridItem(
                path,
                kind=self._kind_resolver(path),
                meta_text=self._meta_resolver(path),
            )
            grid_item.removed.connect(self._remove_path)
            self._layout.addWidget(
                grid_item, row, col, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
            )

        self._layout.setColumnStretch(columns, 1)

    def _remove_path(self, path):
        self._paths = [p for p in self._paths if p != path]
        self._rebuild()
        self.filesChanged.emit(self._paths)
