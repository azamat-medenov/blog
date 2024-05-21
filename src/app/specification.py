from abc import ABCMeta
from typing import Any
from uuid import UUID


class Specification(metaclass=ABCMeta):
    def is_specified(self) -> dict[Any, Any]:
        raise NotImplementedError


class NameSpecification(Specification):
    def __init__(self, name: str):
        self.name = name

    def is_specified(self) -> dict[str, str]:
        return {'name': self.name}


class IDSpecification(Specification):
    def __init__(self, id: UUID):
        self.id = id

    def is_specified(self) -> dict[str, UUID]:
        return {'id': self.id}


class EmailSpecification(Specification):
    def __init__(self, email: str):
        self.email = email

    def is_specified(self) -> dict[str, str]:
        return {'email': self.email}


class UsernameSpecification(Specification):
    def __init__(self, username: str):
        self.username = username

    def is_specified(self) -> dict[str, str]:
        return {'username': self.username}
