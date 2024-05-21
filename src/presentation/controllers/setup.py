from fastapi import FastAPI

from src.presentation.controllers.author import author_router
from src.presentation.controllers.post import post_router


def setup_controllers(app: FastAPI) -> None:
    app.include_router(author_router)
    app.include_router(post_router)