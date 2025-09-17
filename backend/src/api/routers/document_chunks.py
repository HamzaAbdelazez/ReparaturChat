from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.config.db import get_db
from api.database.repository import document_chunk as repository
from api.models import document_chunk as schemas
import uuid

router = APIRouter(
    prefix="/chunks",
    tags=["Document Chunks"],
)

@router.post("/", response_model=schemas.DocumentChunkRead)
def create_chunk(chunk: schemas.DocumentChunkCreate, db: Session = Depends(get_db)):
    return repository.create_chunk(db, chunk)

@router.get("/{document_id}", response_model=list[schemas.DocumentChunkRead])
def get_chunks(document_id: uuid.UUID, db: Session = Depends(get_db)):
    chunks = repository.get_chunks_by_document(db, document_id)
    if not chunks:
        raise HTTPException(status_code=404, detail="No chunks found for this document")
    return chunks
