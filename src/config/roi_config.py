import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Roi:
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class DetectorRoiConfig:
    countdown: Roi
    result: Roi
    number: Roi
    wheel: Roi | None = None


def _roi_from_dict(data: dict) -> Roi:
    return Roi(
        x=int(data["x"]),
        y=int(data["y"]),
        width=int(data["width"]),
        height=int(data["height"]),
    )


def save_roi_config(
    config: DetectorRoiConfig,
    path: str = "roi_config.json",
) -> None:
    Path(path).write_text(
        json.dumps(
            asdict(config),
            indent=2,
        ),
        encoding="utf-8",
    )


def load_roi_config(
    path: str = "roi_config.json",
) -> DetectorRoiConfig:

    data = json.loads(
        Path(path).read_text(
            encoding="utf-8"
        )
    )

    required_keys = {
        "countdown",
        "result",
        "number",
    }

    if not required_keys.issubset(data):
        raise ValueError(
            "Old or invalid ROI configuration detected. "
            "Delete roi_config.json and press R "
            "to configure countdown, result, and number ROIs."
        )

    return DetectorRoiConfig(
        countdown=_roi_from_dict(
            data["countdown"]
        ),
        result=_roi_from_dict(
            data["result"]
        ),
        number=_roi_from_dict(
            data["number"]
        ),
        wheel=(
            _roi_from_dict(data["wheel"])
            if data.get("wheel")
            else None
        ),
    )
