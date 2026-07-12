"""Ingest layer interface — consumed by dataset/detect/track without caring whether
frames come from a recorded file (Phase 1A) or a live RTSP stream (Phase 1B).
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol

import numpy as np


@dataclass(frozen=True, slots=True)
class Frame:
    image: np.ndarray
    frame_index: int
    timestamp_s: float


class VideoSource(Protocol):
    def frames(self) -> Iterator[Frame]:
        """Yield frames in order, starting at frame_index=0."""
        ...
