LIGHT_COLORS = {
    # Base surfaces
    "bg": "#f7f8fa",
    "content_bg": "#f7f8fa",
    "surface": "#ffffff",
    "surface_raised": "#f6f7f9",
    "border": "#e8e9ed",
    "border_strong": "#d7d9e0",
    # Sidebar — follows the app theme (was always dark; now matches Light/Dark).
    "sidebar_bg": "#ffffff",
    "sidebar_border": "#e8e9ed",
    "sidebar_title": "#14161f",
    "sidebar_subtitle": "#8a8fa0",
    "sidebar_section_label": "#9397a8",
    "sidebar_item_text": "#4b4f5c",
    "sidebar_item_text_hover": "#14161f",
    "sidebar_item_hover_bg": "rgba(20, 22, 31, 0.05)",
    "sidebar_item_active_bg": "#fef2f2",
    "sidebar_item_active_text": "#14161f",
    "sidebar_indicator": "#dc2626",
    "sidebar_icon_muted": "#8a8fa0",
    "sidebar_icon_active": "#14161f",
    "sidebar_footer_text": "#9397a8",
    "sidebar_footer_border": "#e8e9ed",
    # Text
    "text_primary": "#14161f",
    "text_secondary": "#565c6d",
    "text_muted": "#8a8fa0",
    "page_title": "#14161f",
    # Icons (content area)
    "icon_default": "#14161f",
    "icon_muted": "#6b7280",
    # Accent — reserved for primary actions, active states, progress, status.
    "accent": "#dc2626",
    "accent_hover": "#b91c1c",
    "accent_pressed": "#991b1b",
    "accent_soft": "#fef2f2",
    "accent_on": "#ffffff",
    # Status
    "success": "#16a34a",
    "warning": "#d97706",
    "error": "#f97316",
    # Inputs
    "input_bg": "#ffffff",
    "input_border": "#d8dae2",
    "input_text": "#14161f",
    "input_placeholder": "#9aa0b4",
    "combo_popup_bg": "#ffffff",
    # Drop workspace
    "workspace_bg": "#fafafc",
    "workspace_border": "#dfe1e8",
    "workspace_active_bg": "#fef2f2",
    "workspace_active_border": "#dc2626",
    # Scrollbar
    "scroll_track": "#f1f2f6",
    "scroll_handle": "#cfd2dc",
    "scroll_handle_hover": "#adb1c0",
    # Toast
    "toast_bg": "#14161f",
    "toast_text": "#f7f8fa",
}

DARK_COLORS = {
    "bg": "#0a0b10",
    "content_bg": "#0e1017",
    "surface": "#14161f",
    "surface_raised": "#191c28",
    "border": "#20222e",
    "border_strong": "#33354a",
    "sidebar_bg": "#0a0b10",
    "sidebar_border": "#1b1d29",
    "sidebar_title": "#ffffff",
    "sidebar_subtitle": "#8b8fa3",
    "sidebar_section_label": "#5b5f72",
    "sidebar_item_text": "#b7bacb",
    "sidebar_item_text_hover": "#ffffff",
    "sidebar_item_hover_bg": "rgba(255, 255, 255, 0.05)",
    "sidebar_item_active_bg": "rgba(255, 255, 255, 0.07)",
    "sidebar_item_active_text": "#ffffff",
    "sidebar_indicator": "#ef4444",
    "sidebar_icon_muted": "#8b8fa3",
    "sidebar_icon_active": "#ffffff",
    "sidebar_footer_text": "#5b5f72",
    "sidebar_footer_border": "#1b1d29",
    "text_primary": "#e7e8ee",
    "text_secondary": "#9397a8",
    "text_muted": "#6b6f85",
    "page_title": "#f5f6fa",
    "icon_default": "#e7e8ee",
    "icon_muted": "#9397a8",
    "accent": "#ef4444",
    "accent_hover": "#f87171",
    "accent_pressed": "#dc2626",
    "accent_soft": "#2a1212",
    "accent_on": "#ffffff",
    "success": "#4ade80",
    "warning": "#fbbf24",
    "error": "#fb923c",
    "input_bg": "#0e1017",
    "input_border": "#262838",
    "input_text": "#e7e8ee",
    "input_placeholder": "#5b5f72",
    "combo_popup_bg": "#14161f",
    "workspace_bg": "#0e1017",
    "workspace_border": "#20222e",
    "workspace_active_bg": "#2a1212",
    "workspace_active_border": "#ef4444",
    "scroll_track": "#0e1017",
    "scroll_handle": "#262838",
    "scroll_handle_hover": "#33354a",
    "toast_bg": "#1b1d29",
    "toast_text": "#f5f6fa",
}


