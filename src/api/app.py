import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routers import dashboard, history, section_analytics, sessions, spins, wheel_analytics, ws
from api.websocket_manager import ConnectionManager
from events.event_publisher import EventPublisher
from storage.correction_service import CorrectionService
from storage.database import Database
from storage.manual_result_service import ManualResultService
from storage.round_repository import RoundRepository
from storage.spin_repository import SpinRepository
from storage.session_repository import SessionRepository


def create_app(
    database: Database,
    round_repository: RoundRepository,
    spin_repository: SpinRepository,
    connection_manager: ConnectionManager | None = None,
    event_publisher: EventPublisher | None = None,
) -> FastAPI:

    connection_manager = connection_manager or ConnectionManager()

    event_publisher = event_publisher or EventPublisher(connection_manager)

    @asynccontextmanager
    async def lifespan(app: FastAPI):

        event_publisher.bind_loop(asyncio.get_running_loop())

        yield

    app = FastAPI(title="Roulette Analytics API", lifespan=lifespan)

    app.state.database = database
    app.state.round_repository = round_repository
    app.state.spin_repository = spin_repository
    app.state.session_repository = SessionRepository(database)
    app.state.connection_manager = connection_manager
    app.state.event_publisher = event_publisher

    app.state.manual_result_service = ManualResultService(
        database=database,
        round_repository=round_repository,
        spin_repository=spin_repository,
    )

    app.state.correction_service = CorrectionService(
        database=database,
        round_repository=round_repository,
        spin_repository=spin_repository,
    )

    app.include_router(history.router)
    app.include_router(sessions.router)
    app.include_router(section_analytics.router)
    app.include_router(wheel_analytics.router)
    app.include_router(spins.router)
    app.include_router(dashboard.router)
    app.include_router(ws.router)

    return app
