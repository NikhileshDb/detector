import asyncio
import json
import threading
import time

from api.websocket_manager import ConnectionManager
from events.event_publisher import EventPublisher
from events.event_types import RoundStartedEvent, SpinConfirmedEvent, serialize_event


class FakeWebSocket:
    def __init__(self):
        self.sent = []

    async def send_text(self, message):
        self.sent.append(message)


def test_serialize_event_format():

    event = SpinConfirmedEvent(
        round_id=1,
        number="17",
        color="BLACK",
        confidence=0.9,
    )

    payload = json.loads(serialize_event(event))

    assert payload["type"] == "spin_confirmed"
    assert payload["data"]["number"] == "17"


def test_publish_before_bind_loop_is_noop():

    manager = ConnectionManager()
    publisher = EventPublisher(manager)

    publisher.publish(RoundStartedEvent(round_id=1))


def test_publish_delivers_from_another_thread():

    manager = ConnectionManager()
    fake_socket = FakeWebSocket()
    publisher = EventPublisher(manager)

    async def run_loop():

        manager._connections.append(fake_socket)

        publisher.bind_loop(asyncio.get_running_loop())

        await asyncio.sleep(0.5)

    def publish_from_other_thread():

        time.sleep(0.1)

        publisher.publish(RoundStartedEvent(round_id=7))

    thread = threading.Thread(target=publish_from_other_thread)
    thread.start()

    asyncio.run(run_loop())

    thread.join()

    assert len(fake_socket.sent) == 1
    assert json.loads(fake_socket.sent[0])["type"] == "round_started"
    assert json.loads(fake_socket.sent[0])["data"]["round_id"] == 7
