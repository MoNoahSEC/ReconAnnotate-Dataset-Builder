"""
Annotation list panel — shows all annotations on the current image.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QComboBox
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush
from PyQt6.QtCore import Qt, pyqtSignal
from ..utils.colors import get_class_color
from ..models.annotation import BBoxAnnotation, PolygonAnnotation


class AnnotationPanel(QWidget):
    """Docstring"""
    annotation_selected = pyqtSignal(str)
    annotation_delete_requested = pyqtSignal(str)
    annotation_class_change = pyqtSignal(str, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._annotations = []
        self._class_names = []
        self._setup_ui()

    def _setup_ui(self):
        """Docstring"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        title = QLabel("Annotations")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)

        self._count_label = QLabel("0 annotations")
        self._count_label.setObjectName("SubLabel")
        layout.addWidget(self._count_label)

        self._list = QListWidget()
        self._list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self._list.currentRowChanged.connect(self._on_selection_changed)
        layout.addWidget(self._list)

        btn_row = QHBoxLayout()
        del_btn = QPushButton("Delete")
        del_btn.setObjectName("DangerButton")
        del_btn.clicked.connect(self._on_delete)
        btn_row.addWidget(del_btn)

        del_all_btn = QPushButton("Clear All")
        del_all_btn.setObjectName("DangerButton")
        del_all_btn.clicked.connect(self._on_delete_all)
        btn_row.addWidget(del_all_btn)
        layout.addLayout(btn_row)

        cls_row = QHBoxLayout()
        cls_row.addWidget(QLabel("Change to:"))
        self._class_combo = QComboBox()
        self._class_combo.currentIndexChanged.connect(self._on_class_change)
        cls_row.addWidget(self._class_combo)
        layout.addLayout(cls_row)

    def _make_type_icon(self, ann, class_id):
        """Docstring"""
        px = QPixmap(20, 20)
        px.fill(Qt.GlobalColor.transparent)
        painter = QPainter(px)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = get_class_color(class_id)
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        if isinstance(ann, BBoxAnnotation):
            painter.drawRect(2, 2, 16, 16)
        else:
            from PyQt6.QtGui import QPolygonF
            from PyQt6.QtCore import QPointF
            poly = QPolygonF([QPointF(10,2), QPointF(18,14), QPointF(2,14)])
            painter.drawPolygon(poly)
        painter.end()
        return QIcon(px)

    def _on_selection_changed(self, row):
        """Docstring"""
        if 0 <= row < len(self._annotations):
            self.annotation_selected.emit(self._annotations[row].uid)

    def _on_delete(self):
        """Docstring"""
        row = self._list.currentRow()
        if 0 <= row < len(self._annotations):
            self.annotation_delete_requested.emit(self._annotations[row].uid)

    def _on_delete_all(self):
        """Docstring"""
        for ann in list(self._annotations):
            self.annotation_delete_requested.emit(ann.uid)

    def _on_class_change(self, index):
        """Docstring"""
        row = self._list.currentRow()
        if 0 <= row < len(self._annotations) and index >= 0:
            uid = self._annotations[row].uid
            self.annotation_class_change.emit(uid, index)

    def refresh(self, annotations, class_names):
        """Docstring"""
        self._annotations = list(annotations)
        self._class_names = list(class_names)

        self._list.blockSignals(True)
        self._list.clear()
        for ann in self._annotations:
            cname = class_names[ann.class_id] if ann.class_id < len(class_names) else "?"
            type_str = "□" if isinstance(ann, BBoxAnnotation) else "⬡"
            icon = self._make_type_icon(ann, ann.class_id)
            item = QListWidgetItem(icon, f"{type_str} {cname} [{ann.uid}]")
            self._list.addItem(item)
        self._list.blockSignals(False)

        self._count_label.setText(f"{len(self._annotations)} annotations")

        self._class_combo.blockSignals(True)
        self._class_combo.clear()
        for name in class_names:
            self._class_combo.addItem(name)
        self._class_combo.blockSignals(False)

    def highlight(self, uid):
        """Docstring"""
        for i, ann in enumerate(self._annotations):
            if ann.uid == uid:
                self._list.blockSignals(True)
                self._list.setCurrentRow(i)
                self._list.blockSignals(False)
                return
