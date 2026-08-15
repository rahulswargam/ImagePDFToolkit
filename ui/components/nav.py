from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton

from ui import icons as icon_lib
from ui import tokens

_BREADCRUMB_ICON_COLOR = "#9397a8"

# The sidebar is always dark regardless of app theme, so nav icon colors are
# constant rather than driven by the light/dark color tokens.
ICON_MUTED = "#8b8fa3"
ICON_ACTIVE = "#ffffff"


class NavItem(QPushButton):
    """Sidebar navigation entry: icon + label. Icon brightens when active/checked."""

    def __init__(self, icon_name, text, parent=None):
        super().__init__(text, parent)

        self._icon_name = icon_name

        self.setObjectName("sidebarButton")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setIconSize(QSize(tokens.ICON_MD, tokens.ICON_MD))

        self._sync_icon(False)
        self.toggled.connect(self._sync_icon)

    def _sync_icon(self, checked):
        color = ICON_ACTIVE if checked else ICON_MUTED
        self.setIcon(icon_lib.get_icon(self._icon_name, color, tokens.ICON_MD))


class NavBreadcrumb(QPushButton):
    """'← Home / <page title>' breadcrumb button shown atop every non-Home page."""

    def __init__(self, title_text, parent=None):
        super().__init__(f"Home  /  {title_text}", parent)

        self.setObjectName("backButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setIcon(icon_lib.get_icon("chevron-left", _BREADCRUMB_ICON_COLOR, tokens.ICON_SM))
        self.setIconSize(QSize(tokens.ICON_SM, tokens.ICON_SM))
