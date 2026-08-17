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
from ui.components.workspace import MAX_BATCH_FILES, DropWorkspace, FileGrid, clip_to_max_files
from ui.pages.image_resizer_page import ImageResizerPage
from ui.pages.jpg_to_pdf_page import JpgToPdfPage
from ui.pages.lock_pdf_page import LockPdfPage
from ui.pages.pdf_forms_page import PdfFormsPage
from ui.pages.png_to_jpg_page import PngToJpgPage
from ui.pages.remove_pages_page import RemovePagesPage
from ui.pages.rotate_pdf_page import RotatePdfPage
from ui.pages.sign_pdf_page import SignPdfPage
from ui.pages.unlock_pdf_page import UnlockPdfPage
from ui.pages.watermark_page import WatermarkPage
from tools.image_resizer import format_file_size

_ACCENT = "#ef4444"
_ICON_MUTED = "#9397a8"


def _display_name(section_name):
    """Title-cases a sidebar section label for Home's headings, without
    mangling "PDF" into "Pdf" the way str.title() would."""

    return " ".join(word if word == "PDF" else word.capitalize() for word in section_name.split())

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".bmp")
PDF_EXTENSIONS = (".pdf",)
DROPPABLE_EXTENSIONS = IMAGE_EXTENSIONS + PDF_EXTENSIONS

# Every tool not listed here is assumed to take a PDF (true for the large
# majority — organize/edit/security tools). Only the tools that take
# something other than a PDF need an entry.
_NON_PDF_TOOL_EXTENSIONS = {
    ImageResizerPage: IMAGE_EXTENSIONS,
    PngToJpgPage: (".png",),
    JpgToPdfPage: IMAGE_EXTENSIONS,
}


def _tool_extensions(page_class):
    return _NON_PDF_TOOL_EXTENSIONS.get(page_class, PDF_EXTENSIONS)


# Tools only suggested from Home when exactly one file is selected — either
# because the page genuinely only accepts one file (DropWorkspace(multiple=False):
# Lock/Unlock/Sign/Watermark PDF, PDF Forms, PNG -> JPG), or because a single
# setting (page range, rotation direction) applying identically across several
# unrelated PDFs at once isn't a sensible batch action from this entry point
# (Rotate PDF, Remove Pages).
_SINGLE_FILE_ONLY_TOOLS = {
    LockPdfPage,
    UnlockPdfPage,
    SignPdfPage,
    WatermarkPage,
    PdfFormsPage,
    PngToJpgPage,
    RotatePdfPage,
    RemovePagesPage,
}


def _file_kind(path):
    extension = os.path.splitext(path)[1].lower()
    if extension in IMAGE_EXTENSIONS:
        return "image"
    if extension in PDF_EXTENSIONS:
        return "pdf"
    return "file"


def _file_family(path):
    """Coarse image-vs-pdf grouping used to keep a dropped batch consistent —
    once one type is on the bench, files of the other type get rejected
    rather than silently mixed in with tools that only understand one kind."""

    extension = os.path.splitext(path)[1].lower()
    return "image" if extension in IMAGE_EXTENSIONS else "pdf"


