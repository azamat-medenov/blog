import uuid
from typing import Type, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, or_
from sqlalchemy.orm import selectinload

from src.app.specification import Specification
from src.app.schemas import (
    AuthorCreateDTO, AuthorDTO, CategoryDTO, CreatePostDTO)
from src.infrastructure.database.models import Author, Category, Post, Tag, Media, post_tag


class TagRepo:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model: Type[Tag] = Tag

    async def get_tag(self, specification: Specification):
        query = select(self.model).filter_by(
            **specification.is_specified()
        )
        res = await self.session.execute(query)
        return res.scalar_one_or_none()


class PostRepo:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model: Type[Post] = Post
        self.association_table: Type[post_tag] = post_tag

    async def get_post(self, post_id: uuid.UUID) -> Post:
        query = (select(self.model).options(
            selectinload(Post.tags),
            selectinload(Post.media)).
                 filter(self.model.id == post_id))
        res = await self.session.execute(query)
        return res.scalar_one()

    async def create_post(
            self, schema: CreatePostDTO, author_id: uuid.UUID) -> Post:
        stmt = insert(self.model).values(
            **schema.model_dump(),
            author_id=author_id
        ).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    @staticmethod
    async def add_tags(post: Post, tags: list[Tag]):
        await post.tags.extend(tags)

    async def get_posts_by_tag(self, tag: str):
        query = (select(self.model.id).
                 join_from(self.model, self.association_table).
                 join_from(self.association_table, Tag).
                 filter(Tag.name == tag))
        res = await self.session.execute(query)
        return res.all()

    async def get_posts_by_category(self, category_id: int):
        query = (select(self.model.id).
                 join(self.model.category).
                 filter(self.model.category_id == category_id))
        res = await self.session.execute(query)
        return res.all()


class CategoryRepo:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model: Type[Category] = Category

    async def create_category(self, schema: CategoryDTO) -> Any:
        stmt = insert(self.model).values(
            **schema.model_dump()
        ).returning(self.model.id)
        res = await self.session.execute(stmt)
        await self.session.commit()
        return res.one()

    async def get_category(self, id: int) -> Category:
        query = select(self.model).filter_by(id=id)
        res = await self.session.execute(query)
        return res.scalar_one()


class AuthorRepo:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model: Type[Author] = Author

    async def get_author(
            self, specification: Specification) -> Author | None:
        query = select(self.model).filter_by(
            **specification.is_specified()
        )
        res = await self.session.execute(query)
        return res.scalar_one_or_none()

    async def is_author_exists(self, schema: AuthorCreateDTO) -> bool:
        query = select(self.model).where(or_(
            self.model.username == schema.username,
            self.model.email == schema.email)
        )
        res = await self.session.execute(query)
        return res.first() is not None

    async def create_author(self, schema: AuthorDTO) -> Any:
        stmt = insert(self.model).values(
            id=schema.id,
            username=schema.username,
            name=schema.name,
            hashed_password=schema.hashed_password,
            email=schema.email
        ).returning(
            self.model.id,
            self.model.username,
            self.model.email,
            self.model.name)

        res = await self.session.execute(stmt)
        await self.session.commit()
        return res.one()

    async def get_hashed_password(
            self, specification: Specification) -> str:
        query = (select(self.model.hashed_password).
                 filter_by(**specification.is_specified()))

        res = await self.session.execute(query)
        return res.scalar_one()


class MediaRepo:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model: Type[Media] = Media

    async def get_media(self, media_id: uuid.UUID) -> Media:
        query = select(self.model).filter_by(id=media_id)
        res = await self.session.execute(query)
        return res.scalar_one()
