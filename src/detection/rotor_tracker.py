from collections import deque
from dataclasses import dataclass
from math import atan2, pi, tau

import cv2
import numpy as np

from config.roi_config import Roi

POCKETS = 37
POCKET_ANGLE = tau / POCKETS


@dataclass(frozen=True)
class RotorState:
    timestamp: float
    zero_angle: float
    rev_per_second: float
    residual_pockets: float
    samples: int

    def pocket_at(self, reference_angle: float = -pi / 2) -> int:
        """Wheel-order index of the pocket under ``reference_angle``.

        Angles are screen angles on the rotor ellipse (y down, so they grow
        clockwise). Wheel order runs anticlockwise on screen from zero.
        """
        return round((self.zero_angle - reference_angle) / POCKET_ANGLE) % POCKETS


class RotorTracker:
    """Follows the green zero pocket around the number ring.

    ``ring`` is a box drawn tightly around the ring of numbers; its centre
    and half-sizes give the ellipse the rotor appears as on screen.
    """

    def __init__(self, ring: Roi, window_seconds: float = 2.0, min_samples: int = 8, min_zero_pixels: int = 150):
        self.cx = ring.x + ring.width / 2
        self.cy = ring.y + ring.height / 2
        self.ax = ring.width / 2
        self.ay = ring.height / 2
        self.window_seconds = window_seconds
        self.min_samples = min_samples
        self.min_zero_pixels = min_zero_pixels
        self._history: deque[tuple[float, float]] = deque()
        self._mask = None

    def observe(self, frame, timestamp: float) -> float | None:
        angle = self.zero_angle(frame)
        if angle is None:
            return None
        if self._history and timestamp - self._history[-1][0] > 1.0:
            self._history.clear()
        if self._history:
            previous = self._history[-1][1]
            angle = previous + (angle - previous + pi) % tau - pi
        self._history.append((timestamp, angle))
        while self._history and timestamp - self._history[0][0] > self.window_seconds:
            self._history.popleft()
        return angle

    def zero_angle(self, frame) -> float | None:
        x0, y0, x1, y1 = self._bounds(frame.shape[:2])
        hsv = cv2.cvtColor(frame[y0:y1, x0:x1], cv2.COLOR_BGR2HSV)
        green = cv2.inRange(hsv, (45, 80, 60), (85, 255, 255)) & self._ring_mask(frame.shape[:2])
        count, _, stats, centroids = cv2.connectedComponentsWithStats(green)
        if count < 2:
            return None
        best = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        if stats[best, cv2.CC_STAT_AREA] < self.min_zero_pixels:
            return None
        x, y = centroids[best]
        return atan2((y + y0 - self.cy) / self.ay, (x + x0 - self.cx) / self.ax)

    @property
    def sightings(self) -> int:
        return len(self._history)

    def state(self) -> RotorState | None:
        if len(self._history) < self.min_samples:
            return None
        times = np.array([t for t, _ in self._history])
        angles = np.array([a for _, a in self._history])
        slope, intercept = np.polyfit(times - times[-1], angles, 1)
        residual = float(np.std(angles - (slope * (times - times[-1]) + intercept)))
        return RotorState(
            timestamp=float(times[-1]),
            zero_angle=float(intercept % tau),
            rev_per_second=float(slope / tau),
            residual_pockets=residual / POCKET_ANGLE,
            samples=len(times),
        )

    def _bounds(self, shape) -> tuple[int, int, int, int]:
        height, width = shape
        return (
            max(0, int(self.cx - 1.05 * self.ax)),
            max(0, int(self.cy - 1.05 * self.ay)),
            min(width, int(self.cx + 1.05 * self.ax) + 1),
            min(height, int(self.cy + 1.05 * self.ay) + 1),
        )

    def _ring_mask(self, shape):
        x0, y0, x1, y1 = self._bounds(shape)
        if self._mask is None or self._mask.shape != (y1 - y0, x1 - x0):
            yy, xx = np.mgrid[y0:y1, x0:x1]
            r = np.sqrt(((xx - self.cx) / self.ax) ** 2 + ((yy - self.cy) / self.ay) ** 2)
            self._mask = ((r > 0.82) & (r < 1.05)).astype(np.uint8) * 255
        return self._mask
