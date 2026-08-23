from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self._connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:

        await websocket.accept()

        self._connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:

        if websocket in self._connections:
            self._connections.remove(websocket)

    async def broadcast(self, message: str) -> None:

        dead: list[WebSocket] = []

        for connection in self._connections:

            try:
                await connection.send_text(message)

            except Exception:
                dead.append(connection)

        for connection in dead:
            self.disconnect(connection)
