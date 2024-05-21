import asyncio
import pathlib
import uuid

from fastapi import UploadFile
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.infrastructure.database.models import Category, Post, Tag
from src.app.schemas import CategoryDTO, TagDTO, CreatePostDTO, PostDTO
from src.infrastructure.database.repo import CategoryRepo, TagRepo, PostRepo
from src.infrastructure.s3.commands import s3_media_upload
from src.app.specification import NameSpecification

from sqlalchemy.exc import NoResultFound


async def _create_post(
        repo: PostRepo,
        schema: CreatePostDTO,
        author_id: uuid.UUID,
) -> Post:
    try:
        return await repo.create_post(schema, author_id)
    except IntegrityError:
        raise HTTPException(status_code=422, detail="specified category does not exist")


async def add_tag(
        post: Post,
        tag_repo: TagRepo,
        tag_name: str
):
    tag = await tag_repo.get_tag(NameSpecification(name=tag_name))
    if tag is None:
        tag = Tag(name=tag_name)
    post.tags.append(tag)


async def add_tags(post: Post, repo: TagRepo, tags: list[str]):
    tasks = []
    for tag in tags:
        tasks.append(add_tag(post, repo, tag))
    await asyncio.gather(*tasks)


async def _create_category(repo: CategoryRepo, category: CategoryDTO):
    try:
        return await repo.create_category(schema=category)
    except IntegrityError:
        raise HTTPException(status_code=422, detail='category already exists')


async def _get_posts_by_category(repo: PostRepo, category_id: int):
    res = await repo.get_posts_by_category(category_id)
    return [obj[0] for obj in res]


async def s3_put_files(
        bucket: str,
        files: list[UploadFile],
        id: uuid.UUID,
        s3_client
):
    tasks = []
    for file in files:
        ext = pathlib.Path(file.filename).suffix
        tasks.append(s3_media_upload(bucket, file.file, id, ext, s3_client))
    await asyncio.gather(*tasks)


async def create_post_fully(
        post: CreatePostDTO,
        author_id: uuid.UUID,
        db_session: AsyncSession,
        s3,
        media: list[UploadFile],
        tags: list[str]
):
    post = await _create_post(PostRepo(db_session), post, author_id)
    await add_tags(post, TagRepo(db_session), tags)
    await s3_put_files(s3.bucket_name, media, post.id, s3.client)
    await db_session.commit()
    return post.id
