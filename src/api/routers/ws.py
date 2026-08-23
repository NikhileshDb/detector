from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from api.websocket_manager import ConnectionManager


router = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:

    manager: ConnectionManager = websocket.app.state.connection_manager

    await manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(websocket)
