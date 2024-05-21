import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import List

from pydantic import BaseModel, Field, EmailStr, ConfigDict, model_validator

UTC_6 = timezone(timedelta(hours=6))


class CategoryDTO(BaseModel):
    id: int
    name: str


class TagDTO(BaseModel):
    id: uuid.UUID
    name: str


class CreatePostDTO(BaseModel):
    text: str
    category_id: int

    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class PostDTO(CreatePostDTO):
    id: uuid.UUID
    date_created: datetime
    author_id: uuid.UUID


class PostAuthorDTO(BaseModel):
    author: "AuthorOutDTO"


class Login(BaseModel):
    email_or_username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class AuthorBaseDTO(BaseModel):
    username: str = Field(max_length=20, min_length=6)
    email: EmailStr
    name: str = Field(max_length=20, min_length=6)

    model_config = ConfigDict(from_attributes=True)


class AuthorCreateDTO(AuthorBaseDTO):
    password: str = Field(max_length=30, min_length=8)


class AuthorOutDTO(AuthorBaseDTO):
    id: uuid.UUID


class AuthorDTO(AuthorOutDTO):
    hashed_password: str


class AuthorRelDTO(AuthorDTO):
    entries: List['PostDTO'] = []
