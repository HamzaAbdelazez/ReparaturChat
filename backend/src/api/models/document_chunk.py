import uuid
from typing import List
from pydantic import BaseModel

class DocumentChunkBase(BaseModel):
    content: str

class DocumentChunkCreate(DocumentChunkBase):
    document_id: uuid.UUID
    user_id: uuid.UUID
    embedding: List[float]

class DocumentChunkRead(DocumentChunkBase):
    id: uuid.UUID
    document_id: uuid.UUID
    user_id: uuid.UUID
    embedding: List[float]

    class Config:
        orm_mode = True
