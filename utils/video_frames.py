"""
Video frame extraction utilities (with de-duplication).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np
from PIL import Image


@dataclass(frozen=True)
class VideoMeta:
    path: str
    fps: float
    frame_count: int
    width: int
    height: int
    duration_s: float


@dataclass(frozen=True)
class ExtractPlan:
    # sample one frame every N frames (>= 1)
    frame_step: int
    # bounds to avoid “too few/too many”
    min_images: int
    max_images: int
    # dedup
    dedup_hamming_threshold: int
    # minimum accepted Hamming distance vs last kept frame
    # (0 = keep all)


def _ahash(img_rgb: np.ndarray, size: int = 8) -> int:
    """
    Average-hash for quick near-duplicate detection.
    Returns 64-bit int.
    """
    pil = Image.fromarray(img_rgb)
    pil = pil.resize((size, size), Image.Resampling.BILINEAR).convert("L")
    arr = np.asarray(pil, dtype=np.float32)
    mean = arr.mean()
    bits = (arr > mean).astype(np.uint8).flatten()
    h = 0
    for b in bits:
        h = (h << 1) | int(b)
    return int(h)


def _hamming64(a: int, b: int) -> int:
    return int((a ^ b).bit_count())


def read_video_meta(video_path: str) -> VideoMeta:
    try:
        import cv2  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "OpenCV is required for video import. Install: pip install opencv-python"
        ) from e

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {video_path}")

    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    cap.release()

    duration_s = float(frame_count / fps) if fps > 0 and frame_count > 0 else 0.0
    return VideoMeta(
        path=video_path,
        fps=fps,
        frame_count=frame_count,
        width=width,
        height=height,
        duration_s=duration_s,
    )


def estimate_images(meta: VideoMeta, frame_step: int) -> int:
    if meta.frame_count <= 0:
        return 0
    step = max(1, int(frame_step))
    return int((meta.frame_count + step - 1) // step)


def choose_frame_step_for_range(meta: VideoMeta, min_images: int, max_images: int) -> int:
    """
    Pick a reasonable frame_step to land within [min_images, max_images] if possible.
    """
    if meta.frame_count <= 0:
        return 1
    min_images = max(1, int(min_images))
    max_images = max(min_images, int(max_images))

    # If we sample every frame, this is the maximum possible.
    if meta.frame_count <= max_images:
        return 1

    # Choose step to target the middle of the range.
    target = (min_images + max_images) / 2.0
    step = int(round(meta.frame_count / max(target, 1.0)))
    return max(1, step)


def extract_frames(
    video_path: str,
    output_dir: str,
    plan: ExtractPlan,
    progress_cb: Optional[Callable[[int, int], None]] = None,
) -> list[str]:
    """
    Extract frames as JPG into output_dir, applying dedup + min/max caps.
    Returns list of saved image paths.
    """
    try:
        import cv2  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "OpenCV is required for video import. Install: pip install opencv-python"
        ) from e

    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {video_path}")

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    step = max(1, int(plan.frame_step))
    min_images = max(1, int(plan.min_images))
    max_images = max(min_images, int(plan.max_images))
    thr = max(0, int(plan.dedup_hamming_threshold))

    saved: list[str] = []
    last_hash: Optional[int] = None

    frame_idx = 0
    kept_attempts = 0
    while True:
        ok, frame_bgr = cap.read()
        if not ok:
            break

        if frame_idx % step != 0:
            frame_idx += 1
            continue

        # Stop if we reached max images.
        if len(saved) >= max_images:
            break

        frame_rgb = frame_bgr[:, :, ::-1]  # BGR -> RGB
        h = _ahash(frame_rgb)
        if last_hash is not None and thr > 0:
            if _hamming64(last_hash, h) <= thr:
                frame_idx += 1
                if progress_cb:
                    progress_cb(frame_idx, total)
                continue

        # Save
        kept_attempts += 1
        fname = f"frame_{frame_idx:08d}.jpg"
        out_path = os.path.join(output_dir, fname)
        # Use cv2.imwrite for speed (expects BGR)
        cv2.imwrite(out_path, frame_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        saved.append(out_path)
        last_hash = h

        frame_idx += 1
        if progress_cb:
            progress_cb(frame_idx, total)

    cap.release()

    # If we ended up with too few images because of dedup, relax dedup once (simple fallback).
    if len(saved) < min_images and thr > 0:
        # try again with thr=0 but keep max_images
        cap = cv2.VideoCapture(video_path)
        if cap.isOpened():
            frame_idx = 0
            while len(saved) < min_images:
                ok, frame_bgr = cap.read()
                if not ok:
                    break
                if frame_idx % step != 0:
                    frame_idx += 1
                    continue
                fname = f"frame_{frame_idx:08d}_extra.jpg"
                out_path = os.path.join(output_dir, fname)
                cv2.imwrite(out_path, frame_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
                saved.append(out_path)
                frame_idx += 1
            cap.release()

    return saved

