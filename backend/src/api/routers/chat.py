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
    # Simple prefixes that don't overwhelm normal conversation
    BEGINNER: str = "You are a helpful assistant. I'm new to repairs, so please explain things clearly."
    INTERMEDIATE: str = "You are a helpful assistant. I have some repair experience."
    EXPERT: str = "You are a helpful assistant. I'm experienced with repairs."
    
    # Only use detailed repair context for repair-specific questions
    REPAIR_CONTEXT = """
When discussing repairs, please include:
- Required tools and their prices
- Step-by-step instructions appropriate for the user's skill level
- Cost comparison: DIY vs professional service
- Safety considerations
"""


def is_repair_related_question(question: str) -> bool:
    """Check if the question is repair-related to decide whether to use repair context."""
    repair_keywords = [
        'repair', 'fix', 'broken', 'replace', 'install', 'maintenance', 
        'troubleshoot', 'problem', 'issue', 'error', 'malfunction',
        'appliance', 'dishwasher', 'washing machine', 'dryer', 'refrigerator',
        'oven', 'microwave', 'tools', 'parts', 'cost', 'professional'
    ]
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in repair_keywords)


def build_question_with_context(question: str, user_level_rate: int, conversation_context: str = "", is_repair_question: bool = False) -> str:
    """Build the question with appropriate context based on content and user level."""
    if user_level_rate in [3, 4]:
        level_prefix = UserLevelQuestionPrefix.INTERMEDIATE
    elif user_level_rate == 5:
        level_prefix = UserLevelQuestionPrefix.EXPERT
    else:
        level_prefix = UserLevelQuestionPrefix.BEGINNER
    
    # Build context parts
    context_parts = [level_prefix]
    
    # Add repair context only for repair-related questions
    if is_repair_question:
        context_parts.append(UserLevelQuestionPrefix.REPAIR_CONTEXT)
    
    # Add conversation history if available
    if conversation_context:
        context_parts.append(conversation_context)
        context_parts.append(f"New question: {question}")
    else:
        context_parts.append(f"Question: {question}")
    
    return "\n\n".join(context_parts)


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
        # Get conversation history for context
        conversation_context = get_conversation_history(conversation_id, db) if conversation_id else ""
        
        # Check if this is repair-related to determine context level
        is_repair_question = is_repair_related_question(question)
        
        # Build the question with appropriate context
        full_question = build_question_with_context(
            question=question,
            user_level_rate=user_level_rate,
            conversation_context=conversation_context,
            is_repair_question=is_repair_question
        )
        
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
        # Get conversation history for context
        conversation_context = get_conversation_history(conversation_id, db) if conversation_id else ""
        
        # For PDF chat, assume it's repair-related and include repair context
        enhanced_question = build_question_with_context(
            question=question,
            user_level_rate=user_level_rate,
            conversation_context=conversation_context,
            is_repair_question=True  # PDF uploads are typically repair manuals
        )
            
        result = process_question(
            question=enhanced_question,
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
