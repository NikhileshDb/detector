import cv2


class CameraSource:
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self._capture: cv2.VideoCapture | None = None

    def start(self) -> None:
        self._capture = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not self._capture.isOpened():
            raise RuntimeError(
                f"Unable to open camera index {self.camera_index}")
        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self._capture.set(cv2.CAP_PROP_FPS, 60)

        width = self._capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fps = self._capture.get(cv2.CAP_PROP_FPS)

        print(f"Capture: {width}x{height} @ {fps} FPS")

    def read(self):
        if self._capture is None:
            raise RuntimeError(f"CameraSource has not been started.")
        success, frame = self._capture.read()

        if not success:
            return None

        return frame

    def stop(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None
