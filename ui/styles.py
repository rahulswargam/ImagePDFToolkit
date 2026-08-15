LIGHT_COLORS = {
    "window_bg": "#f7f8fa",
    "sidebar_bg": "#14161f",
    "sidebar_border": "#20222e",
    "app_title": "#ffffff",
    "sidebar_subtitle": "#8b8fa3",
    "section_label": "#6b6f85",
    "sidebar_button_text": "#c4c7d4",
    "sidebar_button_hover_bg": "rgba(255, 255, 255, 0.06)",
    "sidebar_button_hover_text": "#ffffff",
    "sidebar_active_bg": "rgba(220, 38, 38, 0.18)",
    "sidebar_active_border": "#f87171",
    "sidebar_active_text": "#ffffff",
    "accent": "#dc2626",
    "accent_hover": "#b91c1c",
    "accent_pressed": "#991b1b",
    "accent_soft": "#fef2f2",
    "content_bg": "#f7f8fa",
    "text_primary": "#14161f",
    "text_secondary": "#565c6d",
    "page_title": "#14161f",
    "page_subtitle": "#565c6d",
    "card_bg": "#ffffff",
    "card_border": "#e5e7eb",
    "card_border_hover": "#fca5a5",
    "input_bg": "#ffffff",
    "input_border": "#d8dae2",
    "input_text": "#14161f",
    "combo_popup_bg": "#ffffff",
    "preview_bg": "#fafafc",
    "preview_border": "#dfe1e8",
    "drag_active_bg": "#fef2f2",
    "drag_active_border": "#dc2626",
    "scroll_track": "#f1f2f6",
    "scroll_handle": "#cfd2dc",
    "scroll_handle_hover": "#adb1c0",
    "toast_bg": "#14161f",
    "toast_text": "#f7f8fa",
    "success": "#16a34a",
    "error": "#f97316",
    "footer_text": "#5b5f72",
    "footer_border": "#20222e",
}

DARK_COLORS = {
    "window_bg": "#0a0b10",
    "sidebar_bg": "#0a0b10",
    "sidebar_border": "#1b1d29",
    "app_title": "#ffffff",
    "sidebar_subtitle": "#8b8fa3",
    "section_label": "#5b5f72",
    "sidebar_button_text": "#b7bacb",
    "sidebar_button_hover_bg": "rgba(255, 255, 255, 0.05)",
    "sidebar_button_hover_text": "#ffffff",
    "sidebar_active_bg": "rgba(239, 68, 68, 0.22)",
    "sidebar_active_border": "#f87171",
    "sidebar_active_text": "#ffffff",
    "accent": "#ef4444",
    "accent_hover": "#f87171",
    "accent_pressed": "#dc2626",
    "accent_soft": "#2a1212",
    "content_bg": "#0e1017",
    "text_primary": "#e7e8ee",
    "text_secondary": "#9397a8",
    "page_title": "#f5f6fa",
    "page_subtitle": "#9397a8",
    "card_bg": "#14161f",
    "card_border": "#20222e",
    "card_border_hover": "#991b1b",
    "input_bg": "#0e1017",
    "input_border": "#262838",
    "input_text": "#e7e8ee",
    "combo_popup_bg": "#14161f",
    "preview_bg": "#0e1017",
    "preview_border": "#20222e",
    "drag_active_bg": "#2a1212",
    "drag_active_border": "#ef4444",
    "scroll_track": "#0e1017",
    "scroll_handle": "#262838",
    "scroll_handle_hover": "#33354a",
    "toast_bg": "#1b1d29",
    "toast_text": "#f5f6fa",
    "success": "#4ade80",
    "error": "#fb923c",
    "footer_text": "#5b5f72",
    "footer_border": "#1b1d29",
}


