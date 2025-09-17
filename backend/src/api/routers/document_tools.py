from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.config.db import get_db
from api.models import document_tool as schemas
from api.database.repository import document_tool as repository
import uuid

router = APIRouter(
    prefix="/documents",
    tags=["Document Tools"],
)

@router.post("/{document_id}/tools/{tool_id}", response_model=schemas.DocumentToolRead)
def add_tool_to_document(document_id: uuid.UUID, tool_id: uuid.UUID, db: Session = Depends(get_db)):
    return repository.add_tool_to_document(db, document_id, tool_id)

@router.get("/{document_id}/tools", response_model=list[schemas.DocumentToolRead])
def get_tools_for_document(document_id: uuid.UUID, db: Session = Depends(get_db)):
    return repository.get_tools_for_document(db, document_id)

@router.delete("/{document_id}/tools/{tool_id}", response_model=schemas.DocumentToolRead)
def remove_tool_from_document(document_id: uuid.UUID, tool_id: uuid.UUID, db: Session = Depends(get_db)):
    mapping = repository.remove_tool_from_document(db, document_id, tool_id)
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    return mapping
