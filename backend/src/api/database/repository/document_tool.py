from sqlalchemy.orm import Session
from api.database.table_models import DocumentTool
from api.models import document_tool as schemas

def add_tool_to_document(db: Session, document_id: str, tool_id: str):
    mapping = DocumentTool(document_id=document_id, tool_id=tool_id)
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping

def get_tools_for_document(db: Session, document_id: str):
    return db.query(DocumentTool).filter(DocumentTool.document_id == document_id).all()

def remove_tool_from_document(db: Session, document_id: str, tool_id: str):
    mapping = db.query(DocumentTool).filter(
        DocumentTool.document_id == document_id,
        DocumentTool.tool_id == tool_id
    ).first()
    if mapping:
        db.delete(mapping)
        db.commit()
    return mapping
