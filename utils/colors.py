"""
Distinct color palette for annotation classes.
"""
from PyQt6.QtGui import QColor

CLASS_COLORS = [
    QColor(255, 85, 85),
    QColor(85, 255, 85),
    QColor(85, 170, 255),
    QColor(255, 255, 85),
    QColor(255, 85, 255),
    QColor(85, 255, 255),
    QColor(255, 170, 85),
    QColor(170, 85, 255),
    QColor(85, 255, 170),
    QColor(255, 85, 170),
    QColor(170, 255, 85),
    QColor(85, 170, 170),
    QColor(255, 200, 150),
    QColor(150, 150, 255),
    QColor(255, 150, 200),
    QColor(200, 255, 150),
    QColor(150, 255, 255),
    QColor(255, 220, 100),
    QColor(180, 100, 255),
    QColor(100, 255, 200),
]


def get_class_color(class_index: int) -> QColor:
    """Docstring"""
    return CLASS_COLORS[class_index % len(CLASS_COLORS)]


def get_class_color_with_alpha(class_index: int, alpha: int = 60) -> QColor:
    """Docstring"""
    color = QColor(get_class_color(class_index))
    color.setAlpha(alpha)
    return color


def get_class_color_hex(class_index: int) -> str:
    """Docstring"""
    c = get_class_color(class_index)
    return c.name()
