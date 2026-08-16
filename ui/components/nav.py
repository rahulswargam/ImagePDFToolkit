from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton

from ui import icons as icon_lib
from ui import tokens

_BREADCRUMB_ICON_COLOR = "#9397a8"

# Icon pixmaps are tinted directly (not QSS-driven), so they need their own
# per-theme palette now that the sidebar follows Light/Dark instead of
# always staying dark. NavItem.set_dark_mode() switches between these.
_DARK_ICON_MUTED = "#8b8fa3"
_DARK_ICON_HOVER = "#c4c7d4"
_DARK_ICON_ACTIVE = "#ffffff"

_LIGHT_ICON_MUTED = "#8a8fa0"
_LIGHT_ICON_HOVER = "#3f434f"
_LIGHT_ICON_ACTIVE = "#14161f"


class NavItem(QPushButton):
    """Sidebar navigation entry: icon + label. Icon brightens on hover, and
    fully on active/checked."""

    def __init__(self, icon_name, text, dark_mode=True, parent=None):
        super().__init__(text, parent)

        self._icon_name = icon_name
        self._dark_mode = dark_mode

        self.setObjectName("sidebarButton")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setIconSize(QSize(tokens.ICON_MD, tokens.ICON_MD))

        self._sync_icon()
        self.toggled.connect(self._sync_icon)

    def set_dark_mode(self, dark_mode):
        self._dark_mode = dark_mode
        self._sync_icon()

    def _sync_icon(self, *_args):
        if self._dark_mode:
            muted, hover, active = _DARK_ICON_MUTED, _DARK_ICON_HOVER, _DARK_ICON_ACTIVE
        else:
            muted, hover, active = _LIGHT_ICON_MUTED, _LIGHT_ICON_HOVER, _LIGHT_ICON_ACTIVE

        if self.isChecked():
            color = active
        elif self.underMouse():
            color = hover
        else:
            color = muted
        self.setIcon(icon_lib.get_icon(self._icon_name, color, tokens.ICON_MD))

    def enterEvent(self, event):
        self._sync_icon()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._sync_icon()
        super().leaveEvent(event)


class NavBreadcrumb(QPushButton):
    """'← Home / <page title>' breadcrumb button shown atop every non-Home page."""

    def __init__(self, title_text, parent=None):
        super().__init__(f"Home  /  {title_text}", parent)

        self.setObjectName("backButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setIcon(icon_lib.get_icon("chevron-left", _BREADCRUMB_ICON_COLOR, tokens.ICON_SM))
        self.setIconSize(QSize(tokens.ICON_SM, tokens.ICON_SM))
        self.setToolTip("Back to Home")
