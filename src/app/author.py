import os
import uuid
from datetime import datetime, timedelta
from typing import Annotated

from dotenv import load_dotenv
from email_validator import EmailNotValidError, validate_email
from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from src.app.hash_password import bcrypt_context, hash_password
from src.app.specification import (
    EmailSpecification,
    IDSpecification,
    UsernameSpecification,
)
from src.app.uuid7 import uuid7
from src.app.exceptions import UnAuthorizedError
from src.app.schemas import UTC_6, AuthorCreateDTO, AuthorDTO, AuthorOutDTO
from src.infrastructure.database.repo import AuthorRepo

load_dotenv()

JWT_EXPIRES = timedelta(minutes=60)
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="authors/login")


async def _get_author(repo: AuthorRepo, user_id: uuid.UUID) -> AuthorOutDTO:
    user = await repo.get_author(IDSpecification(user_id))
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="USER DOES NOT EXIST")

    return AuthorOutDTO.model_validate(user)


async def _create_author(repo: AuthorRepo, user: AuthorCreateDTO) -> AuthorOutDTO:
    if await repo.is_author_exists(user):
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail="USERNAME OR EMAIL ALREADY TAKEN"
        )

    new_user = AuthorDTO(
        id=uuid7(), hashed_password=hash_password(user.password), **user.model_dump()
    )
    res = await repo.create_author(new_user)
    return AuthorOutDTO.model_validate(res)


async def check_login(login: str, repo: AuthorRepo) -> AuthorDTO | None:
    try:
        validate_email(login)
    except EmailNotValidError:
        user = await repo.get_author(UsernameSpecification(login))
    else:
        user = await repo.get_author(EmailSpecification(login))
    if user is not None:
        return AuthorDTO.model_validate(user)


def create_access_token(username: str, author_id: uuid.UUID, expires: timedelta) -> str:
    return jwt.encode(
        {
            "username": username,
            "exp": datetime.now(tz=UTC_6) + expires,
            "id": str(author_id),
        },
        SECRET_KEY,
        ALGORITHM,
    )


async def authenticate_author(
    login: str, repo: AuthorRepo, password: str
) -> str:
    author = await check_login(login, repo)
    if author is not None and bcrypt_context.verify(password, author.hashed_password):
        return create_access_token(author.username, author.id, JWT_EXPIRES)

    raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="BAD CREDENTIALS")


async def get_current_author(token: Annotated[str, Depends(oauth2_bearer)]) -> uuid.UUID:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        author_id = payload.get("id")
        exp = payload.get("exp")
        if (
            username is None
            or author_id is None
            or datetime.now(tz=UTC_6) > datetime.fromtimestamp(timestamp=exp, tz=UTC_6)
        ):
            raise JWTError()
        return author_id
    except JWTError:
        raise UnAuthorizedError()