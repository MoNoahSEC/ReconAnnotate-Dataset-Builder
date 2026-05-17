"""
Class manager panel — add, edit, delete, and select annotation classes.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QLineEdit, QLabel,
    QInputDialog, QMessageBox, QSizePolicy
)
from PyQt6.QtGui import QColor, QIcon, QPixmap, QPainter, QBrush
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from ..utils.colors import get_class_color


class ClassPanel(QWidget):
    """Docstring"""
    class_selected = pyqtSignal(int, str)
    class_added = pyqtSignal(str)
    class_removed = pyqtSignal(int)
    class_renamed = pyqtSignal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Docstring"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        title = QLabel("Classes")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)

        add_row = QHBoxLayout()
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("New class name...")
        self._name_input.returnPressed.connect(self._on_add)
        add_row.addWidget(self._name_input)

        add_btn = QPushButton("+ Add")
        add_btn.setObjectName("AccentButton")
        add_btn.setFixedWidth(70)
        add_btn.clicked.connect(self._on_add)
        add_row.addWidget(add_btn)
        layout.addLayout(add_row)

        self._list = QListWidget()
        self._list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self._list.currentRowChanged.connect(self._on_selection_changed)
        self._list.itemDoubleClicked.connect(self._on_rename)
        layout.addWidget(self._list)

        btn_row = QHBoxLayout()
        rename_btn = QPushButton("Rename")
        rename_btn.clicked.connect(self._on_rename_btn)
        btn_row.addWidget(rename_btn)

        del_btn = QPushButton("Delete")
        del_btn.setObjectName("DangerButton")
        del_btn.clicked.connect(self._on_delete)
        btn_row.addWidget(del_btn)
        layout.addLayout(btn_row)

        hint = QLabel("Shortcuts: 1-9 to select class")
        hint.setObjectName("SubLabel")
        layout.addWidget(hint)

    def _make_color_icon(self, index):
        """Docstring"""
        px = QPixmap(16, 16)
        px.fill(Qt.GlobalColor.transparent)
        painter = QPainter(px)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = get_class_color(index)
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, 12, 12)
        painter.end()
        return QIcon(px)

    def _on_add(self):
        """Docstring"""
        name = self._name_input.text().strip()
        if name:
            self._name_input.clear()
            self.class_added.emit(name)

    def _on_selection_changed(self, row):
        """Docstring"""
        if row >= 0:
            item = self._list.item(row)
            if item:
                self.class_selected.emit(row, item.text())

    def _on_rename_btn(self):
        """Docstring"""
        item = self._list.currentItem()
        if item:
            self._on_rename(item)

    def _on_rename(self, item=None):
        """Docstring"""
        if not item:
            item = self._list.currentItem()
        if not item:
            return
        row = self._list.row(item)
        new_name, ok = QInputDialog.getText(
            self, "Rename Class", "New name:", text=item.text()
        )
        if ok and new_name.strip():
            self.class_renamed.emit(row, new_name.strip())

    def _on_delete(self):
        """Docstring"""
        row = self._list.currentRow()
        if row < 0:
            return
        name = self._list.item(row).text()
        reply = QMessageBox.question(
            self, "Delete Class",
            f"Delete class '{name}'?\nAll annotations with this class will be removed.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.class_removed.emit(row)

    def refresh(self, class_names: list, active_index: int = 0):
        """Docstring"""
        self._list.blockSignals(True)
        self._list.clear()
        for i, name in enumerate(class_names):
            item = QListWidgetItem(self._make_color_icon(i), name)
            self._list.addItem(item)
        if 0 <= active_index < len(class_names):
            self._list.setCurrentRow(active_index)
        self._list.blockSignals(False)

    def select_class_by_index(self, index: int):
        """Docstring"""
        if 0 <= index < self._list.count():
            self._list.setCurrentRow(index)
