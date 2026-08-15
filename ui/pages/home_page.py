import os
from datetime import datetime

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import activity_store
from ui import icons as icon_lib
from ui import tokens
from ui.components.workspace import DropWorkspace

_ACCENT = "#ef4444"
_ICON_MUTED = "#9397a8"

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".bmp")
PDF_EXTENSIONS = (".pdf",)

_ACTIVITY_ICONS = {
    "resize": "resize",
    "png_to_jpg": "repeat",
    "jpg_to_pdf": "layers",
    "pdf_to_jpg": "image",
    "lock": "lock",
    "unlock": "unlock",
}


def _relative_time(iso_timestamp):
    try:
        when = datetime.fromisoformat(iso_timestamp)
    except (TypeError, ValueError):
        return ""

    now = datetime.now()
    same_day = when.date() == now.date()
    time_text = when.strftime("%-I:%M %p") if os.name != "nt" else when.strftime("%I:%M %p").lstrip("0")

    if same_day:
        return f"Today {time_text}"

    yesterday = (now.date() - when.date()).days == 1
    if yesterday:
        return f"Yesterday {time_text}"

    return when.strftime("%b %-d") if os.name != "nt" else when.strftime("%b %d").replace(" 0", " ")


class QuickActionRow(QFrame):
    """A single Quick Action entry. `featured=True` renders larger with a
    description, giving Home a hierarchy instead of N identical tiles."""

    def __init__(self, icon_name, title_text, description, callback, featured=False, parent=None):
        super().__init__(parent)

        self.setObjectName("quickActionRow")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        pad = 18 if featured else 12
        layout.setContentsMargins(pad, pad, pad, pad)
        layout.setSpacing(14)

        icon_size = 26 if featured else 18
        icon_label = QLabel()
        icon_label.setPixmap(icon_lib.get_pixmap(icon_name, _ACCENT, icon_size))
        icon_label.setFixedSize(icon_size, icon_size)
        layout.addWidget(icon_label)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(3)

        title_label = QLabel(title_text)
        title_label.setObjectName("quickActionTitle")
        if featured:
            title_label.setStyleSheet(f"font-size: {tokens.FONT_SUBHEAD}px;")
        text_layout.addWidget(title_label)

        if featured and description:
            subtitle_label = QLabel(description)
            subtitle_label.setObjectName("quickActionSubtitle")
            subtitle_label.setWordWrap(True)
            text_layout.addWidget(subtitle_label)

        layout.addLayout(text_layout, 1)

        chevron = QLabel()
        chevron.setPixmap(icon_lib.get_pixmap("chevron-right", _ICON_MUTED, tokens.ICON_SM))
        layout.addWidget(chevron)

        self._callback = callback

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._callback:
            self._callback()
        super().mousePressEvent(event)


class ActivityRow(QFrame):
    def __init__(self, entry, parent=None):
        super().__init__(parent)

        self.setObjectName("activityRow")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 10, 4, 10)
        layout.setSpacing(12)

        icon_name = _ACTIVITY_ICONS.get(entry.get("kind"), "file")
        icon_label = QLabel()
        icon_label.setPixmap(icon_lib.get_pixmap(icon_name, _ICON_MUTED, tokens.ICON_MD))
        icon_label.setFixedSize(tokens.ICON_MD, tokens.ICON_MD)
        layout.addWidget(icon_label)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        name_label = QLabel(entry.get("filename", ""))
        name_label.setObjectName("activityName")
        text_layout.addWidget(name_label)

        detail_label = QLabel(entry.get("detail", ""))
        detail_label.setObjectName("activityDetail")
        text_layout.addWidget(detail_label)

        layout.addLayout(text_layout, 1)

        time_label = QLabel(_relative_time(entry.get("timestamp", "")))
        time_label.setObjectName("activityTime")
        layout.addWidget(time_label, alignment=Qt.AlignmentFlag.AlignTop)


