import uuid
from pydantic import BaseModel

class DocumentToolBase(BaseModel):
    document_id: uuid.UUID
    tool_id: uuid.UUID

class DocumentToolCreate(DocumentToolBase):
    pass

class DocumentToolRead(DocumentToolBase):
    id: uuid.UUID

    class Config:
        orm_mode = True
