from pathlib import Path

import cv2


def save_reference(
    frame,
    path: str,
) -> None:

    target = Path(path)

    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    success = cv2.imwrite(
        str(target),
        frame,
    )

    if not success:
        raise RuntimeError(
            f"Failed saving reference: {path}"
        )


def load_reference(
    path: str,
):

    target = Path(path)

    if not target.exists():
        return None

    return cv2.imread(
        str(target)
    )
