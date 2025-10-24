from dataclasses import dataclass
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from api.routers.dependencies import db_dependency
from api.service.rag import process_question
from api.service.llm_service import llm_service, LLMProvider
from api.database.table_models import ChatMessage, Message, Conversation, Device, UserDevice

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


async def get_conversation_history(conversation_id: UUID, db: AsyncSession, limit: int = 10) -> str:
    """
    Retrieve recent conversation history and format it for AI context.
    Returns a formatted string with conversation history.
    """
    if not conversation_id:
        return ""
    
    try:
        # Get recent messages from the conversation (excluding the current message being processed)
        result = await db.execute(
            select(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp.desc())
            .limit(limit)
        )
        messages = result.scalars().all()
        
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


async def get_device_context(device_id: UUID, db: AsyncSession) -> str:
    """
    Retrieve device information and format it for AI context.
    Returns device details that the LLM can use for context.
    """
    if not device_id:
        return ""
    
    try:
        # Get device information
        result = await db.execute(select(Device).filter(Device.id == device_id))
        device = result.scalar_one_or_none()
        
        if not device:
            return ""
        
        device_context = f"""Device Context:
Manufacturer: {device.manufacturer}
Model: {device.model}
Category: {device.category}
Warranty Period: {device.warranty_period_months} months
Repair Complexity: {device.repair_complexity}/5

Please consider this device information when providing repair advice and recommendations."""
        
        return device_context
        
    except Exception as e:
        logger.warning(f"Failed to retrieve device context: {e}")
        return ""


async def get_conversation_with_device_context(conversation_id: UUID, db: AsyncSession) -> tuple[str, str]:
    """
    Get both conversation history and device context if conversation has device assigned.
    Returns tuple of (conversation_context, device_context).
    """
    conversation_context = ""
    device_context = ""
    
    if not conversation_id:
        return conversation_context, device_context
    
    try:
        # Get conversation with device info
        result = await db.execute(select(Conversation).filter(Conversation.id == conversation_id))
        conversation = result.scalar_one_or_none()
        
        if conversation:
            # Get conversation history
            conversation_context = await get_conversation_history(conversation_id, db)
            
            # Get device context if device is assigned to conversation
            if conversation.device_id:
                device_context = await get_device_context(conversation.device_id, db)
        
        return conversation_context, device_context
        
    except Exception as e:
        logger.warning(f"Failed to retrieve conversation and device context: {e}")
        return "", ""


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


def build_question_with_context(question: str, user_level_rate: int, conversation_context: str = "", device_context: str = "", is_repair_question: bool = False) -> str:
    """Build the question with appropriate context based on content and user level, including device context."""
    if user_level_rate in [3, 4]:
        level_prefix = UserLevelQuestionPrefix.INTERMEDIATE
    elif user_level_rate == 5:
        level_prefix = UserLevelQuestionPrefix.EXPERT
    else:
        level_prefix = UserLevelQuestionPrefix.BEGINNER
    
    # Build context parts
    context_parts = [level_prefix]
    
    # Add device context if available (important for repair context)
    if device_context:
        context_parts.append(device_context)
    
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
async def general_chat(
        question: str, 
        user_id: UUID, 
        user_level_rate: int = Query(1, ge=1, le=5, description="User expertise level from 1 (beginner) to 5 (expert)"),
        conversation_id: UUID = Query(None, description="Optional conversation ID for context"),
        llm_model: str = Query("gemma3", description="LLM model to use: gemma3, gemini, deepseek, or gpt5"),
        db: AsyncSession = Depends(db_dependency)
    ):
    """
    General chatbot endpoint with device context support.
    """
    try:
        # Get conversation history AND device context
        conversation_context, device_context = await get_conversation_with_device_context(conversation_id, db)
        
        # Check if this is repair-related to determine context level
        is_repair_question = is_repair_related_question(question)
        
        # Build the question with appropriate context including device info
        full_question = build_question_with_context(
            question=question,
            user_level_rate=user_level_rate,
            conversation_context=conversation_context,
            device_context=device_context,
            is_repair_question=is_repair_question
        )
        
        # Determine LLM provider
        try:
            llm_model_lower = llm_model.lower()
            if llm_model_lower == "gemma3":
                provider = LLMProvider.GEMMA3
            elif llm_model_lower == "gemini":
                provider = LLMProvider.GEMINI
            elif llm_model_lower == "deepseek":
                provider = LLMProvider.DEEPSEEK
            elif llm_model_lower == "gpt5":
                provider = LLMProvider.GPT5
            else:
                provider = LLMProvider.GEMMA3  # Default fallback
        except:
            provider = LLMProvider.GEMMA3  # Default fallback
        
        # Call selected LLM with conversation context
        response = llm_service.ask_question(
            question=full_question, 
            provider=provider,
            is_repair_question=is_repair_question,
            include_tools_parts=is_repair_question  # Only extract tools/parts for repair questions
        )
        answer = response.get("answer", "No answer")

        # Save chat history (no document_id here)
        user_msg = ChatMessage(user_id=user_id, role="user", message=question)
        assistant_msg = ChatMessage(user_id=user_id, role="assistant", message=answer)

        db.add(user_msg)
        db.add(assistant_msg)
        await db.commit()

        return {"question": question, "answer": answer}

    except Exception as e:
        logger.exception("❌ General chat error")
        raise HTTPException(status_code=500, detail=f"General chat error: {str(e)}")


@router.get("/pdf")
async def chat_with_pdf(
    question: str = Query(..., description="User question"),
    document_id: UUID = Query(..., description="UUID of the uploaded PDF"),
    user_id: UUID = Query(..., description="UUID of the user asking the question"),
    user_level_rate: int = Query(1, ge=1, le=5, description="User expertise level from 1 (beginner) to 5 (expert)"),
    conversation_id: UUID = Query(None, description="Optional conversation ID for context"),
    llm_model: str = Query("gemma3", description="LLM model to use: gemma3, gemini, deepseek, or gpt5"),
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
        # Get conversation history for context
        conversation_context = await get_conversation_history(conversation_id, db) if conversation_id else ""
        
        # For PDF chat, assume it's repair-related and include repair context
        enhanced_question = build_question_with_context(
            question=question,
            user_level_rate=user_level_rate,
            conversation_context=conversation_context,
            is_repair_question=True  # PDF uploads are typically repair manuals
        )
            
        result = await process_question(
            question=enhanced_question,
            db=db,
            document_id=document_id,
            user_id=user_id,
            llm_provider=llm_model,
        )
        return result  # includes "answer", "raw_response", "elapsed_time"
    except Exception as e:
        logger.exception("❌ Chat with PDF error")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


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
        query = select(ChatMessage).filter(ChatMessage.user_id == user_id)
        if document_id:
            query = query.filter(ChatMessage.document_id == document_id)

        result = await db.execute(query.order_by(ChatMessage.created_at.asc()))
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
