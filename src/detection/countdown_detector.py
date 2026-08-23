from detection.result_state_detector import (
    ResultStateDetector,
)


class CountdownDetector:
    def __init__(
        self,
        baseline_frame,
    ):
        self._detector = (
            ResultStateDetector(
                baseline_frame,
                difference_threshold=25.0,
                changed_pixel_ratio_threshold=0.15,
            )
        )

    def is_visible(
        self,
        frame,
    ) -> bool:

        return (
            self._detector
            .is_result_visible(frame)
        )
