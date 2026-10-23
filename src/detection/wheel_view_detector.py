import cv2


class WheelViewDetector:
    """Tells the wheel close-up apart from the dealer/table camera.

    Compares colour histograms rather than pixels, so the spinning rotor
    and moving ball do not count as a view change.
    """

    def __init__(self, reference_frame, similarity_threshold: float = 0.80):
        self.similarity_threshold = similarity_threshold
        self.reference = self._histogram(reference_frame)

    def similarity(self, frame) -> float:
        return float(cv2.compareHist(self.reference, self._histogram(frame), cv2.HISTCMP_CORREL))

    def is_wheel_view(self, frame) -> bool:
        return self.similarity(frame) >= self.similarity_threshold

    @staticmethod
    def _histogram(frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        histogram = cv2.calcHist([hsv], [0, 1], None, [30, 32], [0, 180, 0, 256])
        cv2.normalize(histogram, histogram)
        return histogram
