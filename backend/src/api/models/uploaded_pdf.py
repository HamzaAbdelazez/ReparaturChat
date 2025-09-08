from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel


class UploadedPdfIn(BaseModel):
    user_id: UUID
    title: str
    content: bytes
    file_size: int | None = None


class UploadedPdfOut(BaseModel):
    id: UUID
    title: str
    file_size: int
    uploaded_at: datetime
    user_id: UUID

    class Config:
        from_attributes = True
