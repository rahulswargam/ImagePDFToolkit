import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.pages.image_resizer_page import ImageResizerPage
from ui.pages.jpg_to_pdf_page import JpgToPdfPage
from ui.pages.lock_pdf_page import LockPdfPage
from ui.pages.pdf_to_jpg_page import PdfToJpgPage
from ui.pages.png_to_jpg_page import PngToJpgPage
from ui.pages.unlock_pdf_page import UnlockPdfPage
from ui.styles import DARK_STYLE, LIGHT_STYLE
from ui.widgets import AnimatedButton, Toast, ToolCard

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_PATH = os.path.join(BASE_DIR, "assets", "icons", "app.ico")
TOOL_ICON_DIR = os.path.join(BASE_DIR, "assets", "icons", "tools")

RESIZE_ICON = os.path.join(TOOL_ICON_DIR, "resize.png")
IMAGE_ICON = os.path.join(TOOL_ICON_DIR, "image.png")
DOCUMENT_ICON = os.path.join(TOOL_ICON_DIR, "document.png")
LOCK_ICON = os.path.join(TOOL_ICON_DIR, "lock.png")
UNLOCK_ICON = os.path.join(TOOL_ICON_DIR, "unlock.png")

IMAGE_TOOLS = [
    (RESIZE_ICON, "Image Resizer", "Compress images down to a target file size.", ImageResizerPage),
    (IMAGE_ICON, "PNG → JPG", "Convert PNG images into JPG format.", PngToJpgPage),
    (DOCUMENT_ICON, "JPG → PDF", "Convert one or multiple JPG images into a PDF.", JpgToPdfPage),
]

PDF_TOOLS = [
    (IMAGE_ICON, "PDF → JPG", "Convert PDF pages into high-quality JPG images.", PdfToJpgPage),
    (LOCK_ICON, "Lock PDF", "Protect your PDF document with a password.", LockPdfPage),
    (UNLOCK_ICON, "Unlock PDF", "Remove password protection from a PDF.", UnlockPdfPage),
]

ALL_TOOLS = IMAGE_TOOLS + PDF_TOOLS

APP_VERSION = "1.0.0"
COPYRIGHT_TEXT = "© 2026 Rahul Swargam\nMIT License"


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image & PDF Toolkit")
        self.resize(1200, 760)
        self.setMinimumSize(1040, 680)

        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        self.dark_mode = False
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self.nav_buttons = {}

        # Apply the stylesheet before building any widgets: widgets created
        # while QApplication has no stylesheet yet don't reliably get
        # repolished when one is set afterwards (seen as unstyled/"faded"
        # buttons on the Home page cards, built inside setup_ui()).
        app = QApplication.instance()
        if app:
            app.setStyleSheet(LIGHT_STYLE)

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
        sidebar.setFixedWidth(280)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(24, 26, 24, 20)
        sidebar_layout.setSpacing(2)

        title = QLabel("Image & PDF")
        title.setObjectName("appTitle")

        subtitle = QLabel("TOOLKIT")
        subtitle.setObjectName("sidebarSubtitle")

        sidebar_layout.addWidget(title)
        sidebar_layout.addWidget(subtitle)
        sidebar_layout.addSpacing(28)

        self.home_button = self.create_sidebar_button("⌂   Home", checked=True)
        self.home_button.clicked.connect(self.show_home)
        sidebar_layout.addWidget(self.home_button)

        sidebar_layout.addWidget(self._section_label("IMAGE"))

        for icon, title_text, description, page_class in IMAGE_TOOLS:
            sidebar_layout.addWidget(
                self._build_nav_button(title_text, description, page_class)
            )

        sidebar_layout.addWidget(self._section_label("PDF"))

        for icon, title_text, description, page_class in PDF_TOOLS:
            sidebar_layout.addWidget(
                self._build_nav_button(title_text, description, page_class)
            )

        sidebar_layout.addStretch()

        self.theme_button = QPushButton("🌙   Dark Mode")
        self.theme_button.setObjectName("themeToggle")
        self.theme_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_button.clicked.connect(self.toggle_theme)
        sidebar_layout.addWidget(self.theme_button)

        sidebar_layout.addSpacing(6)

        settings_button = QPushButton("⚙   Settings")
        settings_button.setObjectName("themeToggle")
        settings_button.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_button.clicked.connect(self.coming_soon)
        sidebar_layout.addWidget(settings_button)

        sidebar_layout.addSpacing(18)

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

    def _build_nav_button(self, title_text, description, page_class):
        button = self.create_sidebar_button(f"▪   {title_text}")
        button.clicked.connect(
            lambda checked=False, p=page_class, t=title_text, d=description: self.open_tool(p, t, d)
        )
        self.nav_buttons[title_text] = button
        return button

    def create_sidebar_button(self, text, checked=False):
        button = QPushButton(text)
        button.setObjectName("sidebarButton")
        button.setCheckable(True)
        button.setChecked(checked)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.nav_group.addButton(button)
        return button

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

        page_title = QLabel("Image & PDF Toolkit")
        page_title.setObjectName("pageTitle")

        page_subtitle = QLabel("Simple, fast and offline tools for your images and PDF files.")
        page_subtitle.setObjectName("pageSubtitle")

        self.content_layout.addWidget(page_title)
        self.content_layout.addWidget(page_subtitle)
        self.content_layout.addSpacing(24)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.viewport().setObjectName("scrollViewport")

        cards_container = QWidget()
        cards_container.setObjectName("scrollViewport")
        grid = QGridLayout(cards_container)
        grid.setSpacing(18)

        for index, (icon, title_text, description, page_class) in enumerate(ALL_TOOLS):
            row = index // 2
            column = index % 2

            card = ToolCard(
                icon,
                title_text,
                description,
                lambda checked=False, p=page_class, t=title_text, d=description: self.open_tool(p, t, d),
            )
            grid.addWidget(card, row, column)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        scroll_area.setWidget(cards_container)
        self.content_layout.addWidget(scroll_area)

    def open_tool(self, page_class, title_text, description):

        self.clear_content()

        if title_text in self.nav_buttons:
            self.nav_buttons[title_text].setChecked(True)

        breadcrumb = QPushButton(f"←   Home  /  {title_text}")
        breadcrumb.setObjectName("backButton")
        breadcrumb.setCursor(Qt.CursorShape.PointingHandCursor)
        breadcrumb.clicked.connect(self.show_home)
        self.content_layout.addWidget(breadcrumb)

        self.content_layout.addSpacing(12)

        title = QLabel(title_text)
        title.setObjectName("pageTitle")

        subtitle = QLabel(description)
        subtitle.setObjectName("pageSubtitle")

        self.content_layout.addWidget(title)
        self.content_layout.addWidget(subtitle)
        self.content_layout.addSpacing(18)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.viewport().setObjectName("scrollViewport")

        page = page_class(self.notify)
        page.setObjectName("scrollViewport")
        scroll_area.setWidget(page)

        self.content_layout.addWidget(scroll_area)

    def coming_soon(self):
        QMessageBox.information(self, "Coming Soon", "This will be added next.")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self):

        stylesheet = DARK_STYLE if self.dark_mode else LIGHT_STYLE

        app = QApplication.instance()
        if app:
            app.setStyleSheet(stylesheet)

        self.theme_button.setText("☀️   Light Mode" if self.dark_mode else "🌙   Dark Mode")

    def resizeEvent(self, event):
        super().resizeEvent(event)

        if self.toast.isVisible():
            self.toast._reposition()
