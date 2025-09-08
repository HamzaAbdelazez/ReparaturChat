import uuid

from pydantic import BaseModel


class UserIn(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: uuid.UUID
    username: str


class UserLoginIn(BaseModel):
    username: str
    password: str


class UserLoginOut(BaseModel):
    id: uuid.UUID
    username: str