class HomePage(QWidget):
    """Home / Tool Command Center: hero, one big drop workspace that
    auto-routes dropped files, Quick Actions, and Recent Activity."""

    def __init__(self, notify, open_tool, open_dropped_files, tools, parent=None):
        super().__init__(parent)

        self.notify = notify
        self.open_tool = open_tool
        self.open_dropped_files = open_dropped_files
        self.tools = tools

        self.setup_ui()

    def setup_ui(self):

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # =========================
        # HERO
        # =========================

        badge_wrap = QFrame()
        badge_wrap.setObjectName("heroBadge")
        badge_row = QHBoxLayout(badge_wrap)
        badge_row.setContentsMargins(10, 6, 14, 6)
        badge_row.setSpacing(6)

        badge_icon = QLabel()
        badge_icon.setPixmap(icon_lib.get_pixmap("zap", _ACCENT, 12))
        badge_row.addWidget(badge_icon)

        badge_text = QLabel("FAST · PRIVATE · OFFLINE")
        badge_text.setObjectName("heroBadgeText")
        badge_row.addWidget(badge_text)

        badge_line = QHBoxLayout()
        badge_line.addWidget(badge_wrap)
        badge_line.addStretch()
        layout.addLayout(badge_line)
        layout.addSpacing(14)

        page_title = QLabel("Image & PDF Toolkit")
        page_title.setObjectName("pageTitle")
        layout.addWidget(page_title)

        page_subtitle = QLabel("Fast, private, offline tools for your images and PDF files.")
        page_subtitle.setObjectName("pageSubtitle")
        layout.addWidget(page_subtitle)
        layout.addSpacing(22)

        # =========================
        # DROP WORKSPACE
        # =========================

        self.drop_workspace = DropWorkspace(
            IMAGE_EXTENSIONS + PDF_EXTENSIONS,
            _ACCENT,
            multiple=True,
            title="Drop a file to get started",
            subtitle="Drag & drop an image or PDF, or click to browse",
            hint="JPG · PNG · WEBP · PDF",
        )
        self.drop_workspace.filesDropped.connect(self._on_files_dropped)
        self.drop_workspace.browseRequested.connect(self._browse)
        layout.addWidget(self.drop_workspace)
        layout.addSpacing(28)

        # =========================
        # QUICK ACTIONS
        # =========================

        section = QLabel("Quick Actions")
        section.setObjectName("sectionHeading")
        layout.addWidget(section)
        layout.addSpacing(10)

        for index, (icon_name, title_text, description, page_class) in enumerate(self.tools):
            row = QuickActionRow(
                icon_name,
                title_text,
                description,
                lambda p=page_class, t=title_text, d=description: self.open_tool(p, t, d),
                featured=(index == 0),
            )
            layout.addWidget(row)
            layout.addSpacing(8)

        layout.addSpacing(20)

        # =========================
        # RECENT ACTIVITY
        # =========================

        activity_heading = QLabel("Recent Activity")
        activity_heading.setObjectName("sectionHeading")
        layout.addWidget(activity_heading)
        layout.addSpacing(10)

        recent = activity_store.get_recent(limit=8)

        if not recent:
            empty_title = QLabel("Nothing processed yet")
            empty_title.setObjectName("emptyStateTitle")
            layout.addWidget(empty_title)

            empty_subtitle = QLabel("Files you process will show up here.")
            empty_subtitle.setObjectName("emptyStateSubtitle")
            layout.addWidget(empty_subtitle)
        else:
            for entry in recent:
                layout.addWidget(ActivityRow(entry))

        layout.addStretch()

    def _browse(self):
        from PySide6.QtWidgets import QFileDialog

        extensions = " ".join(f"*{ext}" for ext in IMAGE_EXTENSIONS + PDF_EXTENSIONS)
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select a file", "", f"Supported files ({extensions})"
        )
        if paths:
            self._on_files_dropped(paths)

    def _on_files_dropped(self, paths):
        self.open_dropped_files(paths)
