import uuid

from typing import List
from datetime import datetime

from sqlalchemy import String, Column, ForeignKey, Table
from src.app.uuid7 import uuid7
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


association_table = Table(
    "association_table",
    Base.metadata,
    Column("post_id", ForeignKey("post.id")),
    Column("tag_id", ForeignKey("tag.id")),
)


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    posts: Mapped[List["Post"]] = relationship(
        secondary=association_table, back_populates="tags"
    )

    def __repr__(self):
        return f"<Tag: {self.name}>"


class Post(Base):
    __tablename__ = "post"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
    date_created: Mapped[datetime] = mapped_column(default=datetime.now())
    author_fk: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("author.id"), nullable=False, index=True
    )
    tag: Mapped["Tag"] = relationship(back_populates="posts")
    author: Mapped["Author"] = relationship(back_populates="posts")
    medias: Mapped[List["Media"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )
    tags: Mapped[List["Tag"]] = relationship(
        secondary=association_table, back_populates="posts"
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
        back_populates='author', cascade='all, delete-orphan'
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

    def __repr__(self) -> str:
        return f"<Media: {self.id}>"
