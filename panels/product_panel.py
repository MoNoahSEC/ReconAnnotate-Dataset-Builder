"""
Product panel — manage multiple products and choose active product.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLineEdit,
    QInputDialog,
)
from PyQt6.QtCore import pyqtSignal


class ProductPanel(QWidget):
    product_selected = pyqtSignal(int)
    product_added = pyqtSignal(str)
    product_removed = pyqtSignal(int)
    product_renamed = pyqtSignal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        title = QLabel("Products")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)

        add_row = QHBoxLayout()
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("New product name…")
        self._name_input.returnPressed.connect(self._on_add)
        add_row.addWidget(self._name_input)

        add_btn = QPushButton("+ Add")
        add_btn.setObjectName("AccentButton")
        add_btn.setFixedWidth(70)
        add_btn.clicked.connect(self._on_add)
        add_row.addWidget(add_btn)
        layout.addLayout(add_row)

        self._list = QListWidget()
        self._list.currentRowChanged.connect(self._on_selected)
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

        hint = QLabel("Each image belongs to the active product.")
        hint.setObjectName("SubLabel")
        layout.addWidget(hint)

    def _on_add(self):
        name = self._name_input.text().strip()
        if name:
            self._name_input.clear()
            self.product_added.emit(name)

    def _on_selected(self, row: int):
        if row >= 0:
            self.product_selected.emit(row)

    def _on_rename_btn(self):
        item = self._list.currentItem()
        if item:
            self._on_rename(item)

    def _on_rename(self, item=None):
        if not item:
            item = self._list.currentItem()
        if not item:
            return
        row = self._list.row(item)
        new_name, ok = QInputDialog.getText(self, "Rename Product", "New name:", text=item.text())
        if ok and new_name.strip():
            self.product_renamed.emit(row, new_name.strip())

    def _on_delete(self):
        row = self._list.currentRow()
        if row >= 0:
            self.product_removed.emit(row)

    def refresh(self, products: list[str], active_index: int = 0):
        self._list.blockSignals(True)
        self._list.clear()
        for name in products:
            self._list.addItem(QListWidgetItem(name))
        if 0 <= active_index < len(products):
            self._list.setCurrentRow(active_index)
        self._list.blockSignals(False)

