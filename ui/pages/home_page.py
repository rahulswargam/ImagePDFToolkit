from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ui import icons as icon_lib
from ui.components.animation import fade_in
from ui import tokens
from ui.components.workspace import DropWorkspace

_ACCENT = "#ef4444"
_ICON_MUTED = "#9397a8"

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".bmp")
PDF_EXTENSIONS = (".pdf",)


class QuickActionRow(QFrame):
    """A single Quick Action entry. `featured=True` renders larger with a
    description, giving Home a hierarchy instead of N identical tiles."""

    def __init__(self, icon_name, title_text, description, callback, featured=False, parent=None):
        super().__init__(parent)

        self.setObjectName("quickActionRow")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName(f"Open {title_text}" + (f" — {description}" if description else ""))

        layout = QHBoxLayout(self)
        pad = 18 if featured else 12
        layout.setContentsMargins(pad, pad, pad, pad)
        layout.setSpacing(14)

        badge_size = 44 if featured else 34
        icon_size = 22 if featured else 16
        icon_badge = QLabel()
        icon_badge.setObjectName("quickActionIconBadge")
        icon_badge.setFixedSize(badge_size, badge_size)
        icon_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_badge.setPixmap(icon_lib.get_pixmap(icon_name, _ACCENT, icon_size))
        layout.addWidget(icon_badge)

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

        self._chevron = QLabel()
        self._chevron.setPixmap(icon_lib.get_pixmap("chevron-right", _ICON_MUTED, tokens.ICON_SM))
        layout.addWidget(self._chevron)

        self._callback = callback

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._callback:
            self._callback()
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space) and self._callback:
            self._callback()
        else:
            super().keyPressEvent(event)

    def enterEvent(self, event):
        self._chevron.setPixmap(icon_lib.get_pixmap("chevron-right", _ACCENT, tokens.ICON_SM))
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._chevron.setPixmap(icon_lib.get_pixmap("chevron-right", _ICON_MUTED, tokens.ICON_SM))
        super().leaveEvent(event)


class HomePage(QWidget):
    """Home / Tool Command Center: hero, one big drop workspace that
    auto-routes dropped files, and Quick Actions."""

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

        badge_line = QHBoxLayout()
        badge_line.setSpacing(8)
        badge_line.addWidget(self._build_hero_badge("zap", "FAST"))
        badge_line.addWidget(self._build_hero_badge("shield", "PRIVATE"))
        badge_line.addWidget(self._build_hero_badge("offline", "OFFLINE"))
        badge_line.addStretch()
        layout.addLayout(badge_line)
        layout.addSpacing(14)

        page_title = QLabel("Image & PDF Toolkit")
        page_title.setObjectName("pageTitle")
        fade_in(page_title)
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

        layout.addStretch()

    @staticmethod
    def _build_hero_badge(icon_name, label):
        badge = QFrame()
        badge.setObjectName("heroBadge")

        row = QHBoxLayout(badge)
        row.setContentsMargins(10, 6, 14, 6)
        row.setSpacing(6)

        icon = QLabel()
        icon.setPixmap(icon_lib.get_pixmap(icon_name, _ACCENT, 12))
        row.addWidget(icon)

        text = QLabel(label)
        text.setObjectName("heroBadgeText")
        row.addWidget(text)

        return badge

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
