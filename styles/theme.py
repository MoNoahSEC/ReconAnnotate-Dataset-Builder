"""
Premium Orange and White stylesheet for PyQt6.
Creates an ultra-clean, smart, and dynamic interface.
"""

BG_DARK = "#fffbf8"          # Warm Peach White background
BG_PANEL = "#fff6f0"         # Warm creamy background for panels
BG_CARD = "#ffffff"          # White cards for high contrast
BG_HOVER = "#ffebe0"         # Warm peach hover state
BG_SELECTED = "rgba(255, 107, 0, 0.15)" # Transparent orange selection highlight
BORDER = "#ffd3c4"           # Soft peach border
BORDER_FOCUS = "#ff6b00"     # Vibrant orange focus border
ACCENT = "#ff6b00"           # Premium Vibrant Orange
ACCENT_HOVER = "#ff8533"     # Bright orange hover
ACCENT_GRADIENT_START = "#ff6b00"
ACCENT_GRADIENT_END = "#ff944d"

TEXT_PRIMARY = "#1e293b"     # High readability dark slate
TEXT_SECONDARY = "#64748b"   # Slate gray for secondary details
TEXT_MUTED = "#94a3b8"       # Muted text

SUCCESS = "#ff6b00"          # Cohesive with orange
SUCCESS_HOVER = "#ff8533"
WARNING = "#ff8800"
WARNING_HOVER = "#ffa366"
DANGER = "#e05300"
DANGER_HOVER = "#ff6b00"


def get_stylesheet() -> str:
    """
    Returns the complete premium orange-white light stylesheet for PyQt6.
    Ensures beautiful pill-shaped/semi-circular buttons and smooth animations.
    """
    return f"""
    /* === Main Window & Core Widgets === */
    QMainWindow {{
        background-color: {BG_DARK};
        color: {TEXT_PRIMARY};
    }}
    
    QWidget {{
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        font-size: 13px;
        color: {TEXT_PRIMARY};
    }}
    
    QFrame {{
        border: none;
    }}
    
    /* === Left & Right Side Panels === */
    QDockWidget {{
        titlebar-close-icon: none;
        titlebar-normal-icon: none;
        border: none;
    }}
    
    QDockWidget > QWidget {{
        background-color: {BG_PANEL};
        border-right: 1px solid {BORDER};
        border-left: 1px solid {BORDER};
    }}
    
    /* === Sections Titles === */
    QLabel#SectionTitle {{
        font-size: 15px;
        font-weight: bold;
        color: {ACCENT};
        padding: 4px 0px;
    }}
    
    QLabel#SubLabel {{
        color: {TEXT_SECONDARY};
        font-size: 11px;
    }}
    
    /* === Beautiful Pill-Shaped Buttons === */
    QPushButton {{
        background-color: {BG_CARD};
        border: 2px solid {BORDER};
        border-radius: 15px;
        padding: 6px 16px;
        font-weight: bold;
        color: {TEXT_PRIMARY};
    }}
    
    QPushButton:hover {{
        background-color: {BG_HOVER};
        border-color: {ACCENT};
        color: {ACCENT};
    }}
    
    QPushButton:pressed {{
        background-color: {BG_SELECTED};
    }}
    
    QPushButton#AccentButton {{
        background-color: {ACCENT};
        border: 2px solid {ACCENT};
        color: #ffffff;
    }}
    
    QPushButton#AccentButton:hover {{
        background-color: {ACCENT_HOVER};
        border-color: {ACCENT_HOVER};
        color: #ffffff;
    }}
    
    QPushButton#DangerButton {{
        background-color: {BG_CARD};
        border: 2px solid {DANGER};
        color: {DANGER};
    }}
    
    QPushButton#DangerButton:hover {{
        background-color: {DANGER};
        border-color: {DANGER};
        color: #ffffff;
    }}
    
    /* === Smooth Input Controls === */
    QLineEdit, QSpinBox, QDoubleSpinBox {{
        background-color: {BG_CARD};
        border: 2px solid {BORDER};
        border-radius: 12px;
        padding: 5px 12px;
        color: {TEXT_PRIMARY};
    }}
    
    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
        border-color: {BORDER_FOCUS};
    }}
    
    /* === ComboBox === */
    QComboBox {{
        background-color: {BG_CARD};
        border: 2px solid {BORDER};
        border-radius: 12px;
        padding: 4px 12px;
        color: {TEXT_PRIMARY};
    }}
    
    QComboBox:on, QComboBox:focus {{
        border-color: {BORDER_FOCUS};
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 8px;
        selection-background-color: {BG_SELECTED};
        selection-color: {ACCENT};
        padding: 4px;
    }}
    
    /* === QListWidget & QTreeWidget === */
    QListWidget, QTreeWidget {{
        background-color: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 6px;
        show-decoration-selected: 1;
    }}
    
    QListWidget::item, QTreeWidget::item {{
        border-radius: 8px;
        padding: 6px;
        margin: 2px 0px;
        color: {TEXT_PRIMARY};
    }}
    
    QListWidget::item:hover, QTreeWidget::item:hover {{
        background-color: {BG_HOVER};
        color: {ACCENT};
    }}
    
    QListWidget::item:selected, QTreeWidget::item:selected {{
        background-color: {BG_SELECTED};
        color: {ACCENT};
        font-weight: bold;
    }}
    
    /* === Toolbars === */
    QToolBar {{
        background-color: {BG_PANEL};
        border-bottom: 1px solid {BORDER};
        spacing: 8px;
        padding: 6px;
    }}
    
    QToolButton {{
        background-color: {BG_CARD};
        border: 2px solid {BORDER};
        border-radius: 15px;
        padding: 5px;
        color: {TEXT_PRIMARY};
    }}
    
    QToolButton:hover {{
        background-color: {BG_HOVER};
        border-color: {ACCENT};
        color: {ACCENT};
    }}
    
    QToolButton:checked {{
        background-color: {ACCENT};
        border-color: {ACCENT};
        color: #ffffff;
    }}
    
    /* === Radio Buttons === */
    QRadioButton {{
        spacing: 8px;
        font-weight: 500;
    }}
    
    QRadioButton::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 9px;
        border: 2px solid {BORDER};
        background-color: {BG_CARD};
    }}
    
    QRadioButton::indicator:hover {{
        border-color: {ACCENT};
    }}
    
    QRadioButton::indicator:checked {{
        background-color: {ACCENT};
        border-color: {ACCENT};
    }}
    
    /* === ScrollBars === */
    QScrollBar:vertical {{
        border: none;
        background-color: {BG_DARK};
        width: 8px;
        margin: 0px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {BORDER};
        border-radius: 4px;
        min-height: 20px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {ACCENT};
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    QScrollBar:horizontal {{
        border: none;
        background-color: {BG_DARK};
        height: 8px;
        margin: 0px;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {BORDER};
        border-radius: 4px;
        min-width: 20px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {ACCENT};
    }}
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
    
    /* === Status Bar === */
    QStatusBar {{
        background-color: {BG_PANEL};
        border-top: 1px solid {BORDER};
        color: {TEXT_SECONDARY};
    }}
    
    QStatusBar QLabel {{
        color: {TEXT_SECONDARY};
    }}
    """
