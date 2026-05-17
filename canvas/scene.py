"""
AnnotationScene — handles drawing logic for bounding boxes and polygons.
"""
from enum import Enum
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsLineItem
from PyQt6.QtGui import QPen, QColor, QPixmap, QBrush, QPolygonF
from PyQt6.QtCore import Qt, QPointF, pyqtSignal, QRectF
from .items import BBoxItem, PolygonItem
from ..utils.colors import get_class_color
from ..models.annotation import BBoxAnnotation, PolygonAnnotation
import uuid


class DrawMode(Enum):
    """Docstring"""
    NONE = "none"
    BBOX = "bbox"
    POLYGON = "polygon"
    FREEHAND = "freehand"
    EDIT = "edit"


class AnnotationScene(QGraphicsScene):
    """Docstring"""
    annotation_created = pyqtSignal(object)
    annotation_deleted = pyqtSignal(str)
    annotation_modified = pyqtSignal(str)
    item_selected = pyqtSignal(str)
    mouse_moved = pyqtSignal(float, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._mode = DrawMode.NONE
        self._active_class_id = 0
        self._active_class_name = ""
        self._image_item = None
        self._image_w = 0
        self._image_h = 0

        self._bbox_start = None
        self._bbox_preview = None

        self._polygon_points = []
        self._polygon_lines = []
        self._polygon_preview_line = None

        self._freehand_points = []
        self._freehand_path_item = None

        self._annotation_items = {}

    @property
    def mode(self):
        return self._mode

    def set_mode(self, mode: DrawMode):
        """Docstring"""
        self._cancel_drawing()
        self._mode = mode
        for item in self._annotation_items.values():
            item.set_editing(mode == DrawMode.EDIT)

    def set_active_class(self, class_id: int, class_name: str):
        """Docstring"""
        self._active_class_id = class_id
        self._active_class_name = class_name

    def load_image(self, pixmap: QPixmap):
        """Docstring"""
        self.clear()
        self._annotation_items.clear()
        self._cancel_drawing()
        self._image_item = self.addPixmap(pixmap)
        self._image_item.setZValue(-1)
        self._image_w = pixmap.width()
        self._image_h = pixmap.height()
        self.setSceneRect(0, 0, self._image_w, self._image_h)

    def add_bbox_item(self, ann: BBoxAnnotation, class_name: str):
        """Docstring"""
        item = BBoxItem(ann.x, ann.y, ann.w, ann.h, ann.class_id, class_name, ann.uid)
        item.setZValue(1)
        self.addItem(item)
        self._annotation_items[ann.uid] = item
        return item

    def add_polygon_item(self, ann: PolygonAnnotation, class_name: str):
        """Docstring"""
        item = PolygonItem(ann.points, ann.class_id, class_name, ann.uid)
        item.setZValue(1)
        self.addItem(item)
        self._annotation_items[ann.uid] = item
        return item

    def remove_item_by_uid(self, uid: str):
        """Docstring"""
        if uid in self._annotation_items:
            item = self._annotation_items.pop(uid)
            self.removeItem(item)

    def highlight_item(self, uid: str):
        """Docstring"""
        for u, item in self._annotation_items.items():
            item.setSelected(u == uid)

    def get_selected_uid(self):
        """Docstring"""
        for uid, item in self._annotation_items.items():
            if item.isSelected():
                return uid
        return None

    def _cancel_drawing(self):
        """Docstring"""
        self._bbox_start = None
        if self._bbox_preview:
            self.removeItem(self._bbox_preview)
            self._bbox_preview = None
        for line in self._polygon_lines:
            self.removeItem(line)
        self._polygon_lines.clear()
        self._polygon_points.clear()
        if self._polygon_preview_line:
            self.removeItem(self._polygon_preview_line)
            self._polygon_preview_line = None
        if self._freehand_path_item:
            self.removeItem(self._freehand_path_item)
            self._freehand_path_item = None
        self._freehand_points.clear()

    def cancel_current(self):
        """Docstring"""
        self._cancel_drawing()

    def _clamp_to_image(self, pos: QPointF) -> QPointF:
        """Docstring"""
        if self._image_w <= 0 or self._image_h <= 0:
            return QPointF(0, 0)
        x = max(0.0, min(float(self._image_w), float(pos.x())))
        y = max(0.0, min(float(self._image_h), float(pos.y())))
        return QPointF(x, y)

    def _simplify_polyline(self, pts, epsilon: float):
        """Docstring"""
        if len(pts) < 3:
            return pts

        def _perp_dist(p, a, b):
            ax, ay = a
            bx, by = b
            px, py = p
            dx = bx - ax
            dy = by - ay
            if dx == 0 and dy == 0:
                return ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5
            t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
            t = max(0.0, min(1.0, t))
            cx = ax + t * dx
            cy = ay + t * dy
            return ((px - cx) ** 2 + (py - cy) ** 2) ** 0.5

        a = pts[0]
        b = pts[-1]
        max_d = -1.0
        idx = -1
        for i in range(1, len(pts) - 1):
            d = _perp_dist(pts[i], a, b)
            if d > max_d:
                max_d = d
                idx = i
        if max_d <= epsilon or idx < 0:
            return [a, b]
        left = self._simplify_polyline(pts[: idx + 1], epsilon)
        right = self._simplify_polyline(pts[idx:], epsilon)
        return left[:-1] + right

    def mousePressEvent(self, event):
        """Docstring"""
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return

        pos = self._clamp_to_image(event.scenePos())

        if self._mode == DrawMode.BBOX:
            self._bbox_start = pos
            color = get_class_color(self._active_class_id)
            pen = QPen(color, 2, Qt.PenStyle.DashLine)
            pen.setCosmetic(True)
            self._bbox_preview = self.addRect(QRectF(pos, pos), pen)
            self._bbox_preview.setZValue(10)

        elif self._mode == DrawMode.POLYGON:
            self._polygon_points.append((pos.x(), pos.y()))
            if len(self._polygon_points) > 1:
                p1 = self._polygon_points[-2]
                p2 = self._polygon_points[-1]
                color = get_class_color(self._active_class_id)
                pen = QPen(color, 2)
                pen.setCosmetic(True)
                line = self.addLine(p1[0], p1[1], p2[0], p2[1], pen)
                line.setZValue(10)
                self._polygon_lines.append(line)

        elif self._mode == DrawMode.FREEHAND:
            self._freehand_points = [(pos.x(), pos.y())]
            from PyQt6.QtGui import QPainterPath
            path = QPainterPath(QPointF(pos.x(), pos.y()))
            color = get_class_color(self._active_class_id)
            pen = QPen(color, 2, Qt.PenStyle.SolidLine)
            pen.setCosmetic(True)
            self._freehand_path_item = self.addPath(path, pen)
            self._freehand_path_item.setZValue(10)

        elif self._mode == DrawMode.EDIT:
            super().mousePressEvent(event)
            for uid, item in self._annotation_items.items():
                if item.isSelected():
                    self.item_selected.emit(uid)
                    return
            return
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Docstring"""
        pos = self._clamp_to_image(event.scenePos())
        self.mouse_moved.emit(pos.x(), pos.y())

        if self._mode == DrawMode.BBOX and self._bbox_start and self._bbox_preview:
            rect = QRectF(self._bbox_start, pos).normalized()
            self._bbox_preview.setRect(rect)

        elif self._mode == DrawMode.POLYGON and self._polygon_points:
            last = self._polygon_points[-1]
            if self._polygon_preview_line:
                self.removeItem(self._polygon_preview_line)
            color = get_class_color(self._active_class_id)
            pen = QPen(color, 1, Qt.PenStyle.DashLine)
            pen.setCosmetic(True)
            self._polygon_preview_line = self.addLine(
                last[0], last[1], pos.x(), pos.y(), pen
            )
            self._polygon_preview_line.setZValue(10)

        elif self._mode == DrawMode.FREEHAND and self._freehand_points and self._freehand_path_item:
            lastx, lasty = self._freehand_points[-1]
            dx = pos.x() - lastx
            dy = pos.y() - lasty
            if (dx * dx + dy * dy) >= 1.0:
                self._freehand_points.append((pos.x(), pos.y()))
                from PyQt6.QtGui import QPainterPath
                path = self._freehand_path_item.path()
                path.lineTo(QPointF(pos.x(), pos.y()))
                self._freehand_path_item.setPath(path)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Docstring"""
        if event.button() != Qt.MouseButton.LeftButton:
            super().mouseReleaseEvent(event)
            return

        if self._mode == DrawMode.BBOX and self._bbox_start:
            pos = self._clamp_to_image(event.scenePos())
            rect = QRectF(self._bbox_start, pos).normalized()
            rect = rect.intersected(QRectF(0, 0, max(self._image_w, 1), max(self._image_h, 1)))
            if rect.width() > 3 and rect.height() > 3:
                uid = str(uuid.uuid4())[:8]
                ann = BBoxAnnotation(
                    class_id=self._active_class_id,
                    x=rect.x(), y=rect.y(),
                    w=rect.width(), h=rect.height(),
                    uid=uid
                )
                self.add_bbox_item(ann, self._active_class_name)
                self.annotation_created.emit(ann)
            if self._bbox_preview:
                self.removeItem(self._bbox_preview)
                self._bbox_preview = None
            self._bbox_start = None
            return

        if self._mode == DrawMode.FREEHAND and self._freehand_points:
            pts = list(self._freehand_points)
            self._freehand_points.clear()
            if self._freehand_path_item:
                self.removeItem(self._freehand_path_item)
                self._freehand_path_item = None

            eps = max(1.5, min(6.0, (self._image_w + self._image_h) / 800.0))
            pts = self._simplify_polyline(pts, eps)

            if len(pts) >= 3:
                if pts[0] != pts[-1]:
                    pts.append(pts[0])
                uid = str(uuid.uuid4())[:8]
                ann = PolygonAnnotation(
                    class_id=self._active_class_id,
                    points=pts,
                    uid=uid
                )
                self.add_polygon_item(ann, self._active_class_name)
                self.annotation_created.emit(ann)
            return
        else:
            super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Docstring"""
        if self._mode == DrawMode.POLYGON and len(self._polygon_points) >= 3:
            self._finalize_polygon()
        else:
            super().mouseDoubleClickEvent(event)

    def close_polygon(self):
        """Docstring"""
        if self._mode == DrawMode.POLYGON and len(self._polygon_points) >= 3:
            self._finalize_polygon()

    def _finalize_polygon(self):
        """Docstring"""
        uid = str(uuid.uuid4())[:8]
        ann = PolygonAnnotation(
            class_id=self._active_class_id,
            points=list(self._polygon_points),
            uid=uid
        )
        self.add_polygon_item(ann, self._active_class_name)
        self.annotation_created.emit(ann)
        for line in self._polygon_lines:
            self.removeItem(line)
        self._polygon_lines.clear()
        self._polygon_points.clear()
        if self._polygon_preview_line:
            self.removeItem(self._polygon_preview_line)
            self._polygon_preview_line = None

    def delete_selected(self):
        """Docstring"""
        uid = self.get_selected_uid()
        if uid:
            self.remove_item_by_uid(uid)
            self.annotation_deleted.emit(uid)

    def change_selected_class(self, class_id, class_name):
        """Docstring"""
        uid = self.get_selected_uid()
        if uid and uid in self._annotation_items:
            self._annotation_items[uid].update_class(class_id, class_name)
            self.annotation_modified.emit(uid)

    def get_all_coords(self):
        """Docstring"""
        results = {}
        for uid, item in self._annotation_items.items():
            if isinstance(item, BBoxItem):
                results[uid] = ("bbox", item.get_pixel_coords())
            elif isinstance(item, PolygonItem):
                results[uid] = ("polygon", item.get_pixel_points())
        return results
