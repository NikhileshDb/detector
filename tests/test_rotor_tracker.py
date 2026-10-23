from math import cos, pi, sin, tau

import cv2
import numpy as np
import pytest

from config.roi_config import Roi
from detection.rotor_tracker import POCKET_ANGLE, RotorState, RotorTracker

RING = Roi(x=200, y=100, width=400, height=300)


def _frame(zero_angle):
    frame = np.zeros((500, 800, 3), dtype=np.uint8)
    cx, cy = 400, 250
    x = int(cx + 0.93 * 200 * cos(zero_angle))
    y = int(cy + 0.93 * 150 * sin(zero_angle))
    cv2.circle(frame, (x, y), 9, (0, 160, 0), -1)
    return frame


def test_finds_zero_angle():
    tracker = RotorTracker(RING)

    assert tracker.zero_angle(_frame(0.5)) == pytest.approx(0.5, abs=0.03)


def test_no_zero_visible_returns_none():
    tracker = RotorTracker(RING)

    assert tracker.zero_angle(np.zeros((500, 800, 3), dtype=np.uint8)) is None
    assert tracker.observe(np.zeros((500, 800, 3), dtype=np.uint8), 0.0) is None


def test_measures_speed_across_wraparound():
    tracker = RotorTracker(RING)
    speed = -0.25  # rev/s, anticlockwise on screen
    for i in range(40):
        t = i / 20
        tracker.observe(_frame(3.0 + speed * tau * t), t)

    state = tracker.state()

    assert state.rev_per_second == pytest.approx(speed, abs=0.01)
    assert state.residual_pockets < 0.5
    assert state.zero_angle == pytest.approx((3.0 + speed * tau * 1.95) % tau, abs=0.05)


def test_needs_enough_samples():
    tracker = RotorTracker(RING, min_samples=8)
    for i in range(3):
        tracker.observe(_frame(0.1 * i), i / 20)

    assert tracker.state() is None


def test_gap_resets_history():
    tracker = RotorTracker(RING, min_samples=2)
    for i in range(5):
        tracker.observe(_frame(0.1 * i), i / 20)
    tracker.observe(_frame(2.0), 5.0)

    assert tracker.state() is None


def test_pocket_at_top():
    def state(zero_angle):
        return RotorState(timestamp=0.0, zero_angle=zero_angle, rev_per_second=0.2, residual_pockets=0.1, samples=10)

    # Zero itself at the top.
    assert state(-pi / 2).pocket_at() == 0
    # Zero one pocket clockwise of the top: the pocket anticlockwise of
    # zero in wheel order (26) is at the top.
    assert state(-pi / 2 + POCKET_ANGLE).pocket_at() == 1
    assert state(-pi / 2 - POCKET_ANGLE).pocket_at() == 36
