from config.roi_config import (
    DetectorRoiConfig,
    save_roi_config,
)
from detection.roi_selector import select_roi


def configure_rois(
    frame,
    output_path: str = "roi_config.json",
) -> DetectorRoiConfig | None:

    print()
    print("Select COUNTDOWN region.")

    countdown = select_roi(
        frame,
        "Select COUNTDOWN ROI",
    )

    if countdown is None:
        return None

    print("Select RESULT PANEL region.")

    result = select_roi(
        frame,
        "Select RESULT ROI",
    )

    if result is None:
        return None

    print("Select WINNING NUMBER only.")

    number = select_roi(
        frame,
        "Select NUMBER ROI",
    )

    if number is None:
        return None

    config = DetectorRoiConfig(
        countdown=countdown,
        result=result,
        number=number,
    )

    save_roi_config(
        config,
        output_path,
    )

    print()
    print("ROI configuration saved.")

    return config
