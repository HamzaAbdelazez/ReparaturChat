import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from api.routers.dependencies import db_dependency
from api.service.rag import process_question
from api.database.table_models import ChatMessage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

@router.get("/history")
async def get_chat_history(
    user_id: UUID = Query(..., description="UUID of the user"),
    document_id: UUID | None = Query(None, description="Optional UUID of the document"),
    db: AsyncSession = Depends(db_dependency),
):
    """
    Endpoint: /chat/history
    - Returns all previous chat messages for a given user.
    - If document_id is provided, filter by document as well.
    - Helps restore chat history after logout/login.
    """
    try:
        query = select(ChatMessage).where(ChatMessage.user_id == user_id)
        if document_id:
            query = query.where(ChatMessage.document_id == document_id)

        query = query.order_by(ChatMessage.created_at.asc())
        result = await db.execute(query)
        messages = result.scalars().all()

        return [
            {
                "id": str(msg.id),
                "role": msg.role,  # "user" or "assistant"
                "message": msg.message,
                "document_id": str(msg.document_id) if msg.document_id else None,
                "created_at": msg.created_at,
            }
            for msg in messages
        ]

    except Exception as e:
        logger.error(f"❌ Error fetching chat history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch chat history")

@router.get("/")
async def chat_with_pdf(
    question: str = Query(..., description="User question"),
    document_id: UUID = Query(..., description="UUID of the uploaded PDF"),
    user_id: UUID = Query(..., description="UUID of the user asking the question"),
    db: AsyncSession = Depends(db_dependency),
):
    """
    Endpoint: /chat
    - Accepts a user question, document_id, and user_id.
    - Retrieves relevant chunks from the database.
    - Sends the context + question to Gemma 3 for answering.
    - Stores the conversation (Q & A) in the database for history.
    - Returns the model's response.
    """
    try:
        result = await process_question(
            question=question,
            db=db,
            document_id=document_id,
            user_id=user_id,
        )
        return result
    except Exception as e:
        logger.error(f"❌ Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


