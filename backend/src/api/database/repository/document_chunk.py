from sqlalchemy.orm import Session
from api.database import table_models as models
from api.models import document_chunk as schemas

# Create new chunk
def create_chunk(db: Session, chunk: schemas.DocumentChunkCreate):
    db_chunk = models.DocumentChunk(
        document_id=chunk.document_id,
        user_id=chunk.user_id,
        content=chunk.content,
        embedding=chunk.embedding
    )
    db.add(db_chunk)
    db.commit()
    db.refresh(db_chunk)
    return db_chunk

# Get all chunks for a document
def get_chunks_by_document(db: Session, document_id):
    return db.query(models.DocumentChunk).filter(
        models.DocumentChunk.document_id == document_id
    ).all()

# Get single chunk
def get_chunk(db: Session, chunk_id):
    return db.query(models.DocumentChunk).filter(
        models.DocumentChunk.id == chunk_id
    ).first()
