import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UserIn(BaseModel):
    username: str
    password: str
    skill_level: Optional[int] = 1  # 1-5 scale
    physical_strength: Optional[int] = 3  # 1-5 scale
    available_space: Optional[int] = 3  # 1-5 scale
    experience_level: Optional[int] = 1  # 1-5 scale


class UserOut(BaseModel):
    id: uuid.UUID
    username: str
    skill_level: int
    physical_strength: int
    available_space: int
    experience_level: int
    profile_updated_at: Optional[datetime]


class UserLoginIn(BaseModel):
    username: str
    password: str


class UserLoginOut(BaseModel):
    id: uuid.UUID
    username: str
    skill_level: int
    physical_strength: int
    available_space: int
    experience_level: int
