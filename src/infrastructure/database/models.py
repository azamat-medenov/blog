import uuid

from typing import List
from datetime import datetime

from sqlalchemy import String, Column, ForeignKey, Table
from src.app.uuid7 import uuid7
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


post_tag = Table(
    "post_tag",
    Base.metadata,
    Column("post_id", ForeignKey("post.id")),
    Column("tag_id", ForeignKey("tag.id")),
)


class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    posts: Mapped[List["Post"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
    name: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        unique=True,
        index=True
    )
    posts: Mapped[List["Post"]] = relationship(
        secondary=post_tag,
        back_populates="tags",
        lazy="selectin"
    )

    def __repr__(self):
        return f"<Tag: {self.name}>"


class Post(Base):
    __tablename__ = "post"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
    text: Mapped[str] = mapped_column(nullable=False)
    date_created: Mapped[datetime] = mapped_column(default=datetime.now())
    author_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("author.id"), nullable=False, index=True
    )
    category_id: Mapped[id] = mapped_column(
        ForeignKey("category.id"), nullable=False, index=True
    )
    category: Mapped["Category"] = relationship(
        back_populates="posts",
        lazy="selectin"
    )
    author: Mapped["Author"] = relationship(back_populates="posts")
    media: Mapped[List["Media"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    tags: Mapped[List["Tag"]] = relationship(
        secondary=post_tag,
        back_populates="posts",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Post: {self.id=}, tags:{self.tags}>"


class Author(Base):
    __tablename__ = "author"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
    username: Mapped[str] = mapped_column(String(25), unique=True)
    name: Mapped[str] = mapped_column(String(25))
    email: Mapped[str]
    hashed_password: Mapped[str]

    posts: Mapped[List['Post']] = relationship(
        back_populates='author',
        cascade='all, delete-orphan',
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Author: {self.username}>"


class Media(Base):
    __tablename__ = "media"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
    media_type: Mapped[str]

    post_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("post.id"), nullable=False, index=True
    )
    post: Mapped["Post"] = relationship(back_populates='media')

    def __repr__(self) -> str:
        return f"<Media: {self.id}>"
