"""
Image categorization panel — Good / Bad / Empty classification.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QRadioButton, QLabel, QButtonGroup, QFrame
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import pyqtSignal
from ..models.image_entry import ImageCategory
from ..styles.theme import SUCCESS, DANGER, TEXT_MUTED


class CategoryPanel(QWidget):
    """Docstring"""
    category_changed = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Docstring"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        title = QLabel("Image Classification")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)

        desc = QLabel("Select category before/after drawing")
        desc.setObjectName("SubLabel")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        self._group = QButtonGroup(self)

        self._good_btn = QRadioButton("Good (No Defects)")
        self._good_btn.setStyleSheet(f"QRadioButton::indicator:checked {{ background-color: {SUCCESS}; border-color: {SUCCESS}; }}")
        self._group.addButton(self._good_btn, 0)
        layout.addWidget(self._good_btn)

        self._bad_btn = QRadioButton("Bad (Defect - Needs Annotation)")
        self._bad_btn.setStyleSheet(f"QRadioButton::indicator:checked {{ background-color: {DANGER}; border-color: {DANGER}; }}")
        self._group.addButton(self._bad_btn, 1)
        layout.addWidget(self._bad_btn)

        self._empty_btn = QRadioButton("Empty (Unsuitable - Excluded)")
        self._group.addButton(self._empty_btn, 2)
        layout.addWidget(self._empty_btn)

        self._group.buttonClicked.connect(self._on_changed)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: rgba(255,255,255,0.08);")
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        self._status = QLabel("")
        self._status.setObjectName("SubLabel")
        self._status.setWordWrap(True)
        layout.addWidget(self._status)

    def _on_changed(self, btn):
        """Docstring"""
        bid = self._group.id(btn)
        mapping = {0: ImageCategory.GOOD, 1: ImageCategory.BAD, 2: ImageCategory.EMPTY}
        cat = mapping.get(bid, ImageCategory.UNCLASSIFIED)
        self.category_changed.emit(cat)
        self._update_status(cat)

    def _update_status(self, cat):
        """Docstring"""
        if cat == ImageCategory.GOOD:
            self._status.setText("→ Will be saved as background (no label)")
            self._status.setStyleSheet(f"color: {SUCCESS};")
        elif cat == ImageCategory.BAD:
            self._status.setText("→ Draw defects to annotate")
            self._status.setStyleSheet(f"color: {DANGER};")
        elif cat == ImageCategory.EMPTY:
            self._status.setText("→ Will be excluded from dataset")
            self._status.setStyleSheet(f"color: {TEXT_MUTED};")
        else:
            self._status.setText("")

    def set_category(self, category: ImageCategory):
        """Docstring"""
        self._group.blockSignals(True)
        if category == ImageCategory.GOOD:
            self._good_btn.setChecked(True)
        elif category == ImageCategory.BAD:
            self._bad_btn.setChecked(True)
        elif category == ImageCategory.EMPTY:
            self._empty_btn.setChecked(True)
        else:
            self._group.setExclusive(False)
            self._good_btn.setChecked(False)
            self._bad_btn.setChecked(False)
            self._empty_btn.setChecked(False)
            self._group.setExclusive(True)
        self._group.blockSignals(False)
        self._update_status(category)
