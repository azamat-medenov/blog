import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.schemas import Token
from src.app.schemas import AuthorCreateDTO, AuthorOutDTO
from src.app.author import _create_author, _get_author, authenticate_author
from src.infrastructure.database.repo import AuthorRepo
from src.presentation.providers.stub import Stub

author_router = APIRouter(prefix="/authors", tags=["authors"])


@author_router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
        user: AuthorCreateDTO, session: Annotated[AsyncSession, Depends(Stub(AsyncSession))]
) -> AuthorOutDTO:
    return await _create_author(AuthorRepo(session), user)


@author_router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: Annotated[AsyncSession, Depends(Stub(AsyncSession))],
) -> dict[str, str]:
    token = await authenticate_author(
        form_data.username, AuthorRepo(session), form_data.password
    )
    return {"token_type": "bearer", "access_token": token}
