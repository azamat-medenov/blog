import asyncio
import pathlib
import uuid

from fastapi import UploadFile
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound

from src.app.uuid7 import uuid7
from src.infrastructure.database.models import Category, Post, Tag, Media
from src.app.schemas import CategoryDTO, TagDTO, CreatePostDTO, PostDTO, PostOutDTO
from src.infrastructure.database.repo import CategoryRepo, TagRepo, PostRepo, MediaRepo
from src.infrastructure.s3.commands import s3_media_upload, s3_get_media
from src.app.specification import NameSpecification


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


async def add_tags(post: Post, repo: TagRepo, tags: list[str] | None):
    tasks = []
    if tags is not None:
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


async def _get_post(repo: PostRepo, post_id: uuid.UUID):
    try:
        post = await repo.get_post(post_id)
        return PostOutDTO(
            id=post.id,
            text=post.text,
            date_created=post.date_created,
            author_id=post.author_id,
            tags=[tag.name for tag in post.tags],
            medias=[m.id for m in post.media],
            category_id=post.category_id
        )
    except NoResultFound:
        raise HTTPException(status_code=404, detail='post not found')


async def s3_put_files(
        files: list[UploadFile],
        db_session: AsyncSession,
        post_id: uuid.UUID
):
    tasks = []
    for file in files:
        ext = pathlib.Path(file.filename).suffix
        media = Media(id=uuid7(), media_type=ext, post_id=post_id)
        db_session.add(media)
        tasks.append(s3_media_upload(file.file, media.id, ext))
    await asyncio.gather(*tasks)


async def create_post_fully(
        post: CreatePostDTO,
        author_id: uuid.UUID,
        db_session: AsyncSession,
        media: list[UploadFile],
        tags: list[str]
):
    post = await _create_post(PostRepo(db_session), post, author_id)
    await add_tags(post, TagRepo(db_session), tags)
    print(f'test 5{media}')
    if media:
        await s3_put_files(media, db_session, post.id)
    await db_session.commit()
    return post.id


async def _get_media(
        media_id: uuid.UUID,
        repo: MediaRepo,
):
    try:
        media = await repo.get_media(media_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="no such media")
    return await s3_get_media(media_id, media.media_type)


async def _get_posts_by_tag(repo: PostRepo, tag: str) -> list[uuid.UUID]:
    res = await repo.get_posts_by_tag(tag)
    return [obj[0] for obj in res]
