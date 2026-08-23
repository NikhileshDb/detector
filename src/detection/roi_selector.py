import cv2

from config.roi_config import Roi


def select_roi(
    frame,
    window_name: str,
) -> Roi | None:

    selection = cv2.selectROI(
        window_name,
        frame,
        showCrosshair=True,
        fromCenter=False,
    )

    cv2.destroyWindow(window_name)

    x, y, width, height = map(
        int,
        selection,
    )

    if width <= 0 or height <= 0:
        return None

    return Roi(
        x=x,
        y=y,
        width=width,
        height=height,
    )
