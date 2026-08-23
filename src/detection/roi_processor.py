import numpy as np

from config.roi_config import Roi


class RoiProcessor:
    @staticmethod
    def crop(
        frame: np.ndarray,
        roi: Roi,
    ) -> np.ndarray:

        return frame[
            roi.y:roi.y + roi.height,
            roi.x:roi.x + roi.width
        ]
