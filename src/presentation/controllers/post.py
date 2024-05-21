import pathlib
import uuid
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.post import _create_category, _get_posts_by_category, create_post_fully
from src.app.schemas import CreatePostDTO, TagDTO, CategoryDTO
from src.app.author import get_current_author
from src.infrastructure.database.repo import CategoryRepo, PostRepo
from src.infrastructure.s3.factory import S3Singleton
from src.presentation.providers.stub import Stub
from src.app.post import s3_put_files

post_router = APIRouter(
    prefix="/posts",
    tags=['posts']
)


@post_router.post("", status_code=201)
async def create_post(
        post: CreatePostDTO,
        author_id: Annotated[uuid.UUID, Depends(get_current_author)],
        db_session: Annotated[AsyncSession, Depends(Stub(AsyncSession))],
        s3: Annotated[S3Singleton, Depends(Stub(S3Singleton))],
        media: list[UploadFile],
        tags: list[str] = Query(None)
):
    return await create_post_fully(
        post, author_id, db_session, s3, media, tags
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
