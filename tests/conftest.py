"""Synthetic video fixture for pipeline tests.

Generated in-process rather than committed as a binary in tests/fixtures/ — no real
farm footage exists yet to use as a representative sample. Replace with a short real
house clip once Dương has one available (see docs/decisions/0001-phase0-tooling.md).
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

FPS = 10.0
WIDTH = 64
HEIGHT = 48


def _make_frame(step: int) -> np.ndarray:
    image = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    x = (step * 4) % (WIDTH - 10)
    cv2.rectangle(image, (x, 10), (x + 10, 30), (255, 255, 255), thickness=-1)
    return image


@pytest.fixture
def synthetic_video(tmp_path: Path) -> Path:
    """A short synthetic clip: moves every frame for a stretch, then holds a
    near-identical frame for a stretch, then moves again — enough structure to
    exercise both interval sampling and near-duplicate dedup.
    """
    video_path = tmp_path / "synthetic.avi"
    writer = cv2.VideoWriter(str(video_path), cv2.VideoWriter_fourcc(*"MJPG"), FPS, (WIDTH, HEIGHT))
    assert writer.isOpened()

    steps = [0, 1, 2, 3, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 7, 8, 9, 10, 11]
    try:
        for step in steps:
            writer.write(_make_frame(step))
    finally:
        writer.release()

    return video_path
