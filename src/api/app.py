from fastapi import FastAPI

from api.routers import dashboard, history, spins
from storage.correction_service import CorrectionService
from storage.database import Database
from storage.manual_result_service import ManualResultService
from storage.round_repository import RoundRepository
from storage.spin_repository import SpinRepository


def create_app(
    database: Database,
    round_repository: RoundRepository,
    spin_repository: SpinRepository,
) -> FastAPI:

    app = FastAPI(title="Roulette Analytics API")

    app.state.database = database
    app.state.round_repository = round_repository
    app.state.spin_repository = spin_repository

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
    app.include_router(spins.router)
    app.include_router(dashboard.router)

    return app
