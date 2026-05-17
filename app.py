"""
Main application window — orchestrates all panels, canvas, and models.
"""
import os
import glob
from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QStatusBar, QMessageBox, QFileDialog, QProgressDialog,
    QScrollArea, QFrame, QApplication
)
from PyQt6.QtGui import QPixmap, QShortcut, QKeySequence, QFont, QAction
from PyQt6.QtCore import Qt, QSize, QTimer
from PIL import Image

from .canvas.scene import AnnotationScene, DrawMode
from .canvas.view import AnnotationView
from .panels.class_panel import ClassPanel
from .panels.image_panel import ImagePanel
from .panels.annotation_panel import AnnotationPanel
from .panels.category_panel import CategoryPanel
from .panels.product_panel import ProductPanel
from .panels.toolbar import ToolBar
from .models.project import ProjectModel
from .models.image_entry import ImageEntry, ImageCategory
from .models.annotation import BBoxAnnotation, PolygonAnnotation
from .export.dataset_exporter import DatasetExporter
from .utils.autosave import AutoSaveManager
from .utils.video_frames import extract_frames
from .panels.video_import_dialog import VideoImportDialog

IMAGE_EXTENSIONS = ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff", "*.tif", "*.webp")


class MainWindow(QMainWindow):
    """Docstring"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Noah ReconAnnotate Pro — Premium Dataset Builder")
        self.setMinimumSize(1200, 750)
        self.resize(1500, 900)

        self._project = ProjectModel(self)
        self._undo_stack = []
        self._redo_stack = []
        self._split_ratio = 0.8
        self._project_save_path = ""

        self._project.add_class("Defect")
        self._project.add_class("Good")
        self._project.add_class("Object")

        self._autosave = AutoSaveManager(self._project, interval_ms=60000, parent=self)
        self._autosave.auto_saved.connect(self._on_autosaved)

        self._setup_ui()
        self._setup_shortcuts()
        self._connect_signals()

        self._toolbar.set_mode_bbox()

        self.statusBar().showMessage("Welcome! Open an image folder to begin annotating.", 5000)

    def _setup_ui(self):
        """Docstring"""
        self._toolbar = ToolBar(self)
        self.addToolBar(self._toolbar)

        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        left_frame = QFrame()
        left_frame.setObjectName("SidePanel")
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(0, 0, 0, 0)
        self._image_panel = ImagePanel()
        left_layout.addWidget(self._image_panel)
        main_splitter.addWidget(left_frame)

        self._scene = AnnotationScene(self)
        self._view = AnnotationView(self._scene, self)
        main_splitter.addWidget(self._view)

        right_frame = QFrame()
        right_frame.setObjectName("SidePanel")
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        right_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(4, 4, 4, 4)
        right_layout.setSpacing(12)

        self._product_panel = ProductPanel()
        right_layout.addWidget(self._product_panel)

        self._class_panel = ClassPanel()
        right_layout.addWidget(self._class_panel)

        self._category_panel = CategoryPanel()
        right_layout.addWidget(self._category_panel)

        self._annotation_panel = AnnotationPanel()
        right_layout.addWidget(self._annotation_panel)

        right_layout.addStretch()
        right_scroll.setWidget(right_container)

        right_outer = QVBoxLayout(right_frame)
        right_outer.setContentsMargins(0, 0, 0, 0)
        right_outer.addWidget(right_scroll)
        main_splitter.addWidget(right_frame)

        main_splitter.setSizes([220, 800, 300])

        self.setCentralWidget(main_splitter)

        self._status_mode = QLabel("Mode: —")
        self._status_class = QLabel("Class: —")
        self._status_zoom = QLabel("Zoom: 100%")
        self._status_pos = QLabel("Pos: (0, 0)")
        self._status_save = QLabel("")

        bar = self.statusBar()
        bar.addWidget(self._status_mode)
        bar.addWidget(self._make_separator())
        bar.addWidget(self._status_class)
        bar.addWidget(self._make_separator())
        bar.addWidget(self._status_zoom)
        bar.addWidget(self._make_separator())
        bar.addWidget(self._status_pos)
        
        # Permanent brand/author label
        self._status_author = QLabel("ReconAnnotate Pro by NOAH")
        self._status_author.setStyleSheet("color: #ff6b00; font-weight: bold; font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; margin-right: 15px; letter-spacing: 0.5px;")
        bar.addPermanentWidget(self._status_author)
        bar.addPermanentWidget(self._status_save)

    def _make_separator(self):
        """Docstring"""
        sep = QLabel("  |  ")
        sep.setStyleSheet("color: rgba(255,255,255,0.2);")
        return sep

    def _setup_shortcuts(self):
        """Docstring"""
        QShortcut(QKeySequence("B"), self).activated.connect(self._toolbar.set_mode_bbox)
        QShortcut(QKeySequence("P"), self).activated.connect(self._toolbar.set_mode_polygon)
        QShortcut(QKeySequence("E"), self).activated.connect(self._toolbar.set_mode_edit)
        QShortcut(QKeySequence("H"), self).activated.connect(self._toolbar.set_mode_freehand)

        QShortcut(QKeySequence("Space"), self).activated.connect(self._project.next_image)
        QShortcut(QKeySequence("D"), self).activated.connect(self._project.next_image)
        QShortcut(QKeySequence("A"), self).activated.connect(self._project.prev_image)

        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self._undo)
        QShortcut(QKeySequence("Ctrl+Y"), self).activated.connect(self._redo)
        QShortcut(QKeySequence("Ctrl+Shift+Z"), self).activated.connect(self._redo)

        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self._save_project)
        QShortcut(QKeySequence("Ctrl+E"), self).activated.connect(self._export_dataset)

        QShortcut(QKeySequence("F"), self).activated.connect(self._view.fit_image)

        # Classification Shortcuts for rapid workflow
        QShortcut(QKeySequence("Ctrl+1"), self).activated.connect(lambda: self._classify_by_shortcut(ImageCategory.GOOD))
        QShortcut(QKeySequence("Ctrl+2"), self).activated.connect(lambda: self._classify_by_shortcut(ImageCategory.BAD))
        QShortcut(QKeySequence("Ctrl+3"), self).activated.connect(lambda: self._classify_by_shortcut(ImageCategory.EMPTY))

        for i in range(9):
            QShortcut(QKeySequence(str(i + 1)), self).activated.connect(
                lambda idx=i: self._select_class_by_shortcut(idx)
            )

    def _classify_by_shortcut(self, category):
        """Classify current image and auto-advance for maximum speed!"""
        self._on_category_changed(category)
        if category in (ImageCategory.GOOD, ImageCategory.EMPTY):
            QTimer.singleShot(150, self._project.next_image)

    def _connect_signals(self):
        """Docstring"""
        self._toolbar.mode_changed.connect(self._on_mode_changed)
        self._toolbar.undo_requested.connect(self._undo)
        self._toolbar.redo_requested.connect(self._redo)
        self._toolbar.save_requested.connect(self._save_project)
        self._toolbar.export_requested.connect(self._export_dataset)
        self._toolbar.fit_requested.connect(self._view.fit_image)
        self._toolbar.split_changed.connect(self._on_split_changed)

        self._image_panel.folder_opened.connect(self._on_folder_opened)
        self._image_panel.image_selected.connect(self._on_image_selected)
        self._image_panel.approved_folder_opened.connect(self._on_approved_folder_opened)
        self._image_panel.empty_folder_opened.connect(self._on_empty_folder_opened)
        self._image_panel.add_more_folder_opened.connect(self._on_add_more_folder_opened)
        self._image_panel.image_erased.connect(self._on_image_erased)
        self._image_panel.video_import_requested.connect(self._on_video_import_requested)

        self._class_panel.class_added.connect(self._on_class_added)
        self._class_panel.class_removed.connect(self._on_class_removed)
        self._class_panel.class_renamed.connect(self._on_class_renamed)
        self._class_panel.class_selected.connect(self._on_class_selected)

        self._product_panel.product_added.connect(self._on_product_added)
        self._product_panel.product_removed.connect(self._on_product_removed)
        self._product_panel.product_renamed.connect(self._on_product_renamed)
        self._product_panel.product_selected.connect(self._on_product_selected)

        self._category_panel.category_changed.connect(self._on_category_changed)

        self._annotation_panel.annotation_selected.connect(self._on_annotation_selected)
        self._annotation_panel.annotation_delete_requested.connect(self._on_annotation_delete)
        self._annotation_panel.annotation_class_change.connect(self._on_annotation_class_change)

        self._scene.annotation_created.connect(self._on_annotation_created)
        self._scene.annotation_deleted.connect(self._on_scene_annotation_deleted)
        self._scene.annotation_modified.connect(self._on_annotation_modified)
        self._scene.item_selected.connect(self._on_scene_item_selected)
        self._scene.mouse_moved.connect(self._on_mouse_moved)

        self._view.zoom_changed.connect(self._on_zoom_changed)

        self._project.current_image_changed.connect(self._on_current_image_changed)
        self._project.annotations_changed.connect(self._refresh_annotation_panel)
        self._project.classes_changed.connect(self._refresh_class_panel)
        self._project.project_loaded.connect(self._refresh_product_panel)

    # ============================================================
    # ============================================================

    def _on_folder_opened(self, folder: str):
        """Docstring"""
        if AutoSaveManager.has_autosave(folder):
            reply = QMessageBox.question(
                self, "Recovery Found",
                "An auto-save was found for this folder.\nWould you like to restore it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                data = AutoSaveManager.load_autosave(folder)
                self._project.load_from_dict(data, folder)
                self._autosave.start(folder)
                self._refresh_all()
                self.statusBar().showMessage("Project restored from auto-save!", 3000)
                return

        # Check if an existing project file (annotation_project.json) is present in the folder
        project_file = os.path.join(folder, "annotation_project.json")
        if os.path.exists(project_file):
            reply = QMessageBox.question(
                self, "Project Found",
                "An existing project file ('annotation_project.json') was found in this folder.\nWould you like to load it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    with open(project_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    self._project.load_from_dict(data, folder)
                    self._project_save_path = project_file
                    self._autosave.start(folder)
                    self._refresh_all()
                    self.statusBar().showMessage("Project loaded from annotation_project.json!", 3000)
                    return
                except Exception as e:
                    QMessageBox.warning(self, "Load Error", f"Failed to load project: {e}")

        entries = []
        for ext in IMAGE_EXTENSIONS:
            pattern = os.path.join(folder, ext)
            for path in sorted(glob.glob(pattern)):
                filename = os.path.basename(path)
                try:
                    with Image.open(path) as pil_img:
                        w, h = pil_img.size
                except Exception:
                    w, h = 0, 0
                entries.append(ImageEntry(path=path, filename=filename, width=w, height=h))

        if not entries:
            QMessageBox.warning(self, "No Images", "No supported images found in this folder.")
            return

        for e in entries:
            e.product_id = self._project.active_product_index
        self._project.set_images(folder, entries)
        self._autosave.start(folder)
        self._refresh_all()
        self.statusBar().showMessage(f"Loaded {len(entries)} images from folder.", 3000)

    def _scan_folder_for_images(self, folder: str):
        """Docstring"""
        entries = []
        for ext in IMAGE_EXTENSIONS:
            pattern = os.path.join(folder, ext)
            for path in sorted(glob.glob(pattern)):
                filename = os.path.basename(path)
                try:
                    with Image.open(path) as pil_img:
                        w, h = pil_img.size
                except Exception:
                    w, h = 0, 0
                entries.append(ImageEntry(path=path, filename=filename, width=w, height=h))
        return entries

    def _on_approved_folder_opened(self, folder: str):
        """Docstring"""
        entries = self._scan_folder_for_images(folder)
        if not entries:
            QMessageBox.warning(self, "No Images", "No supported images found in this folder.")
            return
        for entry in entries:
            entry.category = ImageCategory.GOOD
            entry.product_id = self._project.active_product_index
        count = self._project.append_images(entries)
        if not self._project.source_folder:
            self._autosave.start(folder)
        self._refresh_all()
        self.statusBar().showMessage(
            f"Added {count} approved images (auto-classified as Good)", 4000
        )

    def _on_empty_folder_opened(self, folder: str):
        """Docstring"""
        entries = self._scan_folder_for_images(folder)
        if not entries:
            QMessageBox.warning(self, "No Images", "No supported images found in this folder.")
            return
        for entry in entries:
            entry.category = ImageCategory.EMPTY
            entry.product_id = self._project.active_product_index
        count = self._project.append_images(entries)
        if not self._project.source_folder:
            self._autosave.start(folder)
        self._refresh_all()
        self.statusBar().showMessage(
            f"Added {count} empty images (auto-classified as Empty — excluded)", 4000
        )

    def _on_add_more_folder_opened(self, folder: str):
        """Docstring"""
        entries = self._scan_folder_for_images(folder)
        if not entries:
            QMessageBox.warning(self, "No Images", "No supported images found in this folder.")
            return
        for entry in entries:
            entry.product_id = self._project.active_product_index
        count = self._project.append_images(entries)
        if not self._project.source_folder:
            self._autosave.start(folder)
        self._refresh_all()
        self.statusBar().showMessage(
            f"Added {count} new images to the project", 4000
        )

    def _on_image_erased(self, index: int):
        """Docstring"""
        img = self._project.images[index] if 0 <= index < self._project.image_count else None
        self._project.erase_image(index)
        self._refresh_all()
        if img:
            self.statusBar().showMessage(f"Erased: {img.filename}", 3000)

    def _on_image_selected(self, index: int):
        """Docstring"""
        self._sync_annotations_to_model()
        self._project.go_to_image(index)

    def _on_current_image_changed(self, index: int):
        """Docstring"""
        # Clear undo/redo stacks when active image changes to prevent cross-image state bugs!
        self._undo_stack.clear()
        self._redo_stack.clear()

        img = self._project.current_image
        if not img:
            return

        from .utils.path_resolver import resolve_case_insensitive_path
        actual_path = resolve_case_insensitive_path(img.path)
        print(f"[DEBUG] Attempting to load image from path: {img.path} (Resolved: {actual_path})")
        pixmap = QPixmap(actual_path)
        print(f"[DEBUG] QPixmap isNull? {pixmap.isNull()} | Size: {pixmap.width()}x{pixmap.height()}")
        if pixmap.isNull():
            self.statusBar().showMessage(f"Failed to load: {img.filename}", 3000)
            return

        if img.width == 0:
            img.width = pixmap.width()
            img.height = pixmap.height()

        self._scene.load_image(pixmap)
        print(f"[DEBUG] Scene size: {self._scene.sceneRect()} | Items: {len(self._scene.items())}")

        for ann in img.annotations:
            cname = self._project.classes[ann.class_id] if ann.class_id < len(self._project.classes) else "?"
            if isinstance(ann, BBoxAnnotation):
                self._scene.add_bbox_item(ann, cname)
            elif isinstance(ann, PolygonAnnotation):
                self._scene.add_polygon_item(ann, cname)

        QTimer.singleShot(50, self._view.fit_image)

        self._category_panel.set_category(img.category)
        self._image_panel.set_current(index)
        self._refresh_annotation_panel()

        self.statusBar().showMessage(
            f"Image {index+1}/{self._project.image_count}: {img.filename} "
            f"({img.width}×{img.height})", 3000
        )

    # ============================================================
    # ============================================================

    def _on_class_added(self, name: str):
        self._project.add_class(name)

    def _on_class_removed(self, index: int):
        self._project.remove_class(index)
        self._reload_current_image()

    def _on_class_renamed(self, index: int, new_name: str):
        self._project.rename_class(index, new_name)
        self._reload_current_image()

    def _on_class_selected(self, index: int, name: str):
        self._project.active_class_index = index
        self._scene.set_active_class(index, name)
        self._status_class.setText(f"Class: {name}")

    # ============================================================
    # ============================================================

    def _on_product_added(self, name: str):
        self._project.add_product(name)
        self._refresh_product_panel()

    def _on_product_removed(self, index: int):
        self._project.remove_product(index)
        self._refresh_product_panel()
        self._image_panel.refresh(self._project.images, self._project.current_index, self._project.classes)

    def _on_product_renamed(self, index: int, new_name: str):
        self._project.rename_product(index, new_name)
        self._refresh_product_panel()

    def _on_product_selected(self, index: int):
        self._project.active_product_index = index
        self.statusBar().showMessage(f"Active product: {self._project.active_product_name}", 2500)

    def _select_class_by_shortcut(self, index: int):
        if index < len(self._project.classes):
            self._class_panel.select_class_by_index(index)

    def _refresh_class_panel(self):
        self._class_panel.refresh(self._project.classes, self._project.active_class_index)
        if self._project.classes:
            name = self._project.active_class_name
            self._scene.set_active_class(self._project.active_class_index, name)
            self._status_class.setText(f"Class: {name}")

    # ============================================================
    # ============================================================

    def _on_annotation_created(self, ann):
        """Docstring"""
        if not self._project.classes:
            QMessageBox.warning(self, "No Classes", "Please add at least one class before annotating.")
            self._scene.remove_item_by_uid(ann.uid)
            return
        self._project.add_annotation(ann)
        self._undo_stack.append(("add", ann.uid, ann))
        self._redo_stack.clear()
        img = self._project.current_image
        if img:
            cname = self._project.classes[ann.class_id] if ann.class_id < len(self._project.classes) else ""
            if cname.lower() == "good":
                img.category = ImageCategory.GOOD
                self._category_panel.set_category(ImageCategory.GOOD)
            elif img.category == ImageCategory.UNCLASSIFIED or img.category == ImageCategory.GOOD:
                img.category = ImageCategory.BAD
                self._category_panel.set_category(ImageCategory.BAD)
        self._update_image_status()

    def _on_annotation_delete(self, uid: str):
        """Docstring"""
        img = self._project.current_image
        if img:
            ann = img.get_annotation_by_uid(uid)
            if ann:
                self._undo_stack.append(("delete", uid, ann))
                self._redo_stack.clear()
        self._project.remove_annotation(uid)
        self._scene.remove_item_by_uid(uid)
        self._update_image_status()

    def _on_scene_annotation_deleted(self, uid: str):
        """Docstring"""
        self._on_annotation_delete(uid)

    def _on_annotation_modified(self, uid: str):
        """Docstring"""
        self._sync_annotation_from_scene(uid)

    def _on_annotation_selected(self, uid: str):
        """Docstring"""
        self._scene.highlight_item(uid)

    def _on_scene_item_selected(self, uid: str):
        """Docstring"""
        self._annotation_panel.highlight(uid)

    def _on_annotation_class_change(self, uid: str, new_class_id: int):
        """Docstring"""
        img = self._project.current_image
        if img and new_class_id < len(self._project.classes):
            ann = img.get_annotation_by_uid(uid)
            if ann:
                ann.class_id = new_class_id
                cname = self._project.classes[new_class_id]
                self._scene.change_selected_class(new_class_id, cname)
                self._refresh_annotation_panel()

    def _sync_annotations_to_model(self):
        """Docstring"""
        img = self._project.current_image
        if not img:
            return
        coords = self._scene.get_all_coords()
        for ann in img.annotations:
            if ann.uid in coords:
                atype, data = coords[ann.uid]
                if atype == "bbox" and isinstance(ann, BBoxAnnotation):
                    ann.x = data["x"]
                    ann.y = data["y"]
                    ann.w = data["w"]
                    ann.h = data["h"]
                elif atype == "polygon" and isinstance(ann, PolygonAnnotation):
                    ann.points = data

    def _sync_annotation_from_scene(self, uid: str):
        """Docstring"""
        img = self._project.current_image
        if not img:
            return
        coords = self._scene.get_all_coords()
        if uid in coords:
            ann = img.get_annotation_by_uid(uid)
            if ann:
                atype, data = coords[uid]
                if atype == "bbox" and isinstance(ann, BBoxAnnotation):
                    ann.x, ann.y, ann.w, ann.h = data["x"], data["y"], data["w"], data["h"]
                elif atype == "polygon" and isinstance(ann, PolygonAnnotation):
                    ann.points = data

    def _refresh_annotation_panel(self):
        """Docstring"""
        img = self._project.current_image
        if img:
            self._annotation_panel.refresh(img.annotations, self._project.classes)
        else:
            self._annotation_panel.refresh([], [])

    # ============================================================
    # ============================================================

    def _on_category_changed(self, category):
        """Docstring"""
        self._project.set_category(category)
        self._update_image_status()

    def _on_mode_changed(self, mode: DrawMode):
        """Docstring"""
        self._sync_annotations_to_model()
        self._scene.set_mode(mode)
        mode_names = {
            DrawMode.BBOX: "BBox", DrawMode.POLYGON: "Polygon", DrawMode.FREEHAND: "Freehand",
            DrawMode.EDIT: "Edit", DrawMode.NONE: "—"
        }
        self._status_mode.setText(f"Mode: {mode_names.get(mode, '—')}")

    def _on_mouse_moved(self, x, y):
        self._status_pos.setText(f"Pos: ({int(x)}, {int(y)})")

    def _on_zoom_changed(self, pct):
        self._status_zoom.setText(f"Zoom: {pct}%")

    def _on_split_changed(self, val):
        self._split_ratio = val / 100.0

    # ============================================================
    # ============================================================

    def _undo(self):
        """Docstring"""
        if not self._undo_stack:
            return
        action = self._undo_stack.pop()
        self._redo_stack.append(action)
        atype, uid, ann = action

        if atype == "add":
            self._project.remove_annotation(uid)
            self._scene.remove_item_by_uid(uid)
        elif atype == "delete":
            self._project.add_annotation(ann)
            cname = self._project.classes[ann.class_id] if ann.class_id < len(self._project.classes) else "?"
            if isinstance(ann, BBoxAnnotation):
                self._scene.add_bbox_item(ann, cname)
            elif isinstance(ann, PolygonAnnotation):
                self._scene.add_polygon_item(ann, cname)
        self._refresh_annotation_panel()
        self._update_image_status()

    def _redo(self):
        """Docstring"""
        if not self._redo_stack:
            return
        action = self._redo_stack.pop()
        self._undo_stack.append(action)
        atype, uid, ann = action

        if atype == "add":
            self._project.add_annotation(ann)
            cname = self._project.classes[ann.class_id] if ann.class_id < len(self._project.classes) else "?"
            if isinstance(ann, BBoxAnnotation):
                self._scene.add_bbox_item(ann, cname)
            elif isinstance(ann, PolygonAnnotation):
                self._scene.add_polygon_item(ann, cname)
        elif atype == "delete":
            self._project.remove_annotation(uid)
            self._scene.remove_item_by_uid(uid)
        self._refresh_annotation_panel()
        self._update_image_status()

    # ============================================================
    # ============================================================

    def _save_project(self):
        """Docstring"""
        self._sync_annotations_to_model()
        default_name = "annotation_project.json"
        start_dir = self._project.source_folder if self._project.source_folder else ""
        if self._project_save_path:
            start_dir = os.path.dirname(self._project_save_path)
            default_name = os.path.basename(self._project_save_path)

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Project As…",
            os.path.join(start_dir, default_name) if start_dir else default_name,
            "JSON (*.json)",
        )
        if not path:
            return
        if not path.lower().endswith(".json"):
            path += ".json"

        try:
            self._project.save_to_file(path)
            self._project_save_path = path
            self.statusBar().showMessage("Project saved!", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))
            return
        self._status_save.setText("✓ Saved")
        QTimer.singleShot(3000, lambda: self._status_save.setText(""))

    def _on_video_import_requested(self, category: ImageCategory):
        """Docstring"""
        if not self._project.source_folder:
            QMessageBox.information(
                self,
                "Open Images Folder First",
                "Please open an image folder first (it will be used as the project base).",
            )
            return

        video_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            self._project.source_folder,
            "Video Files (*.mp4 *.avi *.mov *.mkv *.webm *.m4v);;All Files (*.*)",
        )
        if not video_path:
            return

        base = os.path.splitext(os.path.basename(video_path))[0]
        cat_name = category.value
        default_out = os.path.join(self._project.source_folder, "video_frames", f"{base}_{cat_name}")

        dlg = VideoImportDialog(video_path, default_out, self)
        if dlg.exec() != dlg.DialogCode.Accepted:
            return
        cfg = dlg.result_config()
        if not cfg:
            return

        progress = QProgressDialog("Extracting frames from video…", "Cancel", 0, 100, self)
        progress.setWindowTitle("Video Import")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)

        cancelled = {"v": False}

        def update_progress(cur, total):
            if progress.wasCanceled():
                cancelled["v"] = True
                return
            pct = int((cur / max(total, 1)) * 100) if total else 0
            progress.setValue(pct)
            QApplication.processEvents()

        try:
            paths = extract_frames(cfg.meta.path, cfg.output_dir, cfg.plan, progress_cb=update_progress)
        except Exception as e:
            progress.close()
            QMessageBox.critical(self, "Video Import Error", str(e))
            return

        progress.close()
        if cancelled["v"]:
            QMessageBox.information(self, "Cancelled", "Video import was cancelled.")
            return

        # Convert extracted frames to ImageEntry
        entries = []
        for p in paths:
            try:
                px = QPixmap(p)
                w = px.width()
                h = px.height()
            except Exception:
                w, h = 0, 0
            e = ImageEntry(
                path=p,
                filename=os.path.basename(p),
                width=w,
                height=h,
                product_id=self._project.active_product_index,
                category=category,
            )
            entries.append(e)

        added = self._project.append_images(entries)
        self._refresh_all()
        self.statusBar().showMessage(f"Imported {added} frames from video → {category.value.title()}", 5000)

    def _on_autosaved(self):
        """Docstring"""
        self._status_save.setText("✓ Auto-saved")
        QTimer.singleShot(2000, lambda: self._status_save.setText(""))

    def _export_dataset(self):
        """Docstring"""
        self._sync_annotations_to_model()

        if not self._project.classes:
            QMessageBox.warning(self, "No Classes", "Add at least one class before exporting.")
            return

        if self._project.image_count == 0:
            QMessageBox.warning(self, "No Images", "Load images before exporting.")
            return

        default_dir = os.path.join(self._project.source_folder, "dataset")
        output_dir = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", os.path.dirname(default_dir)
        )
        if not output_dir:
            return

        dataset_dir = os.path.join(output_dir, "dataset")

        progress = QProgressDialog("Exporting dataset...", "Cancel", 0, 100, self)
        progress.setWindowTitle("Export Progress")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)

        def update_progress(val):
            progress.setValue(val)
            QApplication.processEvents()

        exporter = DatasetExporter(dataset_dir, self._project.classes, self._split_ratio)
        stats = exporter.export(self._project.images, progress_callback=update_progress)

        progress.setValue(100)
        progress.close()

        msg = (
            f"Export Complete!\n\n"
            f"Output: {stats['output_dir']}\n\n"
            f"Training Set:\n"
            f"   • Images: {stats['train_images']}\n"
            f"   • Annotations: {stats['train_annotations']}\n"
            f"   • Backgrounds: {stats['train_backgrounds']}\n\n"
            f"Validation Set:\n"
            f"   • Images: {stats['val_images']}\n"
            f"   • Annotations: {stats['val_annotations']}\n"
            f"   • Backgrounds: {stats['val_backgrounds']}\n\n"
            f"Classes: {stats['classes']}\n"
        )
        if stats["errors"]:
            msg += f"\nWarnings ({len(stats['errors'])}):\n"
            for e in stats["errors"][:5]:
                msg += f"   • {e}\n"
            if len(stats["errors"]) > 5:
                msg += f"   ...and {len(stats['errors'])-5} more\n"

        QMessageBox.information(self, "Export Complete", msg)
        self.statusBar().showMessage("Dataset exported successfully!", 5000)

    # ============================================================
    # ============================================================

    def _reload_current_image(self):
        """Docstring"""
        idx = self._project.current_index
        if idx >= 0:
            self._on_current_image_changed(idx)

    def _update_image_status(self):
        """Docstring"""
        img = self._project.current_image
        idx = self._project.current_index
        if img and idx >= 0:
            self._image_panel.update_item_status(idx, img.category, img.is_annotated)

    def _refresh_all(self):
        """Docstring"""
        self._refresh_product_panel()
        self._refresh_class_panel()
        self._image_panel.refresh(self._project.images, self._project.current_index, self._project.classes)
        if self._project.current_index >= 0:
            self._on_current_image_changed(self._project.current_index)

    def _refresh_product_panel(self):
        self._product_panel.refresh(self._project.products, self._project.active_product_index)

    def closeEvent(self, event):
        """Docstring"""
        self._sync_annotations_to_model()
        self._autosave.save_now()
        event.accept()
