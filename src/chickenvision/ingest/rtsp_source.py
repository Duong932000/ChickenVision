"""Live RTSP ingest — architecture placeholder only.

Reserved by config schema (chickenvision.config.schema.RtspSourceConfig) so the
`ingest` layer's shape is settled now, but the implementation is locked until
Milestone 1B: real hardware must be chosen first (see CLAUDE.md Phase 1B). Do not
flesh this out early — reconnect/backoff/watchdog behavior belongs to that phase.
"""

from __future__ import annotations

from collections.abc import Iterator

from chickenvision.ingest.base import Frame


class RTSPVideoSource:
    def __init__(self, url: str) -> None:
        self._url = url

    def frames(self) -> Iterator[Frame]:
        raise NotImplementedError(
            f"RTSP ingest for {self._url!r} is Phase 1B — not implemented yet "
            "(locked until hardware is chosen; see CLAUDE.md)"
        )
