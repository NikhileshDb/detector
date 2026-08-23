import uvicorn

from api.app import create_app
from storage.database import Database
from storage.round_repository import RoundRepository
from storage.spin_repository import SpinRepository


database = Database()
database.initialize()

app = create_app(
    database=database,
    round_repository=RoundRepository(database),
    spin_repository=SpinRepository(database),
)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
