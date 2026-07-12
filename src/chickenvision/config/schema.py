"""Farm/house/camera config schema.

Scale is a config change, not a code change (CLAUDE.md mục 4): a second house or
camera is a new list entry in the YAML, never a hard-coded value in this module.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class FileSourceConfig(BaseModel):
    type: Literal["file"] = "file"
    path: Path


class RtspSourceConfig(BaseModel):
    """Reserved for Milestone 1B. FileVideoSource cannot consume this yet — see
    chickenvision.ingest.rtsp_source.RTSPVideoSource, which raises NotImplementedError.
    """

    type: Literal["rtsp"] = "rtsp"
    url: str


CameraSourceConfig = Annotated[FileSourceConfig | RtspSourceConfig, Field(discriminator="type")]


class CameraConfig(BaseModel):
    camera_id: str
    source: CameraSourceConfig


class HouseConfig(BaseModel):
    house_id: str
    cameras: list[CameraConfig]


class PathsConfig(BaseModel):
    data_root: Path
    frames_root: Path
    dataset_root: Path


class FarmConfig(BaseModel):
    farm_id: str
    paths: PathsConfig
    houses: list[HouseConfig]

    def get_house(self, house_id: str) -> HouseConfig:
        for house in self.houses:
            if house.house_id == house_id:
                return house
        raise KeyError(f"house_id {house_id!r} not found in farm {self.farm_id!r}")

    def get_camera(self, house_id: str, camera_id: str) -> CameraConfig:
        house = self.get_house(house_id)
        for camera in house.cameras:
            if camera.camera_id == camera_id:
                return camera
        raise KeyError(
            f"camera_id {camera_id!r} not found in house {house_id!r} (farm {self.farm_id!r})"
        )
