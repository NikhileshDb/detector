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
