import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from pydantic import BaseModel
from api.routers.dependencies import db_dependency
from api.database.table_models import Conversation, Message, UploadedPdf
from typing import List

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/conversations", tags=["conversations"])

@router.get("/test")
async def test_async():
    """Simple test endpoint to verify async is working."""
    return {"status": "async working"}

@router.get("/")
async def get_user_conversations(
    user_id: UUID = Query(..., description="UUID of the user"),
    db: AsyncSession = Depends(db_dependency),
):
    """Get all conversations for a user, ordered by most recent."""
    try:
        # Simple test first - just return conversations without messages
        conversations_query = select(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.created_at.desc())
        
        conversations_result = await db.execute(conversations_query)
        conversations = conversations_result.scalars().all()
        
        result = []
        for conv in conversations:
            # Get the latest message for preview
            latest_message_query = select(Message).filter(
                Message.conversation_id == conv.id
            ).order_by(Message.timestamp.desc()).limit(1)
            
            latest_message_result = await db.execute(latest_message_query)
            latest_message = latest_message_result.scalar_one_or_none()
            
            # Get message count using func.count()
            from sqlalchemy import func
            message_count_query = select(func.count(Message.id)).filter(Message.conversation_id == conv.id)
            message_count_result = await db.execute(message_count_query)
            message_count = message_count_result.scalar()
            
            result.append({
                "id": str(conv.id),
                "title": conv.title,
                "created_at": conv.created_at,
                "latest_message": latest_message.content[:50] + "..." if latest_message else "No messages",
                "message_count": message_count
            })
        
        return result
        
    except Exception as e:
        logger.exception("Error fetching conversations")
        raise HTTPException(status_code=500, detail=f"Failed to fetch conversations: {str(e)}")

@router.post("/")
async def create_conversation(
    user_id: UUID,
    title: str = "New Chat",
    db: AsyncSession = Depends(db_dependency),
):
    """Create a new conversation."""
    try:
        conversation = Conversation(
            user_id=user_id,
            title=title
        )
        
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        
        return {
            "id": str(conversation.id),
            "title": conversation.title,
            "created_at": conversation.created_at,
            "user_id": str(conversation.user_id)
        }
        
    except Exception as e:
        logger.exception("Error creating conversation")
        raise HTTPException(status_code=500, detail="Failed to create conversation")

@router.get("/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: UUID,
    db: AsyncSession = Depends(db_dependency),
):
    """Get all messages in a conversation."""
    try:
        from sqlalchemy import select
        
        messages_query = select(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp.asc())
        
        messages_result = await db.execute(messages_query)
        messages = messages_result.scalars().all()
        
        result = []
        for msg in messages:
            message_data = {
                "id": str(msg.id),
                "type": msg.type,
                "content": msg.content,
                "timestamp": msg.timestamp,
                "conversation_id": str(msg.conversation_id)
            }
            
            # For PDF messages, we'll store the PDF ID in a simple way
            if msg.type == "pdf":
                # Try to find the most recent PDF for this user as a workaround
                message_data["attachment"] = {
                    "type": "pdf",
                    "filename": msg.content.replace("📄 Uploaded: ", "")
                }
            
            result.append(message_data)
        
        return result
        
    except Exception as e:
        logger.exception("Error fetching conversation messages")
        raise HTTPException(status_code=500, detail="Failed to fetch messages")

class MessageCreate(BaseModel):
    message_type: str
    content: str

@router.post("/{conversation_id}/messages")
async def add_message_to_conversation(
    conversation_id: UUID,
    message_data: MessageCreate,
    db: AsyncSession = Depends(db_dependency),
):
    """Add a message to a conversation."""
    try:
        message = Message(
            conversation_id=conversation_id,
            type=message_data.message_type,
            content=message_data.content
        )
        
        db.add(message)
        await db.commit()
        await db.refresh(message)
        
        return {
            "id": str(message.id),
            "type": message.type,
            "content": message.content,
            "timestamp": message.timestamp,
            "conversation_id": str(message.conversation_id)
        }
        
    except Exception as e:
        logger.exception("Error adding message to conversation")
        raise HTTPException(status_code=500, detail="Failed to add message")

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(db_dependency),
):
    """Delete a conversation and all its messages."""
    try:
        from sqlalchemy import select
        
        conversation_query = select(Conversation).filter(Conversation.id == conversation_id)
        conversation_result = await db.execute(conversation_query)
        conversation = conversation_result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        db.delete(conversation)
        await db.commit()
        
        return {"message": "Conversation deleted successfully"}
        
    except Exception as e:
        logger.exception("Error deleting conversation")
        raise HTTPException(status_code=500, detail="Failed to delete conversation")


@router.post("/{conversation_id}/upload-pdf")
async def upload_pdf_to_conversation(
    conversation_id: UUID,
    file: UploadFile = File(...),
    user_id: UUID = Query(...),
    db: AsyncSession = Depends(db_dependency)
):
    """
    Upload a PDF to a conversation (ChatGPT-style).
    Uses the existing uploaded_pdfs functionality.
    """
    try:
        logger.info(f"📄 Starting PDF upload for user {user_id}")
        
        # For now, use the existing PDF upload system
        # Just upload the PDF normally and return success
        formData = {
            'file': file,
            'user_id': user_id
        }
        
        # Validate file
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            logger.error(f"Invalid file type: {file.filename}")
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Read file content
        content = await file.read()
        if len(content) == 0:
            logger.error("Empty file uploaded")
            raise HTTPException(status_code=400, detail="File is empty")
            
        logger.info(f"📄 Processing PDF: {file.filename} ({len(content)} bytes)")

        # Create PDF record using existing system
        new_pdf = UploadedPdf(
            id=uuid.uuid4(),
            title=file.filename,
            content=content,
            file_size=len(content),
            user_id=user_id
        )
        db.add(new_pdf)
        await db.flush()
        await db.commit()
        
        logger.info(f"📄 PDF uploaded successfully: {file.filename}")
        
        return {
            "message": "PDF uploaded successfully",
            "pdf_id": str(new_pdf.id),
            "message_id": "temp", 
            "filename": file.filename,
            "tools_extracted": 0  # For now
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading PDF: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")