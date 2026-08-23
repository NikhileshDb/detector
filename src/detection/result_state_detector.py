import cv2
import numpy as np


class ResultStateDetector:
    def __init__(self, reference_frame, difference_threshold: float = 25.0, changed_pixel_ratio_threshold: float = 0.20):
        self.difference_threshold = difference_threshold
        self.changed_pixel_ratio_threshold = changed_pixel_ratio_threshold
        self.reference = self._prepare(reference_frame)

    def _prepare(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        return gray

    def is_result_visible(self, frame) -> bool:
        current = self._prepare(frame)

        if current.shape != self.reference.shape:
            return False

        difference = cv2.absdiff(
            self.reference,
            current,
        )

        _, thresholded = cv2.threshold(
            difference,
            self.difference_threshold,
            255,
            cv2.THRESH_BINARY,
        )

        changed_pixels = cv2.countNonZero(
            thresholded
        )

        total_pixels = (
            thresholded.shape[0]
            * thresholded.shape[1]
        )

        changed_ratio = (
            changed_pixels / total_pixels
        )

        return (
            changed_ratio
            >= self.changed_pixel_ratio_threshold
        )
