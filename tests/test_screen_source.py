import threading
import time

import numpy as np
import pytest

from capture.screen_source import ScreenSource
from capture.threaded_source import ThreadedFrameSource


class FakeGrabber:
    instances = []

    def __init__(self):
        self.monitors = [
            {"left": 0, "top": 0, "width": 200, "height": 100},
            {"left": 0, "top": 0, "width": 200, "height": 100},
        ]
        self.grabbed = []
        self.closed = False
        self.thread = threading.current_thread()
        FakeGrabber.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def grab(self, area):
        self.grabbed.append(area)
        frame = np.zeros((area["height"], area["width"], 4), dtype=np.uint8)
        frame[..., 0] = 10
        frame[..., 2] = 200
        frame[..., 3] = 255
        return frame

    def close(self):
        self.closed = True


@pytest.fixture(autouse=True)
def _reset_instances():
    FakeGrabber.instances = []


def test_returns_bgr_frames_of_the_region():
    source = ScreenSource(region={"left": 5, "top": 5, "width": 40, "height": 30}, grabber_factory=FakeGrabber)
    source.start()
    frame = source.read()
    source.stop()

    assert frame.shape == (30, 40, 3)
    assert tuple(frame[0, 0]) == (10, 0, 200)
    assert FakeGrabber.instances[-1].grabbed == [{"left": 5, "top": 5, "width": 40, "height": 30}]
    assert FakeGrabber.instances[-1].closed


def test_defaults_to_whole_monitor():
    source = ScreenSource(monitor=1, grabber_factory=FakeGrabber)
    source.start()

    assert source.read().shape == (100, 200, 3)


def test_rejects_missing_monitor():
    with pytest.raises(RuntimeError):
        ScreenSource(monitor=3, grabber_factory=FakeGrabber).start()


def test_read_before_start_fails():
    with pytest.raises(RuntimeError):
        ScreenSource(grabber_factory=FakeGrabber).read()


def test_grabber_is_created_on_the_capture_thread():
    source = ThreadedFrameSource(ScreenSource(max_fps=200, grabber_factory=FakeGrabber))
    source.start()
    try:
        deadline = time.monotonic() + 2
        while source.latest() is None and time.monotonic() < deadline:
            time.sleep(0.005)
        assert source.latest() is not None
    finally:
        source.stop()

    reader = FakeGrabber.instances[-1]
    assert reader.thread.name == "frame-capture"
    assert reader.closed
