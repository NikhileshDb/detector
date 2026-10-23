import json

from config.roi_config import DetectorRoiConfig, Roi, load_roi_config, save_roi_config


def test_config_without_wheel_still_loads(tmp_path):
    path = tmp_path / "roi.json"
    roi = {"x": 1, "y": 2, "width": 3, "height": 4}
    path.write_text(json.dumps({"countdown": roi, "result": roi, "number": roi}))

    assert load_roi_config(str(path)).wheel is None


def test_wheel_roi_round_trips(tmp_path):
    path = tmp_path / "roi.json"
    roi = Roi(1, 2, 3, 4)
    config = DetectorRoiConfig(countdown=roi, result=roi, number=roi, wheel=Roi(10, 20, 300, 300))

    save_roi_config(config, str(path))

    assert load_roi_config(str(path)) == config


def test_rotor_roi_round_trips(tmp_path):
    path = tmp_path / "roi.json"
    roi = Roi(1, 2, 3, 4)
    config = DetectorRoiConfig(countdown=roi, result=roi, number=roi, rotor=Roi(610, 245, 690, 580))

    save_roi_config(config, str(path))

    assert load_roi_config(str(path)).rotor == Roi(610, 245, 690, 580)
