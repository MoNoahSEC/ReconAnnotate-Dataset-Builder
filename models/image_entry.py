"""
Image entry model — represents a single image and its annotations.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Union
from .annotation import BBoxAnnotation, PolygonAnnotation


class ImageCategory(Enum):
    """Docstring"""
    UNCLASSIFIED = "unclassified"
    GOOD = "good"
    BAD = "bad"
    EMPTY = "empty"


@dataclass
class ImageEntry:
    """Docstring"""
    path: str
    filename: str
    width: int = 0
    height: int = 0
    product_id: int = 0
    category: ImageCategory = ImageCategory.UNCLASSIFIED
    annotations: List[Union[BBoxAnnotation, PolygonAnnotation]] = field(default_factory=list)

    @property
    def is_annotated(self) -> bool:
        """Docstring"""
        return len(self.annotations) > 0

    @property
    def annotation_count(self) -> int:
        """Docstring"""
        return len(self.annotations)

    def add_annotation(self, ann: Union[BBoxAnnotation, PolygonAnnotation]):
        """Docstring"""
        self.annotations.append(ann)

    def remove_annotation(self, uid: str):
        """Docstring"""
        self.annotations = [a for a in self.annotations if a.uid != uid]

    def get_annotation_by_uid(self, uid: str):
        """Docstring"""
        for a in self.annotations:
            if a.uid == uid:
                return a
        return None

    def to_dict(self) -> dict:
        """Docstring"""
        return {
            "path": self.path,
            "filename": self.filename,
            "width": self.width,
            "height": self.height,
            "product_id": self.product_id,
            "category": self.category.value,
            "annotations": [a.to_dict() for a in self.annotations],
        }

    @staticmethod
    def from_dict(d: dict) -> "ImageEntry":
        """Docstring"""
        annotations = []
        for ad in d.get("annotations", []):
            if ad["type"] == "bbox":
                annotations.append(BBoxAnnotation.from_dict(ad))
            elif ad["type"] == "polygon":
                annotations.append(PolygonAnnotation.from_dict(ad))

        return ImageEntry(
            path=d["path"],
            filename=d["filename"],
            width=d.get("width", 0),
            height=d.get("height", 0),
            product_id=int(d.get("product_id", 0) or 0),
            category=ImageCategory(d.get("category", "unclassified")),
            annotations=annotations,
        )
