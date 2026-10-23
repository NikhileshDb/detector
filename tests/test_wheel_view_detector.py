import cv2
import numpy as np

from detection.wheel_view_detector import WheelViewDetector


def _wheel(angle):
    frame = np.zeros((200, 200, 3), dtype=np.uint8)
    frame[:] = (20, 90, 20)
    for i in range(37):
        theta = np.deg2rad(angle + i * 360 / 37)
        colour = (0, 0, 200) if i % 2 else (30, 30, 30)
        end = (int(100 + 90 * np.cos(theta)), int(100 + 90 * np.sin(theta)))
        cv2.line(frame, (100, 100), end, colour, 6)
    return frame


def test_rotated_wheel_still_matches_reference():
    detector = WheelViewDetector(_wheel(0))

    assert detector.is_wheel_view(_wheel(47))


def test_different_scene_does_not_match():
    detector = WheelViewDetector(_wheel(0))
    dealer_view = np.full((200, 200, 3), (180, 160, 140), dtype=np.uint8)

    assert not detector.is_wheel_view(dealer_view)
