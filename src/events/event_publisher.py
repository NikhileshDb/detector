import asyncio

from api.websocket_manager import ConnectionManager
from events.event_types import DetectorEvent, serialize_event


class EventPublisher:
    """Bridges the synchronous detector loop (main thread) into the async
    WebSocket broadcast (running on the API thread's event loop). publish()
    is safe to call from any thread once bind_loop() has run."""

    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self._loop: asyncio.AbstractEventLoop | None = None

    def bind_loop(self, loop: asyncio.AbstractEventLoop) -> None:

        self._loop = loop

    def publish(self, event: DetectorEvent) -> None:

        if self._loop is None:
            return

        message = serialize_event(event)

        asyncio.run_coroutine_threadsafe(
            self.connection_manager.broadcast(message),
            self._loop,
        )
