from __future__ import annotations

import csv
from pathlib import Path

from chickenvision.dataset.extract_frames import extract_frames_to_dir
from chickenvision.ingest.file_source import FileVideoSource


def _read_manifest(manifest_path: Path) -> list[dict[str, str]]:
    with manifest_path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_extract_frames_writes_images_and_manifest(synthetic_video: Path, tmp_path: Path) -> None:
    out_dir = tmp_path / "frames"
    source = FileVideoSource(synthetic_video)

    manifest_path = extract_frames_to_dir(
        source,
        out_dir,
        video_name="synthetic",
        interval_seconds=0.1,
        dedup_threshold=5.0,
    )

    rows = _read_manifest(manifest_path)
    assert len(rows) > 0
    for row in rows:
        assert Path(row["output_path"]).exists()

    # the held-still stretch in the fixture should get deduped away, so we keep
    # fewer frames than the 20 total frames in the source video
    assert len(rows) < 20


def test_extract_frames_respects_max_frames(synthetic_video: Path, tmp_path: Path) -> None:
    out_dir = tmp_path / "frames_capped"
    source = FileVideoSource(synthetic_video)

    manifest_path = extract_frames_to_dir(
        source,
        out_dir,
        video_name="synthetic",
        interval_seconds=0.0,
        max_frames=3,
        dedup_threshold=None,
    )

    assert len(_read_manifest(manifest_path)) == 3


def test_extract_frames_dedup_disabled_keeps_every_sampled_frame(
    synthetic_video: Path, tmp_path: Path
) -> None:
    out_dir = tmp_path / "frames_no_dedup"
    source = FileVideoSource(synthetic_video)

    manifest_path = extract_frames_to_dir(
        source,
        out_dir,
        video_name="synthetic",
        interval_seconds=0.0,
        dedup_threshold=None,
    )

    # interval_seconds=0 with dedup disabled samples every frame in the source
    assert len(_read_manifest(manifest_path)) == 20
