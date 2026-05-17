"""
Custom QGraphicsItem subclasses for bounding boxes and polygons.
"""
import math
from PyQt6.QtWidgets import (
    QGraphicsRectItem, QGraphicsPolygonItem,
    QGraphicsItem, QGraphicsSceneHoverEvent,
    QGraphicsSceneMouseEvent, QStyleOptionGraphicsItem
)
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QPainter, QPolygonF, QCursor
from PyQt6.QtCore import Qt, QRectF, QPointF
from ..utils.colors import get_class_color, get_class_color_with_alpha

HANDLE_SIZE = 8
HANDLE_HALF = HANDLE_SIZE / 2


class BBoxItem(QGraphicsRectItem):
    """Docstring"""
    def __init__(self, x, y, w, h, class_id, class_name, uid, parent=None):
        super().__init__(x, y, w, h, parent)
        self.class_id = class_id
        self.class_name = class_name
        self.uid = uid
        self._is_editing = False
        self._resize_handle = None
        self._drag_start_rect = None
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        self._update_style()

    def _update_style(self):
        """Docstring"""
        color = get_class_color(self.class_id)
        fill = get_class_color_with_alpha(self.class_id, 40)
        pen = QPen(color, 2)
        pen.setCosmetic(True)
        self.setPen(pen)
        self.setBrush(QBrush(fill))

    def set_editing(self, editing: bool):
        self._is_editing = editing
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, editing)
        self.update()

    def update_class(self, class_id: int, class_name: str):
        self.class_id = class_id
        self.class_name = class_name
        self._update_style()
        self.update()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None):
        """Docstring"""
        super().paint(painter, option, widget)
        rect = self.rect()
        color = get_class_color(self.class_id)
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        label = f" {self.class_name} "
        fm = painter.fontMetrics()
        tr = fm.boundingRect(label)
        lbg = QRectF(rect.x(), rect.y() - tr.height() - 4, tr.width() + 8, tr.height() + 4)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(color))
        painter.drawRoundedRect(lbg, 3, 3)
        painter.setPen(QPen(QColor(0, 0, 0)))
        painter.drawText(lbg, Qt.AlignmentFlag.AlignCenter, label)
        if self.isSelected() or self._is_editing:
            hp = QPen(QColor(255, 255, 255), 1)
            hp.setCosmetic(True)
            painter.setPen(hp)
            painter.setBrush(QBrush(color))
            for hr in self._get_handles():
                painter.drawRect(hr)
        if self.isSelected():
            sp = QPen(QColor(255, 255, 255), 1, Qt.PenStyle.DashLine)
            sp.setCosmetic(True)
            painter.setPen(sp)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(rect)

    def _get_handles(self):
        """Docstring"""
        r = self.rect()
        s = HANDLE_HALF
        return [
            QRectF(r.left()-s, r.top()-s, HANDLE_SIZE, HANDLE_SIZE),
            QRectF(r.right()-s, r.top()-s, HANDLE_SIZE, HANDLE_SIZE),
            QRectF(r.left()-s, r.bottom()-s, HANDLE_SIZE, HANDLE_SIZE),
            QRectF(r.right()-s, r.bottom()-s, HANDLE_SIZE, HANDLE_SIZE),
        ]

    def _handle_at(self, pos):
        handles = self._get_handles()
        names = ["top_left", "top_right", "bottom_left", "bottom_right"]
        for hr, n in zip(handles, names):
            if hr.contains(pos):
                return n
        return None

    def hoverMoveEvent(self, event):
        if self._is_editing or self.isSelected():
            h = self._handle_at(event.pos())
            if h in ("top_left", "bottom_right"):
                self.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
            elif h in ("top_right", "bottom_left"):
                self.setCursor(QCursor(Qt.CursorShape.SizeBDiagCursor))
            elif self.rect().contains(event.pos()):
                self.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))
            else:
                self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if self._is_editing and event.button() == Qt.MouseButton.LeftButton:
            self._resize_handle = self._handle_at(event.pos())
            self._drag_start_rect = QRectF(self.rect())
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resize_handle and self._drag_start_rect:
            pos = event.pos()
            r = QRectF(self._drag_start_rect)
            if "left" in self._resize_handle:
                r.setLeft(pos.x())
            if "right" in self._resize_handle:
                r.setRight(pos.x())
            if "top" in self._resize_handle:
                r.setTop(pos.y())
            if "bottom" in self._resize_handle:
                r.setBottom(pos.y())
            self.setRect(r.normalized())
            self.update()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._resize_handle = None
        self._drag_start_rect = None
        super().mouseReleaseEvent(event)

    def boundingRect(self):
        r = super().boundingRect()
        return r.adjusted(-HANDLE_SIZE, -30, HANDLE_SIZE, HANDLE_SIZE)

    def get_pixel_coords(self):
        """Docstring"""
        r = self.rect()
        p = self.pos()
        return {"x": r.x()+p.x(), "y": r.y()+p.y(), "w": r.width(), "h": r.height()}


