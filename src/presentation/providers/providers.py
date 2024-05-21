from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.factory import get_async_session
from src.infrastructure.s3.factory import S3Singleton, get_s3, exist_bucket
from src.presentation.providers.stub import Stub


def setup_providers(app: FastAPI) -> None:
    app.dependency_overrides[Stub(AsyncSession)] = get_async_session
    app.dependency_overrides[Stub(S3Singleton)] = get_s3
    exist_bucket()
