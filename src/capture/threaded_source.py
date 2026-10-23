import threading
import time
from collections import deque

from capture.frame_clock import FrameClock, TimedFrame


class ThreadedFrameSource:
    """Reads frames on a background thread so slow OCR in the main loop
    cannot delay capture or skew frame timestamps.

    Keeps a short ring buffer of timestamped frames for the wheel tracker.
    """

    def __init__(self, source, buffer_size: int = 240, clock: FrameClock | None = None):
        self.source = source
        self.clock = clock or FrameClock()
        self._buffer: deque[TimedFrame] = deque(maxlen=buffer_size)
        self._lock = threading.Lock()
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self.source.start()
        self._running = True
        self._thread = threading.Thread(target=self._run, name="frame-capture", daemon=True)
        self._thread.start()

    def _run(self) -> None:
        try:
            while self._running:
                frame = self.source.read()
                timestamp = time.perf_counter()
                if frame is None:
                    time.sleep(0.001)
                    continue
                with self._lock:
                    self._buffer.append(self.clock.stamp(frame, timestamp))
        finally:
            self.source.stop()

    def latest(self) -> TimedFrame | None:
        with self._lock:
            return self._buffer[-1] if self._buffer else None

    def frames_since(self, index: int) -> list[TimedFrame]:
        with self._lock:
            return [timed for timed in self._buffer if timed.index > index]

    @property
    def stream_fps(self) -> float:
        with self._lock:
            return self.clock.stream_fps

    @property
    def capture_fps(self) -> float:
        with self._lock:
            return self.clock.capture_fps

    def stop(self) -> None:
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=2)
            self._thread = None
