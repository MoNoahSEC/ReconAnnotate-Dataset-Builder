"""
Dataset splitter — random train/val split with stratification.
"""
import random
from typing import List, Tuple
from ..models.image_entry import ImageEntry, ImageCategory


def split_dataset(
    images: List[ImageEntry],
    train_ratio: float = 0.8,
    seed: int = 42
) -> Tuple[List[ImageEntry], List[ImageEntry]]:
    """Docstring"""
    random.seed(seed)

    exportable = [
        img for img in images
        if img.category in (ImageCategory.GOOD, ImageCategory.BAD)
    ]

    if not exportable:
        return [], []

    shuffled = list(exportable)
    random.shuffle(shuffled)

    split_idx = max(1, int(len(shuffled) * train_ratio))

    train = shuffled[:split_idx]
    val = shuffled[split_idx:]

    if not val and len(train) > 1:
        val = [train.pop()]

    return train, val
