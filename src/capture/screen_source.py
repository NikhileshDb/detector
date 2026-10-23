import time

import cv2
import mss
import numpy as np


class ScreenSource:
    """Captures the screen directly, so no OBS virtual camera is needed.

    Grabs a monitor, or a region of it, at up to ``max_fps``. Frames come
    back as BGR like ``CameraSource``, so ROIs and detectors work unchanged.
    """

    def __init__(self, monitor: int = 1, region: dict | None = None, max_fps: float = 60.0, grabber_factory=mss.mss):
        self.monitor = monitor
        self.region = region
        self.max_fps = max_fps
        self._grabber_factory = grabber_factory
        self._grabber = None
        self._area = None
        self._last_grab = 0.0

    def start(self) -> None:
        with self._grabber_factory() as grabber:
            monitors = grabber.monitors
            if not 0 <= self.monitor < len(monitors):
                raise RuntimeError(f"Unable to open monitor {self.monitor}; found {len(monitors) - 1}")
            self._area = dict(self.region) if self.region else dict(monitors[self.monitor])
        print(f"Screen capture: {self._area['width']}x{self._area['height']} " f"from monitor {self.monitor} (max {self.max_fps:.0f} FPS)")

    def read(self):
        if self._area is None:
            raise RuntimeError("ScreenSource has not been started.")
        # mss handles are tied to the thread that created them, and reads
        # happen on the capture thread, so the grabber is created here.
        if self._grabber is None:
            self._grabber = self._grabber_factory()
        wait = 1 / self.max_fps - (time.perf_counter() - self._last_grab)
        if wait > 0:
            time.sleep(wait)
        self._last_grab = time.perf_counter()
        shot = self._grabber.grab(self._area)
        return cv2.cvtColor(np.asarray(shot), cv2.COLOR_BGRA2BGR)

    def stop(self) -> None:
        if self._grabber is not None:
            self._grabber.close()
            self._grabber = None
        self._area = None
