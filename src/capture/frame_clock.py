from collections import deque
from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class TimedFrame:
    index: int
    timestamp: float
    frame: np.ndarray
    is_duplicate: bool


class FrameClock:
    """Stamps frames and measures the real stream rate.

    OBS repeats the last browser frame when the stream is slower than the
    capture rate, so the capture FPS overstates how often the picture
    actually changes. Only frames that differ from the previous one count
    towards the stream FPS.
    """

    def __init__(self, duplicate_threshold: float = 0.5, window_seconds: float = 2.0):
        self.duplicate_threshold = duplicate_threshold
        self.window_seconds = window_seconds
        self._index = 0
        self._previous = None
        self._unique_times: deque[float] = deque()
        self._all_times: deque[float] = deque()

    def stamp(self, frame, timestamp: float) -> TimedFrame:
        thumbnail = self._thumbnail(frame)
        is_duplicate = (
            self._previous is not None
            and thumbnail.shape == self._previous.shape
            and float(np.mean(cv2.absdiff(thumbnail, self._previous))) < self.duplicate_threshold
        )
        self._previous = thumbnail
        self._all_times.append(timestamp)
        if not is_duplicate:
            self._unique_times.append(timestamp)
        self._trim(timestamp)
        self._index += 1
        return TimedFrame(self._index, timestamp, frame, is_duplicate)

    @property
    def stream_fps(self) -> float:
        return self._rate(self._unique_times)

    @property
    def capture_fps(self) -> float:
        return self._rate(self._all_times)

    def _rate(self, times: deque[float]) -> float:
        if len(times) < 2: return 0.0
        span = times[-1] - times[0]
        return (len(times) - 1) / span if span > 0 else 0.0

    def _trim(self, now: float) -> None:
        for times in (self._unique_times, self._all_times):
            while times and now - times[0] > self.window_seconds:
                times.popleft()

    @staticmethod
    def _thumbnail(frame):
        gray = frame if frame.ndim == 2 else cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.resize(gray, (64, 36), interpolation=cv2.INTER_AREA)
