"""VideoSource backed by a local video file, via OpenCV's ffmpeg backend.

ffmpeg is expected to be installed at the OS level (README has per-OS install
instructions) — see docs/decisions/0001-phase0-tooling.md for why this project
does not bundle a pip ffmpeg binary instead.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from pathlib import Path

import cv2

from chickenvision.ingest.base import Frame

logger = logging.getLogger(__name__)


class VideoOpenError(RuntimeError):
    """Raised when a video file cannot be opened for reading."""


class FileVideoSource:
    def __init__(self, path: Path) -> None:
        self._path = path

    def frames(self) -> Iterator[Frame]:
        capture = cv2.VideoCapture(str(self._path), cv2.CAP_FFMPEG)
        if not capture.isOpened():
            raise VideoOpenError(
                f"Could not open video {self._path} (is ffmpeg installed and on PATH?)"
            )

        fps = capture.get(cv2.CAP_PROP_FPS) or 0.0
        frame_index = 0
        try:
            while True:
                ok, image = capture.read()
                if not ok:
                    break
                timestamp_s = frame_index / fps if fps > 0 else 0.0
                yield Frame(image=image, frame_index=frame_index, timestamp_s=timestamp_s)
                frame_index += 1
        finally:
            capture.release()

        logger.info("Read %d frames from %s", frame_index, self._path)