def build_style(colors):
    return f"""
QMainWindow {{
    background-color: {colors['window_bg']};
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
    color: {colors['app_title']};
    font-size: 20px;
}}

#sidebarSubtitle {{
    font-family: "Roboto Medium";
    color: {colors['sidebar_subtitle']};
    font-size: 11px;
    letter-spacing: 2px;
}}

#sectionLabel {{
    font-family: "Roboto Medium";
    color: {colors['section_label']};
    font-size: 11px;
    letter-spacing: 1px;
    background-color: transparent;
}}

QPushButton#sidebarButton {{
    font-family: "Roboto";
    background-color: transparent;
    color: {colors['sidebar_button_text']};
    border: none;
    border-left: 3px solid transparent;
    text-align: left;
    padding: 11px 16px;
    font-size: 13.5px;
}}

QPushButton#sidebarButton:hover {{
    background-color: {colors['sidebar_button_hover_bg']};
    color: {colors['sidebar_button_hover_text']};
}}

QPushButton#sidebarButton:checked {{
    background-color: {colors['sidebar_active_bg']};
    border-left: 3px solid {colors['sidebar_active_border']};
    color: {colors['sidebar_active_text']};
    font-family: "Roboto Medium";
}}

QPushButton#themeToggle {{
    font-family: "Roboto";
    background-color: transparent;
    color: {colors['sidebar_button_text']};
    border: 1px solid {colors['sidebar_border']};
    border-radius: 8px;
    padding: 9px 14px;
    text-align: left;
    font-size: 13px;
}}

QPushButton#themeToggle:hover {{
    background-color: {colors['sidebar_button_hover_bg']};
    color: #ffffff;
}}

#sidebarFooter {{
    color: {colors['footer_text']};
    font-size: 11px;
    background-color: transparent;
    border-top: 1px solid {colors['footer_border']};
    padding-top: 12px;
}}

/* =========================
   MAIN CONTENT
   ========================= */

#contentArea {{
    background-color: {colors['content_bg']};
}}

#breadcrumb {{
    font-family: "Roboto Medium";
    color: {colors['text_secondary']};
    font-size: 12.5px;
    background-color: transparent;
}}

#pageTitle {{
    font-family: "Roboto Black";
    color: {colors['page_title']};
    font-size: 30px;
    background-color: transparent;
}}

#heroBadge {{
    font-family: "Roboto SemiBold";
    color: {colors['accent']};
    background-color: {colors['accent_soft']};
    border: 1px solid {colors['card_border_hover']};
    border-radius: 12px;
    font-size: 11px;
    letter-spacing: 1.5px;
    padding: 6px 14px;
}}

#pageSubtitle {{
    font-family: "Roboto";
    color: {colors['page_subtitle']};
    font-size: 13.5px;
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
   CARDS
   ========================= */

QFrame#toolCard {{
    background-color: {colors['card_bg']};
    border: 1px solid {colors['card_border']};
    border-radius: 18px;
}}

QFrame#toolCard:hover {{
    border: 1.5px solid {colors['card_border_hover']};
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

/* =========================
   BUTTONS
   ========================= */

QPushButton#toolButton {{
    font-family: "Roboto SemiBold";
    background-color: {colors['accent']};
    color: #ffffff;
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

QPushButton#secondaryButton {{
    font-family: "Roboto SemiBold";
    background-color: transparent;
    color: {colors['accent']};
    border: 1px solid {colors['card_border']};
    border-radius: 12px;
    padding: 9px 16px;
    font-size: 13.5px;
}}

QPushButton#secondaryButton:hover {{
    border: 1px solid {colors['accent']};
    background-color: {colors['accent_soft']};
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
   PREVIEW / DROP AREA
   ========================= */

#previewFrame {{
    background-color: {colors['preview_bg']};
    border: 1.5px dashed {colors['preview_border']};
    border-radius: 16px;
    color: {colors['text_secondary']};
    font-size: 13px;
    padding: 10px;
}}

#previewFrame[dragActive="true"] {{
    background-color: {colors['drag_active_bg']};
    border: 1.5px dashed {colors['drag_active_border']};
    color: {colors['accent']};
}}

/* =========================
   FILE ROW (batch file lists)
   ========================= */

QFrame#fileRow {{
    background-color: {colors['preview_bg']};
    border: 1px solid {colors['preview_border']};
    border-radius: 12px;
}}

QFrame#fileRow:hover {{
    border: 1px solid {colors['card_border_hover']};
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
    color: {colors['text_secondary']};
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
"""


LIGHT_STYLE = build_style(LIGHT_COLORS)
DARK_STYLE = build_style(DARK_COLORS)
