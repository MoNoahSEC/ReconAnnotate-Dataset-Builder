"""
Video import dialog — choose category, extraction limits, and dedup settings.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QPushButton,
    QFileDialog,
    QGroupBox,
    QMessageBox,
)

from ..utils.video_frames import (
    VideoMeta,
    ExtractPlan,
    read_video_meta,
    estimate_images,
    choose_frame_step_for_range,
)


@dataclass(frozen=True)
class VideoImportConfig:
    output_dir: str
    plan: ExtractPlan
    meta: VideoMeta


class VideoImportDialog(QDialog):
    def __init__(self, video_path: str, default_output_dir: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Video → Frames")
        self.setModal(True)
        self._video_path = video_path
        self._meta: VideoMeta | None = None
        self._result: VideoImportConfig | None = None

        self._output_dir = default_output_dir

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        self._title = QLabel(f"Video: {os.path.basename(video_path)}")
        self._title.setObjectName("SectionTitle")
        layout.addWidget(self._title)

        self._meta_lbl = QLabel("Reading video info…")
        self._meta_lbl.setObjectName("SubLabel")
        layout.addWidget(self._meta_lbl)

        out_row = QHBoxLayout()
        out_row.addWidget(QLabel("Output folder:"), stretch=0)
        self._out_value = QLabel(self._output_dir)
        self._out_value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        out_row.addWidget(self._out_value, stretch=1)
        browse = QPushButton("Browse…")
        browse.clicked.connect(self._browse_output)
        out_row.addWidget(browse, stretch=0)
        layout.addLayout(out_row)

        grp = QGroupBox("Limits & De-duplication")
        g = QVBoxLayout(grp)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Min images:"), 0)
        self._min = QSpinBox()
        self._min.setRange(1, 1000000)
        self._min.setValue(200)
        r1.addWidget(self._min, 1)
        r1.addWidget(QLabel("Max images:"), 0)
        self._max = QSpinBox()
        self._max.setRange(1, 1000000)
        self._max.setValue(2000)
        r1.addWidget(self._max, 1)
        g.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Frame step (every N frames):"), 0)
        self._step = QSpinBox()
        self._step.setRange(1, 1000000)
        self._step.setValue(5)
        self._step.setToolTip("Sample 1 frame every N frames. Smaller = more images.")
        r2.addWidget(self._step, 1)
        auto_step = QPushButton("Auto")
        auto_step.setToolTip("Auto-pick a step to fall within your min/max range.")
        auto_step.clicked.connect(self._auto_pick_step)
        r2.addWidget(auto_step, 0)
        g.addLayout(r2)

        r3 = QHBoxLayout()
        r3.addWidget(QLabel("Dedup threshold (0=off):"), 0)
        self._dedup = QSpinBox()
        self._dedup.setRange(0, 64)
        self._dedup.setValue(5)
        self._dedup.setToolTip("Higher = more aggressive removing near-duplicates.")
        r3.addWidget(self._dedup, 1)
        g.addLayout(r3)

        layout.addWidget(grp)

        self._estimate = QLabel("Estimated: —")
        self._estimate.setObjectName("SubLabel")
        layout.addWidget(self._estimate)

        btns = QHBoxLayout()
        btns.addStretch()
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        ok = QPushButton("Import")
        ok.setObjectName("AccentButton")
        ok.clicked.connect(self._accept)
        btns.addWidget(cancel)
        btns.addWidget(ok)
        layout.addLayout(btns)

        # Load meta + hook recompute
        self._load_meta()
        self._min.valueChanged.connect(self._recompute_estimate)
        self._max.valueChanged.connect(self._recompute_estimate)
        self._step.valueChanged.connect(self._recompute_estimate)
        self._dedup.valueChanged.connect(self._recompute_estimate)

    def _load_meta(self):
        try:
            self._meta = read_video_meta(self._video_path)
        except Exception as e:
            QMessageBox.critical(self, "Video Error", str(e))
            self.reject()
            return

        m = self._meta
        self._meta_lbl.setText(
            f"{m.width}×{m.height} | fps: {m.fps:.2f} | frames: {m.frame_count} | duration: {m.duration_s:.1f}s"
        )
        self._recompute_estimate()

    def _browse_output(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", self._output_dir)
        if folder:
            self._output_dir = folder
            self._out_value.setText(folder)

    def _auto_pick_step(self):
        if not self._meta:
            return
        mn = self._min.value()
        mx = self._max.value()
        step = choose_frame_step_for_range(self._meta, mn, mx)
        self._step.setValue(step)

    def _recompute_estimate(self):
        if not self._meta:
            self._estimate.setText("Estimated: —")
            return
        est = estimate_images(self._meta, self._step.value())
        mn = self._min.value()
        mx = self._max.value()
        hint = ""
        if est > mx:
            hint = " (too many → increase step or lower max)"
        elif est < mn:
            hint = " (too few → decrease step or lower min)"
        self._estimate.setText(f"Estimated images (before dedup): {est}{hint}")

    def _accept(self):
        if not self._meta:
            return
        mn = self._min.value()
        mx = self._max.value()
        if mx < mn:
            QMessageBox.warning(self, "Invalid Limits", "Max images must be >= Min images.")
            return
        if not self._output_dir:
            QMessageBox.warning(self, "Output Folder", "Please select an output folder.")
            return

        plan = ExtractPlan(
            frame_step=self._step.value(),
            min_images=mn,
            max_images=mx,
            dedup_hamming_threshold=self._dedup.value(),
        )
        self._result = VideoImportConfig(output_dir=self._output_dir, plan=plan, meta=self._meta)
        self.accept()

    def result_config(self) -> VideoImportConfig | None:
        return self._result

