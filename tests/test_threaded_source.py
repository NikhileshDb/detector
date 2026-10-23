import time

import numpy as np

from capture.threaded_source import ThreadedFrameSource


class FakeSource:
    def __init__(self, count):
        self.count = count
        self.started = False
        self.stopped = False
        self._read = 0

    def start(self):
        self.started = True

    def read(self):
        if self._read >= self.count:
            return None
        self._read += 1
        return np.full((36, 64, 3), self._read % 256, dtype=np.uint8)

    def stop(self):
        self.stopped = True


def _wait_for(source, index, timeout=2.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        latest = source.latest()
        if latest is not None and latest.index >= index:
            return latest
        time.sleep(0.005)
    raise AssertionError("frames not captured in time")


def test_buffers_timestamped_frames_in_order():
    fake = FakeSource(count=10)
    source = ThreadedFrameSource(fake, buffer_size=5)
    source.start()
    try:
        latest = _wait_for(source, 10)
        frames = source.frames_since(0)
    finally:
        source.stop()

    assert fake.started and fake.stopped
    assert latest.index == 10
    assert [f.index for f in frames] == [6, 7, 8, 9, 10]
    assert all(a.timestamp <= b.timestamp for a, b in zip(frames, frames[1:]))


def test_frames_since_returns_only_newer_frames():
    source = ThreadedFrameSource(FakeSource(count=4))
    source.start()
    try:
        _wait_for(source, 4)
        assert [f.index for f in source.frames_since(2)] == [3, 4]
    finally:
        source.stop()
