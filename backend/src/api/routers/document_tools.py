from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.routers.dependencies import db_dependency
from api.models import tool as tool_schemas
from api.database.table_models import DocumentTool, Tool
import uuid

router = APIRouter(
    prefix="/documents",
    tags=["Document Tools"],
)

@router.get("/{document_id}/tools", response_model=list[tool_schemas.ToolRead])
async def get_tools_for_document(document_id: uuid.UUID, db: AsyncSession = Depends(db_dependency)):
    """Get all tools associated with a document."""
    try:
        # Query tools that are linked to this document
        result = await db.execute(
            select(Tool)
            .join(DocumentTool)
            .where(DocumentTool.document_id == document_id)
        )
        tools = result.scalars().all()
        return [tool_schemas.ToolRead.model_validate(tool) for tool in tools]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting tools: {str(e)}")

@router.post("/{document_id}/tools/{tool_id}")
async def add_tool_to_document(document_id: uuid.UUID, tool_id: uuid.UUID, db: AsyncSession = Depends(db_dependency)):
    """Add a tool to a document."""
    try:
        mapping = DocumentTool(document_id=document_id, tool_id=tool_id)
        db.add(mapping)
        await db.commit()
        return {"message": "Tool added to document", "document_id": str(document_id), "tool_id": str(tool_id)}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding tool: {str(e)}")

@router.delete("/{document_id}/tools/{tool_id}")
async def remove_tool_from_document(document_id: uuid.UUID, tool_id: uuid.UUID, db: AsyncSession = Depends(db_dependency)):
    """Remove a tool from a document."""
    try:
        result = await db.execute(
            select(DocumentTool).where(
                DocumentTool.document_id == document_id,
                DocumentTool.tool_id == tool_id
            )
        )
        mapping = result.scalar_one_or_none()
        
        if not mapping:
            raise HTTPException(status_code=404, detail="Tool mapping not found")
        
        await db.delete(mapping)
        await db.commit()
        return {"message": "Tool removed from document", "document_id": str(document_id), "tool_id": str(tool_id)}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error removing tool: {str(e)}")
