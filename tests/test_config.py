from __future__ import annotations

from pathlib import Path

import pytest

from chickenvision.config.loader import ConfigError, load_config

VALID_YAML = """
farm_id: an_giang_01
paths:
  data_root: data/
  frames_root: data/frames/
  dataset_root: data/datasets/
houses:
  - house_id: house_01
    cameras:
      - camera_id: cam_01
        source:
          type: file
          path: data/raw_videos/sample.mp4
"""


def test_load_config_valid(tmp_path: Path) -> None:
    config_path = tmp_path / "farm.yaml"
    config_path.write_text(VALID_YAML)

    config = load_config(config_path)

    assert config.farm_id == "an_giang_01"
    camera = config.get_camera("house_01", "cam_01")
    assert camera.source.type == "file"
    assert camera.source.path == Path("data/raw_videos/sample.mp4")


def test_load_config_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="not found"):
        load_config(tmp_path / "missing.yaml")


def test_load_config_missing_required_field(tmp_path: Path) -> None:
    config_path = tmp_path / "farm.yaml"
    config_path.write_text("farm_id: an_giang_01\n")  # missing paths/houses

    with pytest.raises(ConfigError, match="failed validation"):
        load_config(config_path)


def test_get_camera_unknown_raises_key_error(tmp_path: Path) -> None:
    config_path = tmp_path / "farm.yaml"
    config_path.write_text(VALID_YAML)
    config = load_config(config_path)

    with pytest.raises(KeyError):
        config.get_camera("house_01", "does_not_exist")
