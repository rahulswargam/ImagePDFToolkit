import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ui import icons as icon_lib
from ui.components.animation import fade_in
from ui import tokens
from ui.components.workspace import DropWorkspace
from ui.pages.excel_to_pdf_page import ExcelToPdfPage
from ui.pages.html_to_pdf_page import HtmlToPdfPage
from ui.pages.image_resizer_page import ImageResizerPage
from ui.pages.jpg_to_pdf_page import JpgToPdfPage
from ui.pages.png_to_jpg_page import PngToJpgPage
from ui.pages.powerpoint_to_pdf_page import PowerpointToPdfPage
from ui.pages.word_to_pdf_page import WordToPdfPage

_ACCENT = "#ef4444"
_ICON_MUTED = "#9397a8"


def _display_name(section_name):
    """Title-cases a sidebar section label for Home's headings, without
    mangling "PDF" into "Pdf" the way str.title() would."""

    return " ".join(word if word == "PDF" else word.capitalize() for word in section_name.split())

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".bmp")
PDF_EXTENSIONS = (".pdf",)
OFFICE_EXTENSIONS = (".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".html", ".htm")
DROPPABLE_EXTENSIONS = IMAGE_EXTENSIONS + PDF_EXTENSIONS + OFFICE_EXTENSIONS

# Every tool not listed here is assumed to take a PDF (true for the large
# majority — organize/optimize/edit/security tools, plus PDF-> conversions).
# Only the tools that take something other than a PDF need an entry.
_NON_PDF_TOOL_EXTENSIONS = {
    ImageResizerPage: IMAGE_EXTENSIONS,
    PngToJpgPage: (".png",),
    JpgToPdfPage: IMAGE_EXTENSIONS,
    WordToPdfPage: (".docx", ".doc"),
    ExcelToPdfPage: (".xlsx", ".xls"),
    PowerpointToPdfPage: (".pptx", ".ppt"),
    HtmlToPdfPage: (".html", ".htm"),
}


def _tool_extensions(page_class):
    return _NON_PDF_TOOL_EXTENSIONS.get(page_class, PDF_EXTENSIONS)


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
    auto-routes dropped files, and a categorized tool grid.

    `sections` is a list of (category_name, tools) pairs, where each
    `tools` entry is (icon_name, title, description, page_class) — the
    same shape used to build the sidebar, so Home mirrors it exactly.
    """

    def __init__(self, notify, open_tool, sections, parent=None):
        super().__init__(parent)

        self.notify = notify
        self.open_tool = open_tool
        self.sections = sections
        self._all_tools = [tool for _section_name, tools in sections for tool in tools]

        self.setup_ui()

    def setup_ui(self):

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # =========================
        # HERO
        # =========================

        page_title = QLabel("FileForge Toolkit")
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
            DROPPABLE_EXTENSIONS,
            _ACCENT,
            multiple=True,
            title="Drop a file to get started",
            subtitle="Drag & drop an image, PDF, or document, or click to browse",
            hint="JPG · PNG · WEBP · PDF · DOCX · XLSX · PPTX · HTML",
        )
        self.drop_workspace.filesDropped.connect(self._on_files_dropped)
        self.drop_workspace.browseRequested.connect(self._browse)
        layout.addWidget(self.drop_workspace)
        layout.addSpacing(18)

        # =========================
        # SUGGESTED TOOLS (populated after a file is dropped)
        # =========================

        self.suggestions_heading = QLabel("")
        self.suggestions_heading.setObjectName("sectionHeading")
        self.suggestions_heading.hide()
        layout.addWidget(self.suggestions_heading)
        layout.addSpacing(10)

        self.suggestions_container = QWidget()
        self.suggestions_grid = QGridLayout(self.suggestions_container)
        self.suggestions_grid.setHorizontalSpacing(12)
        self.suggestions_grid.setVerticalSpacing(8)
        self.suggestions_grid.setColumnStretch(0, 1)
        self.suggestions_grid.setColumnStretch(1, 1)
        self.suggestions_container.hide()
        layout.addWidget(self.suggestions_container)
        layout.addSpacing(22)

        # =========================
        # TOOL CATEGORIES
        # =========================

        for section_name, tools in self.sections:

            heading = QLabel(_display_name(section_name))
            heading.setObjectName("sectionHeading")
            layout.addWidget(heading)
            layout.addSpacing(10)

            grid = QGridLayout()
            grid.setHorizontalSpacing(12)
            grid.setVerticalSpacing(8)
            grid.setColumnStretch(0, 1)
            grid.setColumnStretch(1, 1)

            for index, (icon_name, title_text, description, page_class) in enumerate(tools):
                row = QuickActionRow(
                    icon_name,
                    title_text,
                    description,
                    lambda p=page_class, t=title_text, d=description: self.open_tool(p, t, d),
                )
                grid_row, grid_col = divmod(index, 2)
                grid.addWidget(row, grid_row, grid_col)

            layout.addLayout(grid)
            layout.addSpacing(22)

        layout.addStretch()

    def _browse(self):
        from PySide6.QtWidgets import QFileDialog

        extensions = " ".join(f"*{ext}" for ext in DROPPABLE_EXTENSIONS)
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select a file", "", f"Supported files ({extensions})"
        )
        if paths:
            self._on_files_dropped(paths)

    def _on_files_dropped(self, paths):

        while self.suggestions_grid.count():
            item = self.suggestions_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not paths:
            self.suggestions_heading.hide()
            self.suggestions_container.hide()
            return

        extension = os.path.splitext(paths[0])[1].lower()
        matches = [tool for tool in self._all_tools if extension in _tool_extensions(tool[3])]

        if not matches:
            self.suggestions_heading.hide()
            self.suggestions_container.hide()
            return

        plural = "file" if len(paths) == 1 else "files"
        self.suggestions_heading.setText(f"What would you like to do with your {plural}?")
        self.suggestions_heading.show()

        for index, (icon_name, title_text, description, page_class) in enumerate(matches):
            row = QuickActionRow(
                icon_name,
                title_text,
                description,
                lambda p=page_class, t=title_text, d=description: self.open_tool(p, t, d, initial_paths=paths),
            )
            grid_row, grid_col = divmod(index, 2)
            self.suggestions_grid.addWidget(row, grid_row, grid_col)

        self.suggestions_container.show()
