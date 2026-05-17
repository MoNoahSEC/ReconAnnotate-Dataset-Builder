"""
Project model — central state management for the annotation tool.
"""
import json
import os
from typing import List, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from .image_entry import ImageEntry, ImageCategory
from .annotation import BBoxAnnotation, PolygonAnnotation


class ProjectModel(QObject):
    """Docstring"""
    classes_changed = pyqtSignal()
    current_image_changed = pyqtSignal(int)
    annotations_changed = pyqtSignal()
    category_changed = pyqtSignal()
    project_loaded = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._classes: List[str] = []
        self._products: List[str] = ["Product 1"]
        self._active_product_index: int = 0
        self._images: List[ImageEntry] = []
        self._current_index: int = -1
        self._active_class_index: int = 0
        self._source_folder: str = ""

    @property
    def classes(self) -> List[str]:
        """Docstring"""
        return self._classes

    @property
    def products(self) -> List[str]:
        return self._products

    @property
    def active_product_index(self) -> int:
        return self._active_product_index

    @active_product_index.setter
    def active_product_index(self, val: int):
        if 0 <= val < len(self._products):
            self._active_product_index = val
            self.project_loaded.emit()

    @property
    def active_product_name(self) -> str:
        if 0 <= self._active_product_index < len(self._products):
            return self._products[self._active_product_index]
        return ""

    def add_product(self, name: str) -> int:
        name = (name or "").strip()
        if not name:
            return -1
        self._products.append(name)
        self._active_product_index = len(self._products) - 1
        self.project_loaded.emit()
        return self._active_product_index

    def rename_product(self, index: int, new_name: str):
        new_name = (new_name or "").strip()
        if 0 <= index < len(self._products) and new_name:
            self._products[index] = new_name
            self.project_loaded.emit()

    def remove_product(self, index: int):
        if len(self._products) <= 1:
            return
        if 0 <= index < len(self._products):
            self._products.pop(index)
            for img in self._images:
                if img.product_id == index:
                    img.product_id = 0
                elif img.product_id > index:
                    img.product_id -= 1
            if self._active_product_index >= len(self._products):
                self._active_product_index = len(self._products) - 1
            self.project_loaded.emit()

    def add_class(self, name: str) -> int:
        """Docstring"""
        if name and name not in self._classes:
            self._classes.append(name)
            self.classes_changed.emit()
            return len(self._classes) - 1
        return self._classes.index(name) if name in self._classes else -1

    def rename_class(self, index: int, new_name: str):
        """Docstring"""
        if 0 <= index < len(self._classes) and new_name:
            self._classes[index] = new_name
            self.classes_changed.emit()

    def remove_class(self, index: int):
        """Docstring"""
        if 0 <= index < len(self._classes):
            for img in self._images:
                img.annotations = [
                    a for a in img.annotations if a.class_id != index
                ]
                for a in img.annotations:
                    if a.class_id > index:
                        a.class_id -= 1
            self._classes.pop(index)
            if self._active_class_index >= len(self._classes):
                self._active_class_index = max(0, len(self._classes) - 1)
            self.classes_changed.emit()
            self.annotations_changed.emit()

    @property
    def active_class_index(self) -> int:
        """Docstring"""
        return self._active_class_index

    @active_class_index.setter
    def active_class_index(self, val: int):
        """Docstring"""
        if 0 <= val < len(self._classes):
            self._active_class_index = val

    @property
    def active_class_name(self) -> str:
        """Docstring"""
        if 0 <= self._active_class_index < len(self._classes):
            return self._classes[self._active_class_index]
        return ""

    @property
    def images(self) -> List[ImageEntry]:
        return self._images

    @property
    def image_count(self) -> int:
        return len(self._images)

    @property
    def current_index(self) -> int:
        return self._current_index

    @property
    def current_image(self) -> Optional[ImageEntry]:
        """Docstring"""
        if 0 <= self._current_index < len(self._images):
            return self._images[self._current_index]
        return None

    @property
    def source_folder(self) -> str:
        return self._source_folder

    def set_images(self, folder: str, entries: List[ImageEntry]):
        """Docstring"""
        self._source_folder = folder
        for e in entries:
            e.product_id = self._active_product_index
        self._images = entries
        self._current_index = 0 if entries else -1
        self.project_loaded.emit()
        if self._current_index >= 0:
            self.current_image_changed.emit(self._current_index)

    def append_images(self, entries: List[ImageEntry]):
        """Docstring"""
        if not entries:
            return 0
        for e in entries:
            if getattr(e, "product_id", None) is None:
                e.product_id = self._active_product_index
        if not self._source_folder and entries:
            self._source_folder = os.path.dirname(entries[0].path)
        existing_paths = {img.path for img in self._images}
        new_entries = [e for e in entries if e.path not in existing_paths]
        if not new_entries:
            return 0
        was_empty = len(self._images) == 0
        self._images.extend(new_entries)
        if was_empty:
            self._current_index = 0
        self.project_loaded.emit()
        if was_empty and self._current_index >= 0:
            self.current_image_changed.emit(self._current_index)
        return len(new_entries)

    def go_to_image(self, index: int):
        """Docstring"""
        if 0 <= index < len(self._images):
            self._current_index = index
            self.current_image_changed.emit(index)

    def next_image(self):
        """Docstring"""
        if self._current_index < len(self._images) - 1:
            self.go_to_image(self._current_index + 1)

    def prev_image(self):
        """Docstring"""
        if self._current_index > 0:
            self.go_to_image(self._current_index - 1)

    def erase_image(self, index: int):
        """Docstring"""
        if 0 <= index < len(self._images):
            img = self._images.pop(index)
            if len(self._images) == 0:
                self._current_index = -1
            elif self._current_index >= index:
                self._current_index = max(0, self._current_index - 1)
            

            self.project_loaded.emit()
            if self._current_index >= 0:
                self.current_image_changed.emit(self._current_index)

    def add_annotation(self, ann):
        """Docstring"""
        img = self.current_image
        if img:
            img.add_annotation(ann)
            self.annotations_changed.emit()

    def remove_annotation(self, uid: str):
        """Docstring"""
        img = self.current_image
        if img:
            img.remove_annotation(uid)
            self.annotations_changed.emit()

    def set_category(self, category: ImageCategory):
        """Docstring"""
        img = self.current_image
        if img:
            img.category = category
            self.category_changed.emit()

    def get_annotated_count(self) -> int:
        """Docstring"""
        return sum(
            1 for img in self._images
            if img.is_annotated or img.category != ImageCategory.UNCLASSIFIED
        )

    def to_dict(self) -> dict:
        """Docstring"""
        return {
            "classes": self._classes,
            "products": self._products,
            "source_folder": self._source_folder,
            "current_index": self._current_index,
            "active_class_index": self._active_class_index,
            "active_product_index": self._active_product_index,
            "images": [img.to_dict() for img in self._images],
        }

    def load_from_dict(self, d: dict, current_folder: str = ""):
        """Docstring"""
        self._classes = d.get("classes", [])
        self._products = d.get("products", ["Product 1"]) or ["Product 1"]
        self._active_class_index = d.get("active_class_index", 0)
        self._active_product_index = int(d.get("active_product_index", 0) or 0)
        if self._active_product_index >= len(self._products):
            self._active_product_index = 0
            
        if current_folder:
            self._source_folder = current_folder
        else:
            self._source_folder = d.get("source_folder", "")
            
        if self._source_folder:
            self._source_folder = self._source_folder.replace('\\', '/')
            if os.name != 'nt' and ':' in self._source_folder:
                parts = self._source_folder.split(':', 1)
                self._source_folder = parts[1] if len(parts) > 1 else self._source_folder

        self._images = []
        for img_dict in d.get("images", []):
            entry = ImageEntry.from_dict(img_dict)
            
            orig_path = entry.path.replace('\\', '/')
            filename = os.path.basename(orig_path)
            orig_dir = os.path.basename(os.path.dirname(orig_path))
            
            if self._source_folder:
                if orig_dir.lower() in ("good", "bad", "empty"):
                    # Check if self._source_folder itself ends with a category folder
                    src_basename = os.path.basename(self._source_folder)
                    if src_basename.lower() in ("good", "bad", "empty"):
                        parent_src = os.path.dirname(self._source_folder)
                        entry.path = os.path.join(parent_src, orig_dir, filename)
                    else:
                        entry.path = os.path.join(self._source_folder, orig_dir, filename)
                else:
                    entry.path = os.path.join(self._source_folder, filename)
            else:
                entry.path = orig_path
            
            from ..utils.path_resolver import resolve_case_insensitive_path
            entry.path = resolve_case_insensitive_path(entry.path)
                
            self._images.append(entry)

        self._current_index = d.get("current_index", 0 if self._images else -1)
        self.classes_changed.emit()
        self.project_loaded.emit()
        if self._current_index >= 0:
            self.current_image_changed.emit(self._current_index)

    def save_to_file(self, path: str):
        """Docstring"""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    def load_from_file(self, path: str):
        """Docstring"""
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.load_from_dict(data, os.path.dirname(path))
