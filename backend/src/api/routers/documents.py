import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.config.db import get_db
from api.database.table_models import DocumentTool, Tool
from api.models.tool import ToolRead

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.get("/{document_id}/tools", response_model=list[ToolRead])
def get_tools_for_document(document_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Return all tools linked to a given document via the document_tools table.
    """
    tools = (
        db.query(Tool)
        .join(DocumentTool, DocumentTool.tool_id == Tool.id)
        .filter(DocumentTool.document_id == document_id)
        .all()
    )
    return tools
