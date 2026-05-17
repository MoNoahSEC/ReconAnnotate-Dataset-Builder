"""
Dataset format exporter — creates the complete dataset structure with normalized annotations.
"""
import os
import shutil
import yaml
from typing import List
from ..models.image_entry import ImageEntry, ImageCategory
from ..models.annotation import BBoxAnnotation, PolygonAnnotation
from .splitter import split_dataset


class DatasetExporter:
    """Docstring"""

    def __init__(self, output_dir: str, class_names: List[str], train_ratio: float = 0.8):
        """Docstring"""
        self._output_dir = output_dir
        self._class_names = class_names
        self._train_ratio = train_ratio
        self._errors = []

    def export(self, images: List[ImageEntry], progress_callback=None) -> dict:
        """Docstring"""
        self._errors = []

        dirs = self._create_directories()

        train_imgs, val_imgs = split_dataset(images, self._train_ratio)

        total = len(train_imgs) + len(val_imgs)
        processed = 0

        train_stats = {"images": 0, "annotations": 0, "backgrounds": 0}
        for img in train_imgs:
            self._export_image(img, dirs["images_train"], dirs["labels_train"], train_stats, dirs)
            processed += 1
            if progress_callback:
                progress_callback(int(processed / max(total, 1) * 100))

        val_stats = {"images": 0, "annotations": 0, "backgrounds": 0}
        for img in val_imgs:
            self._export_image(img, dirs["images_val"], dirs["labels_val"], val_stats, dirs)
            processed += 1
            if progress_callback:
                progress_callback(int(processed / max(total, 1) * 100))

        self._create_data_yaml()

        return {
            "output_dir": self._output_dir,
            "train_images": train_stats["images"],
            "train_annotations": train_stats["annotations"],
            "train_backgrounds": train_stats["backgrounds"],
            "val_images": val_stats["images"],
            "val_annotations": val_stats["annotations"],
            "val_backgrounds": val_stats["backgrounds"],
            "classes": len(self._class_names),
            "errors": self._errors,
        }

    def _create_directories(self) -> dict:
        """Docstring"""
        dirs = {
            "images_train": os.path.join(self._output_dir, "images", "train"),
            "images_val": os.path.join(self._output_dir, "images", "val"),
            "labels_train": os.path.join(self._output_dir, "labels", "train"),
            "labels_val": os.path.join(self._output_dir, "labels", "val"),
            "sort_good": os.path.join(self._output_dir, "Good"),
            "sort_bad": os.path.join(self._output_dir, "Bad"),
            "sort_empty": os.path.join(self._output_dir, "Empty"),
        }
        for d in dirs.values():
            os.makedirs(d, exist_ok=True)
        return dirs

    def _export_image(self, img: ImageEntry, img_dir: str, lbl_dir: str, stats: dict, dirs: dict):
        """Docstring"""
        try:
            from ..utils.path_resolver import resolve_case_insensitive_path
            src = resolve_case_insensitive_path(img.path)
            dst = os.path.join(img_dir, img.filename)
            if os.path.exists(src):
                shutil.copy2(src, dst)
            else:
                self._errors.append(f"Image not found: {src}")
                return

            stats["images"] += 1

            if img.category == ImageCategory.GOOD:
                shutil.copy2(src, os.path.join(dirs["sort_good"], img.filename))
            elif img.category == ImageCategory.BAD:
                shutil.copy2(src, os.path.join(dirs["sort_bad"], img.filename))
            elif img.category == ImageCategory.EMPTY:
                shutil.copy2(src, os.path.join(dirs["sort_empty"], img.filename))

            label_name = os.path.splitext(img.filename)[0] + ".txt"
            label_path = os.path.join(lbl_dir, label_name)

            if img.annotations and img.category in (ImageCategory.GOOD, ImageCategory.BAD):
                lines = []
                for ann in img.annotations:
                    line = ann.to_normalized_line(img.width, img.height)
                    lines.append(line)
                    stats["annotations"] += 1

                with open(label_path, "w") as f:
                    f.write("\n".join(lines) + "\n")

            elif img.category in (ImageCategory.GOOD, ImageCategory.EMPTY):
                with open(label_path, "w") as f:
                    pass
                stats["backgrounds"] += 1

            elif img.category == ImageCategory.BAD and not img.annotations:
                with open(label_path, "w") as f:
                    pass
                self._errors.append(
                    f"Warning: '{img.filename}' marked as Bad but has no annotations"
                )

        except Exception as e:
            self._errors.append(f"Error exporting '{img.filename}': {str(e)}")

    def _create_data_yaml(self):
        """Docstring"""
        data = {
            "path": os.path.abspath(self._output_dir),
            "train": "images/train",
            "val": "images/val",
            "nc": len(self._class_names),
            "names": list(self._class_names),
        }

        yaml_path = os.path.join(self._output_dir, "data.yaml")
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
