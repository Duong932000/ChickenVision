"""Stage 2 of the pipeline (CLAUDE.md mục 3b): video -> sampled frames + manifest.

Sampling is a deliberately simple heuristic — fixed time interval plus a
near-duplicate skip via mean absolute pixel difference — not active-learning frame
selection. That belongs to the CVAT bootstrap loop once a first model exists (see
docs/decisions/0001-phase0-tooling.md).
"""

from __future__ import annotations

import csv
import logging
from collections.abc import Iterator
from pathlib import Path

import cv2
import numpy as np

from chickenvision.ingest.base import Frame, VideoSource

logger = logging.getLogger(__name__)

MANIFEST_FIELDNAMES = ["frame_index", "timestamp_s", "source_video", "output_path"]


def _mean_abs_diff(a: np.ndarray, b: np.ndarray) -> float:
    if a.shape != b.shape:
        return 255.0  # different shape => treat as maximally different, always keep
    return float(np.mean(cv2.absdiff(a, b)))


def sample_frames(
    source: VideoSource,
    *,
    interval_seconds: float = 2.0,
    max_frames: int | None = None,
    dedup_threshold: float | None = 2.0,
) -> Iterator[Frame]:
    """Yield frames from `source` at a fixed time interval, skipping frames whose
    mean absolute pixel difference from the last kept frame is below
    `dedup_threshold` (set to None to disable dedup).
    """
    next_sample_at = 0.0
    last_kept: np.ndarray | None = None
    kept = 0

    for frame in source.frames():
        if frame.timestamp_s + 1e-9 < next_sample_at:
            continue

        if (
            dedup_threshold is not None
            and last_kept is not None
            and _mean_abs_diff(frame.image, last_kept) < dedup_threshold
        ):
            next_sample_at = frame.timestamp_s + interval_seconds
            continue

        yield frame
        last_kept = frame.image
        kept += 1
        next_sample_at = frame.timestamp_s + interval_seconds

        if max_frames is not None and kept >= max_frames:
            break

    logger.info(
        "Sampled %d frames (interval_seconds=%.2f, dedup_threshold=%s)",
        kept,
        interval_seconds,
        dedup_threshold,
    )


def extract_frames_to_dir(
    source: VideoSource,
    out_dir: Path,
    *,
    video_name: str,
    interval_seconds: float = 2.0,
    max_frames: int | None = None,
    dedup_threshold: float | None = 2.0,
) -> Path:
    """Sample frames and write them as JPEGs + a CSV manifest into `out_dir`.

    Returns the manifest path — the provenance record consumed when importing a
    batch into CVAT (mục 3b, stage 2 -> 3 của pipeline).
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / f"{video_name}_manifest.csv"

    with manifest_path.open("w", newline="", encoding="utf-8") as manifest_file:
        writer = csv.DictWriter(manifest_file, fieldnames=MANIFEST_FIELDNAMES)
        writer.writeheader()

        written = 0
        for frame in sample_frames(
            source,
            interval_seconds=interval_seconds,
            max_frames=max_frames,
            dedup_threshold=dedup_threshold,
        ):
            output_path = out_dir / f"{video_name}_{frame.frame_index:06d}.jpg"
            if not cv2.imwrite(str(output_path), frame.image):
                raise OSError(f"Failed to write frame image to {output_path}")

            writer.writerow(
                {
                    "frame_index": frame.frame_index,
                    "timestamp_s": f"{frame.timestamp_s:.3f}",
                    "source_video": video_name,
                    "output_path": str(output_path),
                }
            )
            written += 1

    logger.info("Wrote %d frames + manifest to %s", written, manifest_path)
    return manifest_path
