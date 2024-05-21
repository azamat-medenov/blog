import uvicorn
from fastapi import FastAPI

from src.presentation.controllers.setup import setup_controllers
from src.presentation.providers.providers import setup_providers


def main() -> FastAPI:
    app = FastAPI()
    setup_controllers(app)
    setup_providers(app)
    return app


def run() -> None:
    uvicorn.run(r"main:main", reload=True, port=5000)


if __name__ == "__main__":
    run()
