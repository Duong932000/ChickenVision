from __future__ import annotations

import logging
from pathlib import Path

import typer

from chickenvision.config.loader import ConfigError, load_config
from chickenvision.dataset.extract_frames import extract_frames_to_dir
from chickenvision.ingest.file_source import FileVideoSource

logger = logging.getLogger(__name__)

dataset_app = typer.Typer(help="Dataset preparation stages (video -> frames -> annotation).")


@dataset_app.command("extract-frames")
def extract_frames_cmd(
    config: Path = typer.Option(..., "--config", help="Path to farm config YAML."),
    house: str = typer.Option(..., "--house", help="house_id in the config."),
    camera: str = typer.Option(..., "--camera", help="camera_id under the given house."),
    out: Path = typer.Option(..., "--out", help="Output directory for frames + manifest."),
    video: Path = typer.Option(
        None,
        "--video",
        help="Override the video path from config (defaults to the camera's file source path).",
    ),
    interval_seconds: float = typer.Option(
        2.0, "--interval-seconds", min=0.0, help="Seconds between sampled frames."
    ),
    max_frames: int = typer.Option(
        None, "--max-frames", min=1, help="Stop after this many frames are kept."
    ),
    dedup_threshold: float = typer.Option(
        2.0,
        "--dedup-threshold",
        help="Skip frames whose mean abs pixel diff from the last kept frame is below "
        "this. Use 0 to disable dedup.",
    ),
) -> None:
    """Sample frames from a recorded video for a given house/camera, writing images
    plus a CSV manifest to --out.
    """
    try:
        farm_config = load_config(config)
    except ConfigError as exc:
        typer.echo(f"Config error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    try:
        camera_config = farm_config.get_camera(house, camera)
    except KeyError as exc:
        typer.echo(f"Config error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    if video is not None:
        video_path = video
    elif camera_config.source.type == "file":
        video_path = camera_config.source.path
    else:
        typer.echo(
            f"Camera {camera!r} source type {camera_config.source.type!r} has no static "
            "video file — pass --video explicitly, or use a 'file' source in the config.",
            err=True,
        )
        raise typer.Exit(code=1)

    if not video_path.is_file():
        typer.echo(f"Video not found: {video_path}", err=True)
        raise typer.Exit(code=1)

    source = FileVideoSource(video_path)
    effective_dedup = dedup_threshold if dedup_threshold > 0 else None

    manifest_path = extract_frames_to_dir(
        source,
        out,
        video_name=video_path.stem,
        interval_seconds=interval_seconds,
        max_frames=max_frames,
        dedup_threshold=effective_dedup,
    )
    typer.echo(f"Manifest written to {manifest_path}")
