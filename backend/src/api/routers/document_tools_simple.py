from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from api.config.db import get_db
from api.database.table_models import DocumentTool, Tool
from api.models.tool import ToolRead
import uuid
from typing import List

router = APIRouter(
    prefix="/document_tools",
    tags=["Document Tools - Simple"],
)

@router.get("/", response_model=List[ToolRead])
def get_tools_for_document_query_param(
    document_id: str = Query(..., description="Document ID"),
    db: Session = Depends(get_db)
):
    """
    Get tools for a document using query parameter to match frontend expectations.
    Frontend calls: /document_tools/?document_id=<uuid>
    """
    try:
        document_uuid = uuid.UUID(document_id)
        
        # Query tools linked to this document
        tools = (
            db.query(Tool)
            .join(DocumentTool, DocumentTool.tool_id == Tool.id)
            .filter(DocumentTool.document_id == document_uuid)
            .all()
        )
        
        return tools
    except ValueError:
        # Invalid UUID format
        return []
    except Exception:
        # Any other error
        return []