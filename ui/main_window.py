import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

import settings_store
from ui.components.animation import fade_in
from ui.components.nav import NavBreadcrumb, NavItem
from ui.components.scroll import SmoothScrollArea
from ui.components.feedback import Toast
from ui.pages.home_page import IMAGE_EXTENSIONS, HomePage
from ui.pages.compare_pdf_page import ComparePdfPage
from ui.pages.compress_pdf_page import CompressPdfPage
from ui.pages.crop_pdf_page import CropPdfPage
from ui.pages.extract_pages_page import ExtractPagesPage
from ui.pages.image_resizer_page import ImageResizerPage
from ui.pages.jpg_to_pdf_page import JpgToPdfPage
from ui.pages.lock_pdf_page import LockPdfPage
from ui.pages.merge_pdf_page import MergePdfPage
from ui.pages.organize_pdf_page import OrganizePdfPage
from ui.pages.page_numbers_page import PageNumbersPage
from ui.pages.pdf_forms_page import PdfFormsPage
from ui.pages.pdf_to_jpg_page import PdfToJpgPage
from ui.pages.png_to_jpg_page import PngToJpgPage
from ui.pages.redact_pdf_page import RedactPdfPage
from ui.pages.remove_pages_page import RemovePagesPage
from ui.pages.repair_pdf_page import RepairPdfPage
from ui.pages.rotate_pdf_page import RotatePdfPage
from ui.pages.settings_page import SettingsPage
from ui.pages.sign_pdf_page import SignPdfPage
from ui.pages.split_pdf_page import SplitPdfPage
from ui.pages.unlock_pdf_page import UnlockPdfPage
from ui.pages.watermark_page import WatermarkPage
from ui.styles import DARK_STYLE, LIGHT_STYLE
from version import APP_VERSION

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_PATH = os.path.join(BASE_DIR, "assets", "icons", "app.ico")

# (svg icon name, title, description, page class)
IMAGE_TOOLS = [
    ("resize", "Image Resizer", "Compress images down to a target file size.", ImageResizerPage),
    ("repeat", "PNG → JPG", "Convert PNG images into JPG format.", PngToJpgPage),
]

ORGANIZE_TOOLS = [
    ("merge", "Merge PDF", "Combine multiple PDFs into one document.", MergePdfPage),
    ("split", "Split PDF", "Split a PDF into separate single-page files.", SplitPdfPage),
    ("file-minus", "Remove Pages", "Delete specific pages from a PDF.", RemovePagesPage),
    ("file-extract", "Extract Pages", "Pull specific pages into a new PDF.", ExtractPagesPage),
    ("grid", "Organize PDF", "Reorder, rotate, or delete pages visually.", OrganizePdfPage),
]

OPTIMIZE_TOOLS = [
    ("minimize", "Compress PDF", "Shrink PDF file size without losing quality.", CompressPdfPage),
    ("file-pulse", "Repair PDF", "Fix corrupted or malformed PDF files.", RepairPdfPage),
]

CONVERT_TOOLS = [
    ("layers", "JPG → PDF", "Convert one or multiple JPG images into a PDF.", JpgToPdfPage),
    ("image", "PDF → JPG", "Convert PDF pages into high-quality JPG images.", PdfToJpgPage),
]

EDIT_TOOLS = [
    ("rotate-cw", "Rotate PDF", "Rotate every page of a PDF.", RotatePdfPage),
    ("hash", "Add Page Numbers", "Stamp page numbers onto a PDF.", PageNumbersPage),
    ("droplet", "Add Watermark", "Overlay a text watermark across a PDF.", WatermarkPage),
    ("crop", "Crop PDF", "Crop the margins of every page.", CropPdfPage),
    ("clipboard", "PDF Forms", "Fill in a PDF's fillable form fields.", PdfFormsPage),
]

SECURITY_TOOLS = [
    ("lock", "Protect PDF", "Protect your PDF document with a password.", LockPdfPage),
    ("unlock", "Unlock PDF", "Remove password protection from a PDF.", UnlockPdfPage),
    ("edit-3", "Sign PDF", "Stamp a visual signature onto a PDF.", SignPdfPage),
    ("eye-off", "Redact PDF", "Permanently black out sensitive text.", RedactPdfPage),
    ("columns", "Compare PDF", "Find text differences between two PDFs.", ComparePdfPage),
]

