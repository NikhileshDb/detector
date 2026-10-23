# Roulette Analytics Detector

Watches a roulette live-stream feed via OpenCV/EasyOCR, detects round state
transitions and the winning number, and persists rounds/spins to SQLite. A
FastAPI service runs in the same process, exposing history/analytics/live
data over REST and WebSocket for clients such as the Flutter dashboard app.

## Running

```
cd src
../.venv/Scripts/python.exe main.py
```

EasyOCR depends on `opencv-python-headless`, while this application needs
OpenCV's GUI windows for ROI selection. Install the project requirements, then
reinstall the GUI package last so its `cv2` files replace the headless ones:

```
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -m pip uninstall -y opencv-python opencv-python-headless
.venv/Scripts/python.exe -m pip install opencv-python==5.0.0.93
.venv/Scripts/python.exe -c "import cv2; print(cv2.__version__, cv2.currentUIFramework())"
```

This starts both the camera/OCR loop (main thread, with the preview/ROI
windows) and the API server (background thread) in one process.

- API docs: `http://localhost:8000/docs`
- WebSocket stream: `ws://localhost:8000/ws`

## Network / LAN access

The API binds to `0.0.0.0:8000`, so it's reachable from other devices on the
same network (e.g. a phone running the Flutter app) at
`http://<this-machine's-LAN-IP>:8000`.

Find the LAN IP with `ipconfig`. On Windows, the first time `python.exe`
listens on a port while the network is on the Public profile, Windows
Firewall may prompt to allow it — accept for at least the Private/Public
profile matching your network. Confirm from another device with:

```
curl http://<lan-ip>:8000/api/status
```

## Tests

```
.venv/Scripts/python.exe -m pytest
```

## Capture source

By default the detector grabs the screen directly (`CAPTURE_MODE = "screen"`
in `main.py`), so OBS is not needed. Open the live table in the browser on
the primary monitor. For speed, set `SCREEN_REGION` to just the browser
window, e.g. `{"left": 0, "top": 0, "width": 1920, "height": 1080}`, and
redo the ROIs with **R** after changing it. Set `CAPTURE_MODE = "camera"` to
use the OBS Virtual Camera (`CAMERA_INDEX`) instead.

## Capture timing and wheel view

Frames are read on a background thread and timestamped as they arrive, so
slow OCR no longer delays capture. The preview shows two rates:

- **Stream FPS**: how often the picture actually changes. This is the real
  limit for timing the wheel. OBS repeats frames when the browser stream is
  slower than its output rate.
- **Capture FPS**: how often OBS delivers frames.

To detect the wheel close-up:

1. Press **R** and, after the three existing regions, select the **WHEEL**
   region around the rotor (Esc skips it).
2. While the stream shows the wheel close-up, press **W** to save
   `references/wheel_view.png`.

The overlay then shows `View: WHEEL` or `View: OTHER`. Each completed round
saves its stream FPS, duplicate-frame ratio and wheel-view ratio to the
`capture_stats` table, so later analysis can skip spins with poor video.

## Rotor position at bets closed

On the auto wheel the ball is launched after betting closes, so only the
rotor can be measured in time to bet. The detector follows the green zero
pocket and, when the table leaves **BETS CLOSING**, saves the rotor's speed
and the pocket at the top of the screen to `rotor_snapshots`.

1. With the wheel close-up on screen, press **T** and draw a box tightly
   around the ring of numbers on the rotor (the outer edge of the numbers).
2. The overlay draws a green ROTOR box, and each round prints
   `Rotor at bets closed: ...`.

After a few hundred spins, run the offset test from `src`:

```
../.venv/Scripts/python.exe -m analytics.rotor_offset
```

It reports the busiest 5-pocket window of result-vs-rotor offsets for each
rotor direction, with a p-value that accounts for picking the best window.
A p-value above 0.05 means the rotor position does not predict the result.
