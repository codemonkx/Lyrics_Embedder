"""
LyricForge GNOME / Adwaita Design System & Theme
Dark color palette, typography tokens, and Qt Style Sheets (QSS).
"""

# Color Palette Tokens (Adwaita Dark)
BG_BASE = "#1e1e1e"          # Very dark neutral gray base background
BG_SURFACE = "#242424"       # Secondary surface (HeaderBar, Sidebar, Toolbars)
BG_ELEVATED = "#2d2d2d"      # Elevated surface (Cards, Rows, Inputs)
BG_HOVER = "#353535"         # Surface hover state
BG_ACTIVE = "#3e3e3e"        # Surface pressed/active state

BORDER_SUBTLE = "#303030"     # Low-contrast subtle border
BORDER_FOCUS = "#3584e4"      # Focus border accent

ACCENT_BLUE = "#3584e4"       # GNOME Blue accent
ACCENT_BLUE_HOVER = "#1c71d8"
ACCENT_BLUE_ACTIVE = "#1553a1"

TEXT_PRIMARY = "#ffffff"     # High-contrast off-white
TEXT_SECONDARY = "#9a9996"   # Muted gray
TEXT_MUTED = "#77767b"       # Subtext / Metadata

COLOR_SUCCESS = "#2ec27e"    # Green
COLOR_WARNING = "#e5a50a"    # Yellow/Orange
COLOR_ERROR = "#e01b24"      # Red

