"""
Toolbar panel — mode selection, undo/redo, save, export, and train/val slider.
"""
from PyQt6.QtWidgets import (
    QToolBar, QToolButton, QWidget, QHBoxLayout, QLabel,
    QSlider, QButtonGroup, QPushButton, QSizePolicy
)
from PyQt6.QtGui import QAction, QIcon, QFont
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from ..canvas.scene import DrawMode


class ToolBar(QToolBar):
    """Docstring"""
    mode_changed = pyqtSignal(object)
    undo_requested = pyqtSignal()
    redo_requested = pyqtSignal()
    save_requested = pyqtSignal()
    export_requested = pyqtSignal()
    fit_requested = pyqtSignal()
    split_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__("Tools", parent)
        self.setMovable(False)
        self.setIconSize(QSize(20, 20))
        self._setup_ui()

    def _setup_ui(self):
        """Docstring"""
        self._mode_group = QButtonGroup(self)
        self._mode_group.setExclusive(True)

        self._bbox_btn = QToolButton()
        self._bbox_btn.setText("BBox")
        self._bbox_btn.setCheckable(True)
        self._bbox_btn.setToolTip("Bounding Box mode (B)")
        self._mode_group.addButton(self._bbox_btn, 0)
        self.addWidget(self._bbox_btn)

        self._poly_btn = QToolButton()
        self._poly_btn.setText("Polygon")
        self._poly_btn.setCheckable(True)
        self._poly_btn.setToolTip("Polygon mode (P)")
        self._mode_group.addButton(self._poly_btn, 1)
        self.addWidget(self._poly_btn)

        self._free_btn = QToolButton()
        self._free_btn.setText("Freehand")
        self._free_btn.setCheckable(True)
        self._free_btn.setToolTip("Freehand mode → auto polygon (H)")
        self._mode_group.addButton(self._free_btn, 2)
        self.addWidget(self._free_btn)

        self._edit_btn = QToolButton()
        self._edit_btn.setText("Edit")
        self._edit_btn.setCheckable(True)
        self._edit_btn.setToolTip("Edit mode — select, move, delete (E)")
        self._mode_group.addButton(self._edit_btn, 3)
        self.addWidget(self._edit_btn)

        self._mode_group.buttonClicked.connect(self._on_mode_changed)

        self.addSeparator()

        undo_btn = QToolButton()
        undo_btn.setText("Undo")
        undo_btn.setToolTip("Undo (Ctrl+Z)")
        undo_btn.clicked.connect(self.undo_requested.emit)
        self.addWidget(undo_btn)

        redo_btn = QToolButton()
        redo_btn.setText("Redo")
        redo_btn.setToolTip("Redo (Ctrl+Y)")
        redo_btn.clicked.connect(self.redo_requested.emit)
        self.addWidget(redo_btn)

        self.addSeparator()

        fit_btn = QToolButton()
        fit_btn.setText("Fit")
        fit_btn.setToolTip("Fit image to view (F)")
        fit_btn.clicked.connect(self.fit_requested.emit)
        self.addWidget(fit_btn)

        save_btn = QToolButton()
        save_btn.setText("Save")
        save_btn.setToolTip("Save project (Ctrl+S)")
        save_btn.clicked.connect(self.save_requested.emit)
        self.addWidget(save_btn)

        self.addSeparator()

        split_widget = QWidget()
        split_layout = QHBoxLayout(split_widget)
        split_layout.setContentsMargins(4, 0, 4, 0)
        split_layout.setSpacing(6)

        split_layout.addWidget(QLabel("Train:"))
        self._split_slider = QSlider(Qt.Orientation.Horizontal)
        self._split_slider.setRange(50, 95)
        self._split_slider.setValue(80)
        self._split_slider.setFixedWidth(100)
        self._split_slider.setToolTip("Train/Val split ratio")
        self._split_slider.valueChanged.connect(self._on_split_changed)
        split_layout.addWidget(self._split_slider)

        self._split_label = QLabel("80%")
        self._split_label.setFixedWidth(35)
        split_layout.addWidget(self._split_label)

        self.addWidget(split_widget)

        self.addSeparator()

        export_btn = QToolButton()
        export_btn.setText("Export Dataset")
        export_btn.setToolTip("Export normalized dataset (Ctrl+E)")
        export_btn.setObjectName("AccentToolButton")
        export_btn.clicked.connect(self.export_requested.emit)
        self.addWidget(export_btn)

    def _on_mode_changed(self, btn):
        """Docstring"""
        bid = self._mode_group.id(btn)
        modes = {0: DrawMode.BBOX, 1: DrawMode.POLYGON, 2: DrawMode.FREEHAND, 3: DrawMode.EDIT}
        self.mode_changed.emit(modes.get(bid, DrawMode.NONE))

    def _on_split_changed(self, val):
        """Docstring"""
        self._split_label.setText(f"{val}%")
        self.split_changed.emit(val)

    def get_split_ratio(self) -> float:
        """Docstring"""
        return self._split_slider.value() / 100.0

    def set_mode_bbox(self):
        self._bbox_btn.setChecked(True)
        self._on_mode_changed(self._bbox_btn)

    def set_mode_polygon(self):
        self._poly_btn.setChecked(True)
        self._on_mode_changed(self._poly_btn)

    def set_mode_edit(self):
        self._edit_btn.setChecked(True)
        self._on_mode_changed(self._edit_btn)

    def set_mode_freehand(self):
        self._free_btn.setChecked(True)
        self._on_mode_changed(self._free_btn)
