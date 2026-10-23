from dataclasses import dataclass


@dataclass(frozen=True)
class RoundCaptureStats:
    frames: int
    unique_frames: int
    duration_seconds: float
    stream_fps: float
    duplicate_ratio: float
    wheel_view_ratio: float | None


class CaptureStatsAccumulator:
    """Collects per-round capture quality so later analysis can skip spins
    whose video was too choppy or never showed the wheel."""

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self._frames = 0
        self._unique = 0
        self._wheel_frames = 0
        self._wheel_checked = 0
        self._first: float | None = None
        self._last: float | None = None

    def push(self, timestamp: float, is_duplicate: bool, wheel_visible: bool | None = None) -> None:
        if self._first is None: self._first = timestamp
        self._last = timestamp
        self._frames += 1
        if not is_duplicate: self._unique += 1
        if wheel_visible is not None:
            self._wheel_checked += 1
            if wheel_visible: self._wheel_frames += 1

    def summary(self) -> RoundCaptureStats | None:
        if self._frames == 0: return None
        duration = (self._last - self._first) if self._first is not None else 0.0
        return RoundCaptureStats(
            frames=self._frames,
            unique_frames=self._unique,
            duration_seconds=duration,
            stream_fps=(self._unique - 1) / duration if duration > 0 and self._unique > 1 else 0.0,
            duplicate_ratio=1 - self._unique / self._frames,
            wheel_view_ratio=self._wheel_frames / self._wheel_checked if self._wheel_checked else None,
        )
