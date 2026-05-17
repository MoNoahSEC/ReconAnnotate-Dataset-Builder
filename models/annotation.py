"""
Annotation data models for bounding boxes and polygons.
"""
from dataclasses import dataclass, field
from typing import List, Tuple
import uuid


@dataclass
class BBoxAnnotation:
    """Docstring"""
    class_id: int
    x: float  
    y: float  
    w: float  
    h: float  
    uid: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    @property
    def x_center(self) -> float:
        """Docstring"""
        return self.x + self.w / 2.0

    @property
    def y_center(self) -> float:
        """Docstring"""
        return self.y + self.h / 2.0

    def to_normalized_line(self, img_w: int, img_h: int) -> str:
        """Docstring"""
        xc = self.x_center / img_w
        yc = self.y_center / img_h
        w = self.w / img_w
        h = self.h / img_h
        xc = max(0.0, min(1.0, xc))
        yc = max(0.0, min(1.0, yc))
        w = max(0.0, min(1.0, w))
        h = max(0.0, min(1.0, h))
        return f"{self.class_id} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}"

    def to_dict(self) -> dict:
        """Docstring"""
        return {
            "type": "bbox",
            "class_id": self.class_id,
            "x": self.x,
            "y": self.y,
            "w": self.w,
            "h": self.h,
            "uid": self.uid,
        }

    @staticmethod
    def from_dict(d: dict) -> "BBoxAnnotation":
        """Docstring"""
        return BBoxAnnotation(
            class_id=d["class_id"],
            x=d["x"], y=d["y"], w=d["w"], h=d["h"],
            uid=d.get("uid", str(uuid.uuid4())[:8]),
        )


@dataclass
class PolygonAnnotation:
    """Docstring"""
    class_id: int
    points: List[Tuple[float, float]] = field(default_factory=list)
    uid: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_normalized_line(self, img_w: int, img_h: int) -> str:
        """Docstring"""
        parts = [str(self.class_id)]
        for px, py in self.points:
            nx = max(0.0, min(1.0, px / img_w))
            ny = max(0.0, min(1.0, py / img_h))
            parts.append(f"{nx:.6f}")
            parts.append(f"{ny:.6f}")
        return " ".join(parts)

    def to_dict(self) -> dict:
        """Docstring"""
        return {
            "type": "polygon",
            "class_id": self.class_id,
            "points": list(self.points),
            "uid": self.uid,
        }

    @staticmethod
    def from_dict(d: dict) -> "PolygonAnnotation":
        """Docstring"""
        pts = [tuple(p) for p in d["points"]]
        return PolygonAnnotation(
            class_id=d["class_id"],
            points=pts,
            uid=d.get("uid", str(uuid.uuid4())[:8]),
        )
