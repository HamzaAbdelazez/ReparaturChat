from dataclasses import dataclass
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
from api.config.db import get_db
from api.service.rag import process_question, ask_gemma3
from api.database.table_models import ChatMessage, Message, Conversation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


def get_conversation_history(conversation_id: UUID, db: Session, limit: int = 10) -> str:
    """
    Retrieve recent conversation history and format it for AI context.
    Returns a formatted string with conversation history.
    """
    if not conversation_id:
        return ""
    
    try:
        # Get recent messages from the conversation (excluding the current message being processed)
        messages = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp.desc())
            .limit(limit)
            .all()
        )
        
        if not messages:
            return ""
        
        # Reverse to get chronological order and format for context
        messages = list(reversed(messages))
        
        context_parts = ["Previous conversation context:"]
        for msg in messages:
            role = "User" if msg.type == "user" else "Assistant"
            context_parts.append(f"{role}: {msg.content}")
        
        return "\n".join(context_parts) + "\n\nBased on this conversation history, please respond to the new question:"
        
    except Exception as e:
        logger.warning(f"Failed to retrieve conversation history: {e}")
        return ""


@dataclass(frozen=True)
class UserLevelQuestionPrefix:
    BASE_PREFIX = """
    You are a helpful assistant for a repair platform. Answer all questions in English and focus on repair topics for household appliances. 
    
    When applicable, mention:
    - What tools are needed
    - Current prices and cost estimates
    - Vendor suggestions with links
    - Comparison between self-repair and professional help (cost & time)
    """
    BEGINNER: str = f"{BASE_PREFIX}\nI am a beginner with little prior experience in repairs."
    INTERMEDIATE: str = f"{BASE_PREFIX}\nI have intermediate knowledge in repairs."
    EXPERT: str = f"{BASE_PREFIX}\nI am an expert with extensive repair knowledge."


@router.get("/general")
def general_chat(
        question: str, 
        user_id: UUID, 
        user_level_rate: int = Query(1, ge=1, le=5, description="User expertise level from 1 (beginner) to 5 (expert)"),
        conversation_id: UUID = Query(None, description="Optional conversation ID for context"),
        db: Session = Depends(get_db)
    ):
    """
    General chatbot endpoint (no document required).
    """
    try:
        if user_level_rate == 3 or user_level_rate == 4:
            question_prefix = UserLevelQuestionPrefix.INTERMEDIATE
        elif user_level_rate == 5:
            question_prefix = UserLevelQuestionPrefix.EXPERT
        else:
            question_prefix = UserLevelQuestionPrefix.BEGINNER

        # Get conversation history for context
        conversation_context = get_conversation_history(conversation_id, db) if conversation_id else ""
        
        # Build the full question with context
        if conversation_context:
            full_question = f"{question_prefix}\n\n{conversation_context}\n\nNew question: {question}"
        else:
            full_question = f"{question_prefix}, {question}"
        
        # Call Gemma with conversation context
        response = ask_gemma3(full_question)
        answer = response.get("answer", "No answer")

        # Save chat history (no document_id here)
        user_msg = ChatMessage(user_id=user_id, role="user", message=question)
        assistant_msg = ChatMessage(user_id=user_id, role="assistant", message=answer)

        db.add(user_msg)
        db.add(assistant_msg)
        db.commit()

        return {"question": question, "answer": answer}

    except Exception as e:
        logger.exception("❌ General chat error")
        raise HTTPException(status_code=500, detail=f"General chat error: {str(e)}")


@router.get("/pdf")
def chat_with_pdf(
    question: str = Query(..., description="User question"),
    document_id: UUID = Query(..., description="UUID of the uploaded PDF"),
    user_id: UUID = Query(..., description="UUID of the user asking the question"),
    user_level_rate: int = Query(1, ge=1, le=5, description="User expertise level from 1 (beginner) to 5 (expert)"),
    conversation_id: UUID = Query(None, description="Optional conversation ID for context"),
    db: Session = Depends(get_db),
):
    """
    Ask a question about a specific uploaded PDF.
    - Retrieves relevant chunks from DB (filtered by document_id).
    - Sends context + question to Gemma 3 for answering.
    - Stores Q&A in chat history table.
    - Returns the model's response + elapsed time.
    """
    try:
        if user_level_rate == 3 or user_level_rate == 4:
            question_prefix = UserLevelQuestionPrefix.INTERMEDIATE
        elif user_level_rate == 5:
            question_prefix = UserLevelQuestionPrefix.EXPERT
        else:
            question_prefix = UserLevelQuestionPrefix.BEGINNER

        # Get conversation history for context
        conversation_context = get_conversation_history(conversation_id, db) if conversation_id else ""
        
        # Build the question with user level prefix and conversation context
        if conversation_context:
            question = f"{question_prefix}\n\n{conversation_context}\n\nNew question: {question}"
        else:
            question = f"{question_prefix}, {question}"
            
        result = process_question(
            question=question,
            db=db,
            document_id=document_id,
            user_id=user_id,
        )
        return result  # includes "answer", "raw_response", "elapsed_time"
    except Exception as e:
        logger.exception("❌ Chat with PDF error")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.get("/history")
def get_chat_history(
    user_id: UUID = Query(..., description="UUID of the user"),
    document_id: UUID | None = Query(None, description="Optional UUID of the document"),
    db: Session = Depends(get_db),
):
    """
    Returns all previous chat messages for a given user.
    If document_id is provided, filter by document as well.
    """
    try:
        query = db.query(ChatMessage).filter(ChatMessage.user_id == user_id)
        if document_id:
            query = query.filter(ChatMessage.document_id == document_id)

        messages = query.order_by(ChatMessage.created_at.asc()).all()

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