NAV_SECTIONS = [
    ("IMAGE", IMAGE_TOOLS),
    ("ORGANIZE PDF", ORGANIZE_TOOLS),
    ("OPTIMIZE PDF", OPTIMIZE_TOOLS),
    ("CONVERT PDF", CONVERT_TOOLS),
    ("EDIT PDF", EDIT_TOOLS),
    ("PDF SECURITY", SECURITY_TOOLS),
]

ALL_TOOLS = IMAGE_TOOLS + ORGANIZE_TOOLS + OPTIMIZE_TOOLS + CONVERT_TOOLS + EDIT_TOOLS + SECURITY_TOOLS

COPYRIGHT_TEXT = "© 2026 Rahul Swargam\nMIT License"


def _apply_dark_title_bar(hwnd, dark):
    """Best-effort: tints the native Windows title bar to match dark mode."""

    if sys.platform != "win32":
        return

    try:
        import ctypes

        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        value = ctypes.c_int(1 if dark else 0)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            ctypes.c_void_p(int(hwnd)),
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(value),
            ctypes.sizeof(value),
        )
    except Exception:
        pass


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"Image & PDF Toolkit v{APP_VERSION}")
        self.resize(1200, 760)
        self.setMinimumSize(1040, 680)

        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        self.theme_mode = settings_store.get_theme_mode()
        self.dark_mode = self._resolve_dark_mode()

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self.nav_buttons = {}

        # Apply the stylesheet before building any widgets: widgets created
        # while QApplication has no stylesheet yet don't reliably get
        # repolished when one is set afterwards (seen as unstyled/"faded"
        # buttons on the Home page cards, built inside setup_ui()).
        app = QApplication.instance()
        if app:
            app.setStyleSheet(DARK_STYLE if self.dark_mode else LIGHT_STYLE)

        QGuiApplication.styleHints().colorSchemeChanged.connect(self._on_system_theme_changed)

        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # =========================
        # SIDEBAR
        # =========================

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(272)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 24, 20, 20)
        sidebar_layout.setSpacing(2)

        title = QLabel("Image & PDF")
        title.setObjectName("appTitle")

        subtitle = QLabel("TOOLKIT")
        subtitle.setObjectName("sidebarSubtitle")

        sidebar_layout.addWidget(title)
        sidebar_layout.addWidget(subtitle)
        sidebar_layout.addSpacing(26)

        self.home_button = self._build_nav_item("home", "Home", checked=True)
        self.home_button.clicked.connect(self.show_home)
        sidebar_layout.addWidget(self.home_button)

        # The tool list is long enough now (six categories) that it needs to
        # scroll independently of Home/Settings/footer, which stay pinned.
        nav_scroll = SmoothScrollArea()
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setFrameShape(QFrame.Shape.NoFrame)
        nav_scroll.setObjectName("sidebarNavScroll")
        nav_scroll.viewport().setObjectName("sidebarNavViewport")

        nav_list = QWidget()
        nav_list.setObjectName("sidebarNavViewport")
        nav_list_layout = QVBoxLayout(nav_list)
        nav_list_layout.setContentsMargins(0, 0, 0, 0)
        nav_list_layout.setSpacing(2)

        for section_name, tools in NAV_SECTIONS:
            nav_list_layout.addWidget(self._section_label(section_name))
            for icon_name, title_text, description, page_class in tools:
                nav_list_layout.addWidget(
                    self._build_tool_nav_item(icon_name, title_text, description, page_class)
                )

        nav_list_layout.addStretch()
        nav_scroll.setWidget(nav_list)
        sidebar_layout.addWidget(nav_scroll, 1)

        self.settings_button = self._build_nav_item("settings", "Settings")
        self.settings_button.clicked.connect(self.open_settings_page)
        self.nav_buttons["Settings"] = self.settings_button
        sidebar_layout.addWidget(self.settings_button)

        sidebar_layout.addSpacing(14)

        footer = QLabel(f"{COPYRIGHT_TEXT}\nv{APP_VERSION}")
        footer.setObjectName("sidebarFooter")
        footer.setWordWrap(True)
        sidebar_layout.addWidget(footer)

        # =========================
        # CONTENT
        # =========================

        self.content = QWidget()
        self.content.setObjectName("contentArea")

        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(44, 36, 44, 32)
        self.content_layout.setSpacing(6)

        self.toast = Toast(self.content)

        self.show_home()

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content)

    def _section_label(self, text):
        label = QLabel(text)
        label.setObjectName("sectionLabel")
        label.setContentsMargins(5, 18, 5, 4)
        return label

    def _build_nav_item(self, icon_name, text, checked=False):
        item = NavItem(icon_name, text, dark_mode=self.dark_mode)
        item.setChecked(checked)
        self.nav_group.addButton(item)
        return item

    def _build_tool_nav_item(self, icon_name, title_text, description, page_class):
        item = self._build_nav_item(icon_name, title_text)
        item.clicked.connect(
            lambda checked=False, p=page_class, t=title_text, d=description: self.open_tool(p, t, d)
        )
        self.nav_buttons[title_text] = item
        return item

    def notify(self, message, kind="success"):
        self.toast.show_message(message, kind)

    def clear_content(self):

        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def show_home(self):

        self.clear_content()
        self.home_button.setChecked(True)

        scroll_area = SmoothScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.viewport().setObjectName("scrollViewport")

        page = HomePage(self.notify, self.open_tool, self.open_dropped_files, NAV_SECTIONS)
        page.setObjectName("scrollViewport")
        scroll_area.setWidget(page)

        self.content_layout.addWidget(scroll_area)

    def open_dropped_files(self, paths):
        if not paths:
            return

        extension = os.path.splitext(paths[0])[1].lower()

        if extension in IMAGE_EXTENSIONS:
            self.open_tool(
                ImageResizerPage,
                "Image Resizer",
                "Compress images down to a target file size.",
                initial_paths=paths,
            )
        else:
            self.open_tool(
                PdfToJpgPage,
                "PDF → JPG",
                "Convert PDF pages into high-quality JPG images.",
                initial_paths=paths,
            )

    def open_tool(self, page_class, title_text, description, initial_paths=None):
        def factory():
            page = page_class(self.notify)
            if initial_paths:
                self._seed_page(page, initial_paths)
            return page

        self._open_page(title_text, description, factory)

    def _seed_page(self, page, initial_paths):
        for method_name in ("load_images", "load_pdfs", "load_image"):
            method = getattr(page, method_name, None)
            if method is None:
                continue
            try:
                method(initial_paths if method_name != "load_image" else initial_paths[0])
            except Exception:
                pass
            return

    def open_settings_page(self):
        self._open_page(
            "Settings",
            "Configure appearance and default save location.",
            lambda: SettingsPage(self.notify, self.refresh_theme),
        )

    def _open_page(self, title_text, description, page_factory):

        self.clear_content()

        if title_text in self.nav_buttons:
            self.nav_buttons[title_text].setChecked(True)
        else:
            self.home_button.setChecked(False)
            for button in self.nav_buttons.values():
                button.setChecked(False)

        breadcrumb = NavBreadcrumb(title_text)
        breadcrumb.clicked.connect(self.show_home)
        self.content_layout.addWidget(breadcrumb)

        self.content_layout.addSpacing(12)

        title = QLabel(title_text)
        title.setObjectName("pageTitle")
        fade_in(title)

        subtitle = QLabel(description)
        subtitle.setObjectName("pageSubtitle")

        self.content_layout.addWidget(title)
        self.content_layout.addWidget(subtitle)
        self.content_layout.addSpacing(18)

        scroll_area = SmoothScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.viewport().setObjectName("scrollViewport")

        page = page_factory()
        page.setObjectName("scrollViewport")
        scroll_area.setWidget(page)

        self.content_layout.addWidget(scroll_area)

    def _resolve_dark_mode(self):

        if self.theme_mode == settings_store.THEME_DARK:
            return True

        if self.theme_mode == settings_store.THEME_LIGHT:
            return False

        # "system" — follow the OS light/dark setting.
        return QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark

    def refresh_theme(self):
        self.theme_mode = settings_store.get_theme_mode()
        self.apply_theme()

    def _on_system_theme_changed(self, _scheme):
        if self.theme_mode == settings_store.THEME_SYSTEM:
            self.apply_theme()

    def apply_theme(self):

        self.dark_mode = self._resolve_dark_mode()
        stylesheet = DARK_STYLE if self.dark_mode else LIGHT_STYLE

        app = QApplication.instance()
        if app:
            app.setStyleSheet(stylesheet)

        # Nav icons are tinted pixmaps, not QSS-driven, so they need an
        # explicit refresh now that the sidebar follows the app theme.
        # (nav_buttons already includes settings_button, but not home_button.)
        self.home_button.set_dark_mode(self.dark_mode)
        for button in self.nav_buttons.values():
            button.set_dark_mode(self.dark_mode)

        _apply_dark_title_bar(int(self.winId()), self.dark_mode)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        if self.toast.isVisible():
            self.toast._reposition()
