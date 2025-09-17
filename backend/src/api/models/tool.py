import uuid
from pydantic import BaseModel
from typing import Optional


class ToolBase(BaseModel):
    name: str
    description: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    reusability_score: Optional[int] = None


class ToolCreate(ToolBase):
    pass


class ToolRead(ToolBase):
    id: uuid.UUID

    class Config:
        orm_mode = True
