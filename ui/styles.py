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
    "sidebar_active_bg": "rgba(79, 70, 229, 0.18)",
    "sidebar_active_border": "#818cf8",
    "sidebar_active_text": "#ffffff",
    "accent": "#4f46e5",
    "accent_hover": "#4338ca",
    "accent_pressed": "#3730a3",
    "accent_soft": "#eef2ff",
    "content_bg": "#f7f8fa",
    "text_primary": "#14161f",
    "text_secondary": "#6b7280",
    "page_title": "#14161f",
    "page_subtitle": "#6b7280",
    "card_bg": "#ffffff",
    "card_border": "#e5e7eb",
    "card_border_hover": "#c7d2fe",
    "input_bg": "#ffffff",
    "input_border": "#d8dae2",
    "input_text": "#14161f",
    "combo_popup_bg": "#ffffff",
    "preview_bg": "#fafafc",
    "preview_border": "#dfe1e8",
    "drag_active_bg": "#eef2ff",
    "drag_active_border": "#4f46e5",
    "scroll_track": "#f1f2f6",
    "scroll_handle": "#cfd2dc",
    "scroll_handle_hover": "#adb1c0",
    "toast_bg": "#14161f",
    "toast_text": "#f7f8fa",
    "success": "#22c55e",
    "error": "#f87171",
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
    "sidebar_active_bg": "rgba(99, 102, 241, 0.22)",
    "sidebar_active_border": "#818cf8",
    "sidebar_active_text": "#ffffff",
    "accent": "#6366f1",
    "accent_hover": "#7c7ff0",
    "accent_pressed": "#4f46e5",
    "accent_soft": "#181a2e",
    "content_bg": "#0e1017",
    "text_primary": "#e7e8ee",
    "text_secondary": "#9397a8",
    "page_title": "#f5f6fa",
    "page_subtitle": "#9397a8",
    "card_bg": "#14161f",
    "card_border": "#20222e",
    "card_border_hover": "#3f3f8f",
    "input_bg": "#0e1017",
    "input_border": "#262838",
    "input_text": "#e7e8ee",
    "combo_popup_bg": "#14161f",
    "preview_bg": "#0e1017",
    "preview_border": "#20222e",
    "drag_active_bg": "#181a2e",
    "drag_active_border": "#6366f1",
    "scroll_track": "#0e1017",
    "scroll_handle": "#262838",
    "scroll_handle_hover": "#33354a",
    "toast_bg": "#1b1d29",
    "toast_text": "#f5f6fa",
    "success": "#4ade80",
    "error": "#f87171",
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
    font-family: "Roboto";
    color: {colors['app_title']};
    font-size: 20px;
    font-weight: 700;
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
    font-family: "Roboto";
    color: {colors['page_title']};
    font-size: 26px;
    font-weight: 700;
    background-color: transparent;
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
    border-radius: 12px;
}}

QFrame#toolCard:hover {{
    border: 1px solid {colors['card_border_hover']};
}}

QLabel#toolTitle {{
    font-family: "Roboto Medium";
    color: {colors['text_primary']};
    background-color: transparent;
    font-size: 16px;
}}

QLabel#toolDescription {{
    font-family: "Roboto";
    color: {colors['text_secondary']};
    background-color: transparent;
    font-size: 12.5px;
}}

QLabel#fieldLabel {{
    font-family: "Roboto Medium";
    color: {colors['text_secondary']};
    background-color: transparent;
    font-size: 12px;
}}

/* =========================
   BUTTONS
   ========================= */

QPushButton#toolButton {{
    font-family: "Roboto Medium";
    background-color: {colors['accent']};
    color: #ffffff;
    border: none;
    border-radius: 8px;
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
    font-family: "Roboto Medium";
    background-color: transparent;
    color: {colors['accent']};
    border: 1px solid {colors['card_border']};
    border-radius: 8px;
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
    border-radius: 8px;
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
    border-radius: 8px;
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
    border-radius: 12px;
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
   TOAST
   ========================= */

QFrame#toast {{
    background-color: {colors['toast_bg']};
    border-radius: 10px;
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
    background: {colors['scroll_track']};
    width: 10px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background: {colors['scroll_handle']};
    border-radius: 5px;
}}

QScrollBar::handle:vertical:hover {{
    background: {colors['scroll_handle_hover']};
}}
"""


LIGHT_STYLE = build_style(LIGHT_COLORS)
DARK_STYLE = build_style(DARK_COLORS)
