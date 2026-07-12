"""YAML -> validated FarmConfig, failing loudly on any problem.

The farm runs unattended (CLAUDE.md mục 1) — a bad config must raise a clear error
immediately, never fall back to a silent default.
"""

from __future__ import annotations

import logging
from pathlib import Path

import yaml
from pydantic import ValidationError

from chickenvision.config.schema import FarmConfig

logger = logging.getLogger(__name__)


class ConfigError(RuntimeError):
    """Raised when a farm config file is missing, malformed, or fails validation."""


def load_config(path: Path) -> FarmConfig:
    if not path.is_file():
        raise ConfigError(f"Config file not found: {path}")

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML in {path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ConfigError(
            f"Config {path} must be a YAML mapping at the top level, got {type(raw).__name__}"
        )

    try:
        config = FarmConfig.model_validate(raw)
    except ValidationError as exc:
        raise ConfigError(f"Config {path} failed validation:\n{exc}") from exc

    logger.info("Loaded config for farm_id=%s from %s", config.farm_id, path)
    return config