ADWAITA_DARK_QSS = f"""
/* Global Reset & Typography */
QWidget {{
    color: {TEXT_PRIMARY};
    font-family: "Cantarell", "Inter", "Segoe UI", system-ui, sans-serif;
    font-size: 10pt;
    background: transparent;
}}

QMainWindow {{
    background-color: {BG_BASE};
}}

QWidget#central {{
    background-color: {BG_BASE};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 8px;
}}

/* Tooltips */
QToolTip {{
    background-color: {BG_ELEVATED};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 9pt;
}}

/* Frames & Panels */
QFrame#sidebarFrame {{
    background-color: {BG_SURFACE};
    border-right: 1px solid {BORDER_SUBTLE};
    border-top-left-radius: 0px;
    border-bottom-left-radius: 8px;
}}

QFrame#headerFrame {{
    background-color: {BG_SURFACE};
    border-bottom: 1px solid {BORDER_SUBTLE};
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}}

QFrame#cardFrame, QWidget.adwCard {{
    background-color: {BG_ELEVATED};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 8px;
}}

/* Scroll Areas */
QScrollArea {{
    border: none;
    background-color: transparent;
}}

QScrollArea > QWidget > QWidget {{
    background-color: transparent;
}}

/* Typography Classes */
QLabel.pageTitle {{
    font-size: 16pt;
    font-weight: 700;
    color: {TEXT_PRIMARY};
}}

QLabel.pageSubtitle {{
    font-size: 10pt;
    color: {TEXT_SECONDARY};
}}

QLabel.sectionTitle {{
    font-size: 9pt;
    font-weight: 700;
    color: {TEXT_SECONDARY};
    letter-spacing: 0.5px;
    text-transform: uppercase;
}}

QLabel.mutedLabel {{
    color: {TEXT_MUTED};
    font-size: 9pt;
}}

/* Buttons */
QPushButton {{
    background-color: {BG_ELEVATED};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 6px;
    padding: 6px 14px;
    color: {TEXT_PRIMARY};
    font-weight: 500;
    font-size: 10pt;
    min-height: 20px;
}}

QPushButton:hover {{
    background-color: {BG_HOVER};
    border-color: #3e3e3e;
}}

QPushButton:pressed {{
    background-color: {BG_ACTIVE};
}}

QPushButton:disabled {{
    background-color: #242424;
    border-color: {BORDER_SUBTLE};
    color: {TEXT_MUTED};
}}

/* Primary Button (GNOME Blue) */
QPushButton#primaryButton, QPushButton.primaryButton {{
    background-color: {ACCENT_BLUE};
    border: 1px solid {ACCENT_BLUE_HOVER};
    color: #ffffff;
    font-weight: 600;
}}

QPushButton#primaryButton:hover, QPushButton.primaryButton:hover {{
    background-color: {ACCENT_BLUE_HOVER};
}}

QPushButton#primaryButton:pressed, QPushButton.primaryButton:pressed {{
    background-color: {ACCENT_BLUE_ACTIVE};
}}

QPushButton#primaryButton:disabled, QPushButton.primaryButton:disabled {{
    background-color: #28374d;
    border-color: #242e3d;
    color: #62748a;
}}

/* Destructive Button (GNOME Red) */
QPushButton#destructiveButton, QPushButton.destructiveButton {{
    background-color: {COLOR_ERROR};
    border: 1px solid #c01c28;
    color: #ffffff;
    font-weight: 600;
}}

QPushButton#destructiveButton:hover, QPushButton.destructiveButton:hover {{
    background-color: #c01c28;
}}

QPushButton#destructiveButton:pressed, QPushButton.destructiveButton:pressed {{
    background-color: #a0141e;
}}

/* Sidebar Navigation Buttons */
QPushButton.navRow {{
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 8px 12px;
    text-align: left;
    color: {TEXT_SECONDARY};
    font-weight: 500;
    font-size: 10pt;
}}

QPushButton.navRow:hover {{
    background-color: {BG_HOVER};
    color: {TEXT_PRIMARY};
}}

QPushButton.navRowActive {{
    background-color: {BG_ELEVATED};
    border: 1px solid {BORDER_SUBTLE};
    border-left: 3px solid {ACCENT_BLUE};
    border-radius: 6px;
    padding: 8px 12px;
    text-align: left;
    color: {TEXT_PRIMARY};
    font-weight: 600;
    font-size: 10pt;
}}

/* Input Fields */
QLineEdit {{
    background-color: {BG_ELEVATED};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 6px;
    padding: 6px 10px;
    color: {TEXT_PRIMARY};
    selection-background-color: {ACCENT_BLUE};
    font-size: 10pt;
}}

QLineEdit:focus {{
    border: 1px solid {BORDER_FOCUS};
}}

QTextEdit {{
    background-color: {BG_ELEVATED};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 6px;
    color: {TEXT_PRIMARY};
    padding: 8px;
    selection-background-color: {ACCENT_BLUE};
    font-size: 10pt;
}}

QTextEdit:focus {{
    border: 1px solid {BORDER_FOCUS};
}}

/* Table Widget (GNOME List Style) */
QTableWidget {{
    background-color: transparent;
    alternate-background-color: #242424;
    gridline-color: transparent;
    border: none;
    outline: none;
}}

QTableWidget::item {{
    border-bottom: 1px solid {BORDER_SUBTLE};
    padding: 8px 10px;
    color: {TEXT_PRIMARY};
    font-size: 10pt;
}}

QTableWidget::item:selected {{
    background-color: #26384f;
    color: #ffffff;
}}

QTableWidget::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid #4a4a4a;
    border-radius: 4px;
    background-color: {BG_ELEVATED};
}}

QTableWidget::indicator:checked {{
    background-color: {ACCENT_BLUE};
    border-color: {ACCENT_BLUE};
    image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgd2lkdGg9IjE2IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS13aWR0aD0iMyIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cG9seWxpbmUgcG9pbnRzPSIyMCA2IDkgMTcgNCAxMiIvPjwvc3ZnPg==);
}}

QHeaderView::section {{
    background-color: {BG_SURFACE};
    color: {TEXT_SECONDARY};
    padding: 8px 10px;
    border: none;
    border-bottom: 1px solid {BORDER_SUBTLE};
    font-weight: 600;
    font-size: 9pt;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* Checkboxes & Sliders */
QCheckBox {{
    spacing: 8px;
    color: {TEXT_PRIMARY};
    font-size: 10pt;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid #4a4a4a;
    border-radius: 4px;
    background-color: {BG_ELEVATED};
}}

QCheckBox::indicator:checked {{
    background-color: {ACCENT_BLUE};
    border-color: {ACCENT_BLUE};
    image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgd2lkdGg9IjE2IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS13aWR0aD0iMyIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cG9seWxpbmUgcG9pbnRzPSIyMCA2IDkgMTcgNCAxMiIvPjwvc3ZnPg==);
}}

QSlider::groove:horizontal {{
    border: none;
    height: 4px;
    background: {BORDER_SUBTLE};
    border-radius: 2px;
}}

QSlider::sub-page:horizontal {{
    background: {ACCENT_BLUE};
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    background: #ffffff;
    border: 1px solid {BORDER_SUBTLE};
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}}

QSlider::handle:horizontal:hover {{
    background: #ffffff;
    border-color: {ACCENT_BLUE};
}}

/* Progress Bar */
QProgressBar {{
    border: none;
    border-radius: 3px;
    background-color: {BG_ELEVATED};
    text-align: center;
    color: transparent;
    height: 6px;
}}

QProgressBar::chunk {{
    background-color: {ACCENT_BLUE};
    border-radius: 3px;
}}

/* Scrollbars */
QScrollBar:vertical {{
    border: none;
    background: transparent;
    width: 8px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background: #3e3e3e;
    min-height: 24px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background: #505050;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    border: none;
    background: none;
}}

QScrollBar:horizontal {{
    border: none;
    background: transparent;
    height: 8px;
    margin: 0px;
}}

QScrollBar::handle:horizontal {{
    background: #3e3e3e;
    min-width: 24px;
    border-radius: 4px;
}}

QScrollBar::handle:horizontal:hover {{
    background: #505050;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    border: none;
    background: none;
}}

/* Context Menu */
QMenu {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 8px;
    padding: 4px;
}}

QMenu::item {{
    padding: 6px 16px;
    color: {TEXT_PRIMARY};
    border-radius: 4px;
    font-size: 10pt;
}}

QMenu::item:selected {{
    background-color: {ACCENT_BLUE};
    color: #ffffff;
}}

QMenu::separator {{
    height: 1px;
    background-color: {BORDER_SUBTLE};
    margin: 4px 8px;
}}
"""