def build_style(colors):
    return f"""
QMainWindow {{
    background-color: {colors['bg']};
}}

QWidget {{
    font-family: "Roboto";
    font-size: 14px;
    color: {colors['text_primary']};
}}

/* =========================
   SIDEBAR
   ========================= */

#sidebar {{
    background-color: {colors['sidebar_bg']};
    border-right: 1px solid {colors['sidebar_border']};
}}

#appTitle {{
    font-family: "Roboto Black";
    color: {colors['sidebar_title']};
    font-size: 18px;
}}

#sidebarSubtitle {{
    font-family: "Roboto Medium";
    color: {colors['sidebar_subtitle']};
    font-size: 11px;
    letter-spacing: 2px;
}}

#sectionLabel {{
    font-family: "Roboto Medium";
    color: {colors['sidebar_section_label']};
    font-size: 11px;
    letter-spacing: 1px;
    background-color: transparent;
}}

QPushButton#sidebarButton {{
    font-family: "Roboto";
    background-color: transparent;
    color: {colors['sidebar_item_text']};
    border: none;
    border-left: 3px solid transparent;
    text-align: left;
    padding: 10px 14px;
    font-size: 13.5px;
    border-radius: 0px;
}}

QPushButton#sidebarButton:hover {{
    background-color: {colors['sidebar_item_hover_bg']};
    color: {colors['sidebar_item_text_hover']};
}}

QPushButton#sidebarButton:checked {{
    background-color: {colors['sidebar_item_active_bg']};
    border-left: 3px solid {colors['sidebar_indicator']};
    color: {colors['sidebar_item_active_text']};
    font-family: "Roboto Medium";
}}

QPushButton#themeToggle {{
    font-family: "Roboto";
    background-color: transparent;
    color: {colors['sidebar_item_text']};
    border: 1px solid {colors['sidebar_border']};
    border-radius: 8px;
    padding: 9px 14px;
    text-align: left;
    font-size: 13px;
}}

QPushButton#themeToggle:hover {{
    background-color: {colors['sidebar_item_hover_bg']};
    color: #ffffff;
}}

#sidebarFooter {{
    color: {colors['sidebar_footer_text']};
    font-size: 11px;
    background-color: transparent;
    border-top: 1px solid {colors['sidebar_footer_border']};
    padding-top: 12px;
}}

QScrollArea#sidebarNavScroll {{
    background-color: transparent;
    border: none;
}}

QWidget#sidebarNavViewport {{
    background-color: transparent;
}}

#sidebar QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 4px 0px 4px 0px;
}}

#sidebar QScrollBar::handle:vertical {{
    background: {colors['sidebar_border']};
    border-radius: 4px;
    min-height: 24px;
}}

#sidebar QScrollBar::handle:vertical:hover {{
    background: {colors['sidebar_indicator']};
}}

#sidebar QScrollBar::add-line:vertical,
#sidebar QScrollBar::sub-line:vertical {{
    height: 0px;
    border: none;
    background: none;
}}

#sidebar QScrollBar::add-page:vertical,
#sidebar QScrollBar::sub-page:vertical {{
    background: none;
}}

/* =========================
   MAIN CONTENT
   ========================= */

#contentArea {{
    background-color: {colors['content_bg']};
}}

#pageTitle {{
    font-family: "Roboto Black";
    color: {colors['page_title']};
    font-size: 28px;
    background-color: transparent;
}}

#sectionHeading {{
    font-family: "Roboto SemiBold";
    color: {colors['text_primary']};
    font-size: 18px;
    background-color: transparent;
}}

#pageSubtitle {{
    font-family: "Roboto";
    color: {colors['text_secondary']};
    font-size: 13.5px;
    background-color: transparent;
}}

#metaLabel {{
    font-family: "Roboto Medium";
    color: {colors['text_muted']};
    font-size: 12px;
    background-color: transparent;
}}

QPushButton#backButton {{
    font-family: "Roboto Medium";
    background-color: transparent;
    color: {colors['text_secondary']};
    border: none;
    text-align: left;
    padding: 4px 0px;
    font-size: 13px;
}}

QPushButton#backButton:hover {{
    color: {colors['accent']};
}}

/* =========================
   CARDS / SURFACES
   ========================= */

QFrame#toolCard {{
    background-color: {colors['surface']};
    border: 1px solid {colors['border']};
    border-radius: 16px;
}}

QFrame#toolCard:hover {{
    border: 1px solid {colors['border_strong']};
    background-color: {colors['surface_raised']};
}}

QLabel#toolTitle {{
    font-family: "Roboto SemiBold";
    color: {colors['text_primary']};
    background-color: transparent;
    font-size: 16px;
}}

QLabel#toolDescription {{
    font-family: "Roboto";
    color: {colors['text_secondary']};
    background-color: transparent;
    font-size: 13px;
}}

QLabel#fieldLabel {{
    font-family: "Roboto Medium";
    color: {colors['text_secondary']};
    background-color: transparent;
    font-size: 12.5px;
}}

QLabel#numberFieldUnit {{
    font-family: "Roboto SemiBold";
    color: {colors['text_secondary']};
    background-color: transparent;
    font-size: 13px;
}}

QSpinBox#numberFieldSpin {{
    font-family: "Roboto SemiBold";
    background-color: {colors['input_bg']};
    color: {colors['input_text']};
    border: 1px solid {colors['input_border']};
    border-radius: 10px;
    padding: 0px 4px 0px 12px;
    font-size: 15px;
    selection-background-color: {colors['accent']};
}}

QSpinBox#numberFieldSpin:focus {{
    border: 1px solid {colors['accent']};
}}

QSpinBox#numberFieldSpin::up-button,
QSpinBox#numberFieldSpin::down-button {{
    width: 20px;
    border: none;
    background: transparent;
}}

QSpinBox#numberFieldSpin::up-button {{
    subcontrol-position: top right;
    margin: 3px 3px 0px 0px;
}}

QSpinBox#numberFieldSpin::down-button {{
    subcontrol-position: bottom right;
    margin: 0px 3px 3px 0px;
}}

/* =========================
   BUTTONS
   ========================= */

QPushButton#toolButton {{
    font-family: "Roboto SemiBold";
    background-color: {colors['accent']};
    color: {colors['accent_on']};
    border: none;
    border-radius: 12px;
    padding: 10px 16px;
    font-size: 13.5px;
}}

QPushButton#toolButton:hover {{
    background-color: {colors['accent_hover']};
}}

QPushButton#toolButton:pressed {{
    background-color: {colors['accent_pressed']};
}}

QPushButton#toolButton:disabled {{
    background-color: {colors['border_strong']};
    color: {colors['text_muted']};
}}

QPushButton#secondaryButton {{
    font-family: "Roboto SemiBold";
    background-color: transparent;
    color: {colors['text_primary']};
    border: 1px solid {colors['border_strong']};
    border-radius: 12px;
    padding: 9px 16px;
    font-size: 13.5px;
}}

QPushButton#secondaryButton:hover {{
    border: 1px solid {colors['accent']};
    color: {colors['accent']};
}}

QPushButton#iconButton {{
    background-color: transparent;
    border: none;
    border-radius: 8px;
    padding: 6px;
}}

QPushButton#iconButton:hover {{
    background-color: {colors['surface_raised']};
}}

/* =========================
   INPUT FIELDS
   ========================= */

QSpinBox,
QComboBox,
QLineEdit {{
    font-family: "Roboto";
    background-color: {colors['input_bg']};
    color: {colors['input_text']};
    border: 1px solid {colors['input_border']};
    border-radius: 10px;
    padding: 9px 10px;
    min-height: 22px;
    selection-background-color: {colors['accent']};
}}

QSpinBox:focus,
QComboBox:focus,
QLineEdit:focus {{
    border: 1px solid {colors['accent']};
}}

QComboBox QAbstractItemView {{
    font-family: "Roboto";
    background-color: {colors['combo_popup_bg']};
    color: {colors['input_text']};
    selection-background-color: {colors['accent']};
    selection-color: #ffffff;
    outline: none;
}}

QSlider::groove:horizontal {{
    background: {colors['border_strong']};
    height: 4px;
    border-radius: 2px;
}}

QSlider::sub-page:horizontal {{
    background: {colors['accent']};
    height: 4px;
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    background: {colors['accent']};
    border: 2px solid {colors['surface']};
    width: 16px;
    height: 16px;
    margin: -7px 0;
    border-radius: 9px;
}}

QSlider::handle:horizontal:hover {{
    background: {colors['accent_hover']};
}}

QProgressBar {{
    background-color: {colors['border']};
    border: none;
    border-radius: 3px;
    max-height: 6px;
}}

QProgressBar::chunk {{
    background-color: {colors['accent']};
    border-radius: 3px;
}}

QCheckBox {{
    font-family: "Roboto";
    color: {colors['text_primary']};
    spacing: 8px;
    background-color: transparent;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
}}

QLabel {{
    background-color: transparent;
    color: {colors['text_primary']};
}}

/* =========================
   DROP WORKSPACE
   ========================= */

#previewFrame {{
    background-color: {colors['workspace_bg']};
    border: 1.5px dashed {colors['workspace_border']};
    border-radius: 16px;
    color: {colors['text_secondary']};
    font-size: 13px;
    padding: 10px;
}}

#previewFrame[dragActive="true"] {{
    background-color: {colors['workspace_active_bg']};
    border: 1.5px dashed {colors['workspace_active_border']};
    color: {colors['accent']};
}}

#dropWorkspace {{
    background-color: {colors['workspace_bg']};
    border: 1.5px dashed {colors['workspace_border']};
    border-radius: 20px;
}}

#dropWorkspace:hover {{
    border: 1.5px dashed {colors['border_strong']};
    background-color: {colors['surface_raised']};
}}

#dropWorkspace:focus {{
    border: 1.5px dashed {colors['accent']};
}}

#dropWorkspace[dragActive="true"] {{
    background-color: {colors['workspace_active_bg']};
    border: 1.5px dashed {colors['workspace_active_border']};
}}

#dropWorkspaceTitle {{
    font-family: "Roboto SemiBold";
    color: {colors['text_primary']};
    font-size: 16px;
    background-color: transparent;
}}

#dropWorkspaceSubtitle {{
    font-family: "Roboto";
    color: {colors['text_secondary']};
    font-size: 13px;
    background-color: transparent;
}}

#dropWorkspaceHint {{
    font-family: "Roboto Medium";
    color: {colors['text_muted']};
    font-size: 11px;
    letter-spacing: 1px;
    background-color: transparent;
}}

/* =========================
   FILE ROWS / GRID ITEMS
   ========================= */

QFrame#fileRow {{
    background-color: {colors['surface']};
    border: 1px solid {colors['border']};
    border-radius: 12px;
}}

QFrame#fileRow:hover {{
    border: 1px solid {colors['border_strong']};
    background-color: {colors['surface_raised']};
}}

QLabel#fileRowIcon {{
    background-color: {colors['accent_soft']};
    color: {colors['accent']};
    border-radius: 9px;
    font-size: 15px;
}}

QLabel#fileRowName {{
    font-family: "Roboto Medium";
    color: {colors['text_primary']};
    background-color: transparent;
    font-size: 13px;
}}

QLabel#fileRowMeta {{
    font-family: "Roboto Medium";
    color: {colors['text_muted']};
    background-color: transparent;
    font-size: 10.5px;
    letter-spacing: 0.5px;
}}

QPushButton#fileRowRemove {{
    font-family: "Roboto";
    background-color: transparent;
    color: {colors['text_secondary']};
    border: none;
    border-radius: 8px;
    font-size: 14px;
}}

QPushButton#fileRowRemove:hover {{
    background-color: {colors['accent_soft']};
    color: {colors['accent']};
}}

QFrame#fileGridItem {{
    background-color: {colors['surface']};
    border: 1px solid {colors['border']};
    border-radius: 14px;
}}

QFrame#fileGridItem:hover {{
    border: 1px solid {colors['border_strong']};
    background-color: {colors['surface_raised']};
}}

#fileGridThumb {{
    background-color: {colors['workspace_bg']};
    border-radius: 10px;
}}

#fileGridName {{
    font-family: "Roboto Medium";
    color: {colors['text_primary']};
    background-color: transparent;
    font-size: 12.5px;
}}

#fileGridMeta {{
    font-family: "Roboto Medium";
    color: {colors['text_muted']};
    background-color: transparent;
    font-size: 10.5px;
    letter-spacing: 0.3px;
}}

QListWidget#organizeList {{
    background-color: transparent;
    border: none;
    outline: none;
}}

QListWidget#organizeList::item {{
    background-color: {colors['surface']};
    border: 2px solid transparent;
    border-radius: 12px;
    padding: 6px;
    color: {colors['text_secondary']};
    font-family: "Roboto Medium";
    font-size: 11.5px;
}}

QListWidget#organizeList::item:hover {{
    border: 2px solid {colors['border_strong']};
}}

QListWidget#organizeList::item:selected {{
    border: 2px solid {colors['accent']};
    background-color: {colors['accent_soft']};
    color: {colors['accent']};
}}

/* =========================
   PASSWORD FIELD
   ========================= */

QPushButton#revealButton {{
    font-family: "Roboto Medium";
    background-color: {colors['input_bg']};
    color: {colors['text_secondary']};
    border: 1px solid {colors['input_border']};
    border-radius: 10px;
    padding: 9px 14px;
    font-size: 12.5px;
    min-height: 22px;
}}

QPushButton#revealButton:hover {{
    border: 1px solid {colors['accent']};
    color: {colors['accent']};
}}

QPushButton#revealButton:pressed {{
    background-color: {colors['accent_soft']};
    border: 1px solid {colors['accent']};
    color: {colors['accent']};
}}

#strengthSegment {{
    border-radius: 2px;
    background-color: {colors['border_strong']};
    max-height: 4px;
    min-height: 4px;
}}

#strengthSegment[level="weak"] {{
    background-color: {colors['error']};
}}

#strengthSegment[level="medium"] {{
    background-color: {colors['warning']};
}}

#strengthSegment[level="strong"] {{
    background-color: {colors['success']};
}}

#strengthLabel {{
    font-family: "Roboto Medium";
    font-size: 11px;
    background-color: transparent;
    color: {colors['text_muted']};
}}

/* =========================
   COMPLETION DIALOG / EMPTY / MODAL
   ========================= */

#completionBadge {{
    background-color: {colors['success']};
    border: none;
    border-radius: 28px;
}}

#completionBadge[kind="error"],
#completionBadge[kind="warning"] {{
    background-color: {colors['error']};
}}

#completionBadge[kind="info"] {{
    background-color: {colors['text_secondary']};
}}

#completionTitle {{
    font-family: "Roboto Black";
    color: {colors['text_primary']};
    font-size: 19px;
    background-color: transparent;
}}

#completionMessage {{
    font-family: "Roboto";
    color: {colors['text_secondary']};
    font-size: 13.5px;
    background-color: transparent;
}}

#modalCard {{
    background-color: {colors['surface']};
    border: 1px solid {colors['border']};
    border-radius: 18px;
}}

/* =========================
   QUICK ACTIONS / ACTIVITY / SEGMENTED CONTROL
   ========================= */

QFrame#quickActionRow {{
    background-color: {colors['surface']};
    border: 1px solid {colors['border']};
    border-radius: 12px;
}}

QFrame#quickActionRow:hover {{
    border: 1px solid {colors['border_strong']};
    background-color: {colors['surface_raised']};
}}

QFrame#quickActionRow:focus {{
    border: 1px solid {colors['accent']};
}}

#quickActionIconBadge {{
    background-color: {colors['accent_soft']};
    border-radius: 11px;
}}

#quickActionTitle {{
    font-family: "Roboto SemiBold";
    color: {colors['text_primary']};
    font-size: 13.5px;
    background-color: transparent;
}}

#quickActionSubtitle {{
    font-family: "Roboto";
    color: {colors['text_muted']};
    font-size: 11.5px;
    background-color: transparent;
}}

QPushButton#segmentOption {{
    font-family: "Roboto Medium";
    background-color: transparent;
    color: {colors['text_secondary']};
    border: none;
    border-radius: 9px;
    padding: 8px 14px;
    font-size: 13px;
}}

QPushButton#segmentOption:checked {{
    background-color: {colors['surface']};
    color: {colors['text_primary']};
    font-family: "Roboto SemiBold";
}}

#segmentTrack {{
    background-color: {colors['workspace_bg']};
    border: 1px solid {colors['border']};
    border-radius: 11px;
}}

/* =========================
   TOAST
   ========================= */

QFrame#toast {{
    background-color: {colors['toast_bg']};
    border-radius: 14px;
}}

QFrame#toast[kind="success"] {{
    border-left: 4px solid {colors['success']};
}}

QFrame#toast[kind="error"] {{
    border-left: 4px solid {colors['error']};
}}

QLabel#toastMessage {{
    font-family: "Roboto";
    color: {colors['toast_text']};
    font-size: 13px;
    background-color: transparent;
}}

QLabel#toastIcon {{
    font-family: "Roboto Medium";
    font-size: 16px;
    background-color: transparent;
}}

QFrame#toast[kind="success"] QLabel#toastIcon {{
    color: {colors['success']};
}}

QFrame#toast[kind="error"] QLabel#toastIcon {{
    color: {colors['error']};
}}

/* =========================
   SCROLL
   ========================= */

QScrollArea {{
    background-color: transparent;
    border: none;
}}

QWidget#scrollViewport {{
    background-color: transparent;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 14px;
    margin: 4px 3px 4px 1px;
}}

QScrollBar::handle:vertical {{
    background: {colors['scroll_handle']};
    border-radius: 5px;
    min-height: 32px;
}}

QScrollBar::handle:vertical:hover {{
    background: {colors['accent']};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0px;
    border: none;
    background: none;
}}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    background: none;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 14px;
    margin: 1px 4px 3px 4px;
}}

QScrollBar::handle:horizontal {{
    background: {colors['scroll_handle']};
    border-radius: 5px;
    min-width: 32px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {colors['accent']};
}}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    width: 0px;
    border: none;
    background: none;
}}

QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {{
    background: none;
}}

QToolTip {{
    background-color: {colors['toast_bg']};
    color: {colors['toast_text']};
    border: 1px solid {colors['border_strong']};
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 12px;
}}
"""


LIGHT_STYLE = build_style(LIGHT_COLORS)
DARK_STYLE = build_style(DARK_COLORS)
