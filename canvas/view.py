"""
AnnotationView — QGraphicsView with zoom, pan, and crosshair cursor.
"""
from PyQt6.QtWidgets import QGraphicsView
from PyQt6.QtGui import QPainter, QPen, QColor, QCursor, QPixmap, QBrush
from PyQt6.QtCore import Qt, QPoint, pyqtSignal


class AnnotationView(QGraphicsView):
    """Docstring"""
    zoom_changed = pyqtSignal(int)

    MIN_ZOOM = 0.1
    MAX_ZOOM = 20.0

    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self._zoom = 1.0
        self._panning = False
        self._pan_start = QPoint()
        self._mouse_pos = QPoint()

        self.setRenderHints(
            QPainter.RenderHint.Antialiasing
        )
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.SmartViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.setStyleSheet("QGraphicsView { border: none; }")
        self.setBackgroundBrush(QBrush(QColor("#fffaf6")))

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        blank = QPixmap(1, 1)
        blank.fill(Qt.GlobalColor.transparent)
        self._crosshair_cursor = QCursor(blank)

    def fit_image(self):
        """Docstring"""
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self._zoom = self.transform().m11()
        self.zoom_changed.emit(int(self._zoom * 100))

    def set_zoom(self, factor):
        """Docstring"""
        self._zoom = max(self.MIN_ZOOM, min(self.MAX_ZOOM, factor))
        self.resetTransform()
        self.scale(self._zoom, self._zoom)
        self.zoom_changed.emit(int(self._zoom * 100))

    def wheelEvent(self, event):
        """Docstring"""
        delta = event.angleDelta().y()
        if delta > 0:
            factor = 1.15
        else:
            factor = 1 / 1.15

        new_zoom = self._zoom * factor
        if self.MIN_ZOOM <= new_zoom <= self.MAX_ZOOM:
            self._zoom = new_zoom
            self.scale(factor, factor)
            self.zoom_changed.emit(int(self._zoom * 100))

    def mousePressEvent(self, event):
        """Docstring"""
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._pan_start = event.position().toPoint()
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Docstring"""
        self._mouse_pos = event.position().toPoint()

        if self._panning:
            delta = event.position().toPoint() - self._pan_start
            self._pan_start = event.position().toPoint()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            event.accept()
        else:
            super().mouseMoveEvent(event)

        self.viewport().update()

    def mouseReleaseEvent(self, event):
        """Docstring"""
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = False
            self.setCursor(self._crosshair_cursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def enterEvent(self, event):
        """Docstring"""
        self.setCursor(self._crosshair_cursor)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Docstring"""
        self.unsetCursor()
        self.viewport().update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        """Docstring"""
        super().paintEvent(event)

        if self.underMouse():
            painter = QPainter(self.viewport())
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

            pen = QPen(QColor(255, 107, 0, 100), 1)
            pen.setStyle(Qt.PenStyle.SolidLine)
            painter.setPen(pen)

            mx = self._mouse_pos.x()
            my = self._mouse_pos.y()
            vw = self.viewport().width()
            vh = self.viewport().height()

            painter.drawLine(0, my, vw, my)
            painter.drawLine(mx, 0, mx, vh)

            center_pen = QPen(QColor(255, 107, 0, 220), 2)
            painter.setPen(center_pen)
            painter.drawPoint(mx, my)

            scene_pos = self.mapToScene(self._mouse_pos)
            coord_text = f"({int(scene_pos.x())}, {int(scene_pos.y())})"
            painter.setPen(QPen(QColor(30, 41, 59, 200)))
            from PyQt6.QtGui import QFont
            painter.setFont(QFont("Consolas", 9))
            painter.drawText(mx + 15, my - 10, coord_text)

            painter.end()

    def keyPressEvent(self, event):
        """Docstring"""
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            scene = self.scene()
            if hasattr(scene, 'close_polygon'):
                scene.close_polygon()
                return
        elif event.key() == Qt.Key.Key_Escape:
            scene = self.scene()
            if hasattr(scene, 'cancel_current'):
                scene.cancel_current()
                return
        elif event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            scene = self.scene()
            if hasattr(scene, 'delete_selected'):
                scene.delete_selected()
                return
        super().keyPressEvent(event)