def _file_meta(path):
    try:
        return format_file_size(os.path.getsize(path))
    except OSError:
        return ""


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
        self._dropped_paths = []

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
            subtitle="Drag & drop an image or PDF, or click to browse",
            hint="JPG · PNG · WEBP · PDF",
        )
        self.drop_workspace.filesDropped.connect(self._on_files_dropped)
        self.drop_workspace.browseRequested.connect(self._browse)
        layout.addWidget(self.drop_workspace)
        layout.addSpacing(14)

        # =========================
        # SELECTED FILES (populated after a file is dropped)
        # =========================

        self.file_grid = FileGrid(_file_kind, _file_meta)
        self.file_grid.filesChanged.connect(self._on_file_grid_changed)
        self.file_grid.hide()
        layout.addWidget(self.file_grid)
        layout.addSpacing(18)

        # =========================
        # SUGGESTED TOOLS (populated after a file is dropped)
        # =========================

        self.suggestions_card = QFrame()
        self.suggestions_card.setObjectName("toolCard")

        suggestions_card_layout = QVBoxLayout(self.suggestions_card)
        suggestions_card_layout.setContentsMargins(20, 18, 20, 18)
        suggestions_card_layout.setSpacing(14)

        self.suggestions_heading = QLabel("")
        self.suggestions_heading.setObjectName("toolTitle")
        suggestions_card_layout.addWidget(self.suggestions_heading)

        self.suggestions_grid_container = QWidget()
        self.suggestions_grid = QGridLayout(self.suggestions_grid_container)
        self.suggestions_grid.setContentsMargins(0, 0, 0, 0)
        self.suggestions_grid.setHorizontalSpacing(12)
        self.suggestions_grid.setVerticalSpacing(8)
        self.suggestions_grid.setColumnStretch(0, 1)
        self.suggestions_grid.setColumnStretch(1, 1)
        suggestions_card_layout.addWidget(self.suggestions_grid_container)

        self.suggestions_card.hide()
        layout.addWidget(self.suggestions_card)
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
            self, "Select files", "", f"Supported files ({extensions})"
        )
        if paths:
            self._on_files_dropped(paths)

    def _on_files_dropped(self, paths):

        if not paths:
            return

        # Establish the type family from whatever's already selected, or —
        # on a first drop — from the first file of this very batch, so even
        # a mixed batch dropped all at once settles on one consistent type.
        established_family = _file_family(self._dropped_paths[0] if self._dropped_paths else paths[0])
        accepted = [p for p in paths if _file_family(p) == established_family]
        rejected_count = len(paths) - len(accepted)

        combined, truncated = clip_to_max_files(list(self._dropped_paths) + accepted)
        self._dropped_paths = combined
        self._refresh_files()

        if rejected_count and truncated:
            self._warn(
                "Some Files Skipped",
                f"{rejected_count} file(s) were skipped because you already have "
                f"{'images' if established_family == 'image' else 'PDFs'} selected, and "
                f"only the first {MAX_BATCH_FILES} of the rest were kept "
                f"({truncated} extra file(s) were not added).",
            )
        elif rejected_count:
            plural = "file was" if rejected_count == 1 else "files were"
            self._warn(
                "Different File Type",
                f"{rejected_count} {plural} skipped because you already have "
                f"{'images' if established_family == 'image' else 'PDFs'} selected. "
                "Remove them first if you want to switch to a different file type.",
            )
        elif truncated:
            self._warn(
                "Too Many Files",
                f"Only the first {MAX_BATCH_FILES} files were kept "
                f"({truncated} extra file(s) were not added).",
            )

    def _warn(self, title, message):
        from ui.components.feedback import CompletionDialog

        CompletionDialog.warn(self, title, message)

    def _on_file_grid_changed(self, paths):
        self._dropped_paths = paths
        self._refresh_files()

    def _refresh_files(self):

        paths = self._dropped_paths

        if not paths:
            self.file_grid.hide()
            self.drop_workspace.set_text(
                "Drop a file to get started",
                "Drag & drop an image or PDF, or click to browse",
            )
            self._update_suggestions()
            return

        self.file_grid.set_files(paths)
        self.file_grid.show()

        plural = "file" if len(paths) == 1 else "files"
        self.drop_workspace.set_text(f"{len(paths)} {plural} ready", "Drop more files or click to add")

        self._update_suggestions()

    def _update_suggestions(self):

        while self.suggestions_grid.count():
            item = self.suggestions_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        paths = self._dropped_paths

        if not paths:
            self.suggestions_card.hide()
            return

        extension = os.path.splitext(paths[0])[1].lower()
        matches = [tool for tool in self._all_tools if extension in _tool_extensions(tool[3])]

        if len(paths) > 1:
            matches = [tool for tool in matches if tool[3] not in _SINGLE_FILE_ONLY_TOOLS]

        if not matches:
            self.suggestions_card.hide()
            return

        plural = "file" if len(paths) == 1 else "files"
        self.suggestions_heading.setText(f"What would you like to do with your {plural}?")

        for index, (icon_name, title_text, description, page_class) in enumerate(matches):
            row = QuickActionRow(
                icon_name,
                title_text,
                description,
                lambda p=page_class, t=title_text, d=description: self.open_tool(p, t, d, initial_paths=paths),
            )
            grid_row, grid_col = divmod(index, 2)
            self.suggestions_grid.addWidget(row, grid_row, grid_col)

        self.suggestions_card.show()
