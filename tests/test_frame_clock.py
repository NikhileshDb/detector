import numpy as np

from capture.frame_clock import FrameClock


def _frame(value):
    return np.full((72, 128, 3), value, dtype=np.uint8)


def test_repeated_frames_are_marked_duplicate():
    clock = FrameClock()

    first = clock.stamp(_frame(10), 0.0)
    repeat = clock.stamp(_frame(10), 1 / 60)
    changed = clock.stamp(_frame(200), 2 / 60)

    assert not first.is_duplicate
    assert repeat.is_duplicate
    assert not changed.is_duplicate
    assert [first.index, repeat.index, changed.index] == [1, 2, 3]


def test_stream_fps_counts_only_changed_frames():
    clock = FrameClock()

    # 60 fps capture of a 30 fps stream: every frame is shown twice.
    for i in range(121):
        clock.stamp(_frame((i // 2) * 2 % 256), i / 60)

    assert abs(clock.capture_fps - 60) < 1
    assert abs(clock.stream_fps - 30) < 1.5


def test_rates_are_zero_before_two_frames():
    clock = FrameClock()
    clock.stamp(_frame(0), 0.0)

    assert clock.stream_fps == 0.0
    assert clock.capture_fps == 0.0


def test_small_motion_counts_as_a_new_frame():
    # A slowly turning rotor changes only a thin ring of pixels between
    # frames; that must not be mistaken for a repeated frame.
    clock = FrameClock()
    first = np.zeros((1080, 1920, 3), dtype=np.uint8)
    moved = first.copy()
    moved[500:540, 900:940] = 40

    clock.stamp(first, 0.0)

    assert not clock.stamp(moved, 1 / 30).is_duplicate