class PolygonItem(QGraphicsPolygonItem):
    """Docstring"""
    def __init__(self, points, class_id, class_name, uid, parent=None):
        poly = QPolygonF([QPointF(x, y) for x, y in points])
        super().__init__(poly, parent)
        self.class_id = class_id
        self.class_name = class_name
        self.uid = uid
        self._is_editing = False
        self._dragging_vertex = -1
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        self._update_style()

    def _update_style(self):
        color = get_class_color(self.class_id)
        fill = get_class_color_with_alpha(self.class_id, 40)
        pen = QPen(color, 2)
        pen.setCosmetic(True)
        self.setPen(pen)
        self.setBrush(QBrush(fill))

    def set_editing(self, editing: bool):
        self._is_editing = editing
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, editing)
        self.update()

    def update_class(self, class_id, class_name):
        self.class_id = class_id
        self.class_name = class_name
        self._update_style()
        self.update()

    def paint(self, painter, option, widget=None):
        """Docstring"""
        super().paint(painter, option, widget)
        poly = self.polygon()
        color = get_class_color(self.class_id)
        if poly.count() > 0:
            cx = sum(poly.at(i).x() for i in range(poly.count())) / poly.count()
            cy = sum(poly.at(i).y() for i in range(poly.count())) / poly.count()
            painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            label = f" {self.class_name} "
            fm = painter.fontMetrics()
            tr = fm.boundingRect(label)
            lbg = QRectF(cx-tr.width()/2-4, cy-tr.height()/2-2, tr.width()+8, tr.height()+4)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(color))
            painter.drawRoundedRect(lbg, 3, 3)
            painter.setPen(QPen(QColor(0, 0, 0)))
            painter.drawText(lbg, Qt.AlignmentFlag.AlignCenter, label)
        if self.isSelected() or self._is_editing:
            for i in range(poly.count()):
                pt = poly.at(i)
                painter.setPen(QPen(QColor(255, 255, 255), 1))
                painter.setBrush(QBrush(color))
                painter.drawEllipse(pt, HANDLE_HALF, HANDLE_HALF)

    def _vertex_at(self, pos, threshold=8.0):
        poly = self.polygon()
        for i in range(poly.count()):
            pt = poly.at(i)
            if math.hypot(pos.x()-pt.x(), pos.y()-pt.y()) <= threshold:
                return i
        return -1

    def mousePressEvent(self, event):
        if self._is_editing and event.button() == Qt.MouseButton.LeftButton:
            vi = self._vertex_at(event.pos())
            if vi >= 0:
                self._dragging_vertex = vi
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging_vertex >= 0:
            poly = self.polygon()
            poly.replace(self._dragging_vertex, event.pos())
            self.setPolygon(poly)
            self.update()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._dragging_vertex = -1
        super().mouseReleaseEvent(event)

    def get_pixel_points(self):
        """Docstring"""
        poly = self.polygon()
        p = self.pos()
        return [(poly.at(i).x()+p.x(), poly.at(i).y()+p.y()) for i in range(poly.count())]

    def boundingRect(self):
        r = super().boundingRect()
        return r.adjusted(-HANDLE_SIZE, -25, HANDLE_SIZE, HANDLE_SIZE)
