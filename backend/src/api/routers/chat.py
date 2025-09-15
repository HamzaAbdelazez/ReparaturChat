import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from api.routers.dependencies import db_dependency
from api.service.rag import process_question, ask_gemma3
from api.database.table_models import ChatMessage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/general")
async def general_chat(question: str, user_id: UUID, db: AsyncSession = Depends(db_dependency)):
    """
    General chatbot endpoint (no document required).
    """
    try:
        # Call Gemma without PDF context
        response = ask_gemma3(question, context="")
        answer = response.get("answer", "No answer")

        # Save chat history (no document_id here)
        user_msg = ChatMessage(user_id=user_id, role="user", message=question)
        assistant_msg = ChatMessage(user_id=user_id, role="assistant", message=answer)

        db.add_all([user_msg, assistant_msg])
        await db.commit()

        return {"question": question, "answer": answer}

    except Exception as e:
        logger.exception("❌ General chat error")
        raise HTTPException(status_code=500, detail=f"General chat error: {str(e)}")


@router.get("/history")
async def get_chat_history(
    user_id: UUID = Query(..., description="UUID of the user"),
    document_id: UUID | None = Query(None, description="Optional UUID of the document"),
    db: AsyncSession = Depends(db_dependency),
):
    """
    Returns all previous chat messages for a given user.
    If document_id is provided, filter by document as well.
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
                "role": msg.role,
                "message": msg.message,
                "document_id": str(msg.document_id) if msg.document_id else None,
                "created_at": msg.created_at,
            }
            for msg in messages
        ]

    except Exception as e:
        logger.exception("❌ Error fetching chat history")
        raise HTTPException(status_code=500, detail="Failed to fetch chat history")


@router.get("/")
async def chat_with_pdf(
    question: str = Query(..., description="User question"),
    document_id: UUID = Query(..., description="UUID of the uploaded PDF"),
    user_id: UUID = Query(..., description="UUID of the user asking the question"),
    db: AsyncSession = Depends(db_dependency),
):
    """
    Ask a question about a specific uploaded PDF.
    - Retrieves relevant chunks from DB (filtered by document_id).
    - Sends context + question to Gemma 3 for answering.
    - Stores Q&A in chat history table.
    - Returns the model's response + elapsed time.
    """
    try:
        result = await process_question(
            question=question,
            db=db,
            document_id=document_id,
            user_id=user_id,
        )
        return result  # includes "answer", "raw_response", "elapsed_time"
    except Exception as e:
        logger.exception("❌ Chat with PDF error")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
