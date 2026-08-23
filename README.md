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
