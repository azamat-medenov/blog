import pathlib
import uuid
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.post import _create_category, _get_posts_by_category, create_post_fully, _get_post, _get_media, \
    _get_posts_by_tag
from src.app.schemas import CreatePostDTO, TagDTO, CategoryDTO, PostOutDTO
from src.app.author import get_current_author
from src.infrastructure.database.repo import CategoryRepo, PostRepo, MediaRepo
from src.presentation.providers.stub import Stub
from src.app.post import s3_put_files

post_router = APIRouter(
    prefix="/posts",
    tags=['posts']
)


@post_router.get("/media/{id}")
async def get_media(
        id: uuid.UUID,
        db_session: Annotated[AsyncSession, Depends(Stub(AsyncSession))]):
    return await _get_media(id, MediaRepo(db_session))


@post_router.get("", status_code=200)
async def get_post(
        post_id: uuid.UUID,
        db_session: Annotated[AsyncSession, Depends(Stub(AsyncSession))]
) -> PostOutDTO:
    return await _get_post(PostRepo(db_session), post_id)


@post_router.post("", status_code=201)
async def create_post(
        post: CreatePostDTO,
        author_id: Annotated[uuid.UUID, Depends(get_current_author)],
        db_session: Annotated[AsyncSession, Depends(Stub(AsyncSession))],
        media: list[UploadFile],
        tags: list[str] = Query(None)
):
    return await create_post_fully(
        post, author_id, db_session, media, tags
    )


@post_router.post("/category", status_code=201)
async def create_category(
        category: CategoryDTO,
        db_session: Annotated[AsyncSession, Depends(Stub(AsyncSession))]
):
    await _create_category(CategoryRepo(db_session), category)
    return {"status": 201}


@post_router.get("/{category_id}", status_code=200)
async def get_posts_by_category(
        category_id: int,
        db_session: Annotated[AsyncSession, Depends(Stub(AsyncSession))]
):
    return await _get_posts_by_category(
        PostRepo(db_session),
        category_id
    )


@post_router.get("/tag/{tag_name}", status_code=200)
async def get_posts_by_tag(
        tag_name: str,
        db_session: Annotated[AsyncSession, Depends(Stub(AsyncSession))]
):
    return await _get_posts_by_tag(
        PostRepo(db_session),
        tag_name
    )
