import uuid
import logging
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from starlette.status import HTTP_201_CREATED

from api.routers.dependencies import db_dependency
from api.models.uploaded_pdf import UploadedPdfOut
from api.database.table_models import UploadedPdf, Tool, DocumentTool
from api.service.rag import extract_text_from_pdf_bytes, chunk_text, store_chunks_in_db
from api.service.tools_extractor import extract_tools_from_text  # 🔥 new

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/uploadedPdfs", tags=["uploadedPdfs"])


@router.post(
    "/",
    operation_id="UploadPdf",
    status_code=HTTP_201_CREATED,
    response_model=UploadedPdfOut,
)
async def upload_pdf(
    file: UploadFile = File(...),
    user_id: str = "00000000-0000-0000-0000-000000000000",
    db: AsyncSession = Depends(db_dependency),
    background_tasks: BackgroundTasks = None,
):
    """
    Upload a PDF:
    1. Validate file type
    2. Save metadata + content to DB
    3. Extract text, split into chunks, store embeddings
    4. Extract tools from PDF and save them
    """
    try:
        # 1. Validate file
        if file.content_type != "application/pdf" or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Invalid file. Must be a PDF.")

        # Read file into memory
        content_bytes = await file.read()

        # 2. Save PDF into DB
        new_pdf = UploadedPdf(
            id=uuid.uuid4(),
            title=file.filename,
            content=content_bytes,
            file_size=len(content_bytes),
            user_id=uuid.UUID(user_id),
        )
        db.add(new_pdf)
        await db.commit()
        await db.refresh(new_pdf)

        # 3. Extract text + chunks
        pre_extracted_text = ""
        try:
            pre_extracted_text = extract_text_from_pdf_bytes(content_bytes)
            if pre_extracted_text.strip():
                # Save chunks + embeddings
                chunks = chunk_text(pre_extracted_text)
                await store_chunks_in_db(chunks, new_pdf.id, uuid.UUID(user_id), db)
                logger.info(f"💾 Stored {len(chunks)} chunks for PDF {new_pdf.id}")

                # 4. Extract tools
                tools = extract_tools_from_text(pre_extracted_text)
                for tool_name in tools:
                    # Check if tool already exists
                    result = await db.execute(
                        text("SELECT id FROM tools WHERE name=:name"),
                        {"name": tool_name},
                    )
                    row = result.first()

                    if row:
                        tool_id = row[0]
                    else:
                        # Get enhanced tool details
                        from api.service.tools_extractor import get_tool_details
                        tool_details = get_tool_details(tool_name)
                        
                        tool = Tool(
                            id=uuid.uuid4(), 
                            name=tool_name,
                            description=tool_details["description"],
                            reusability_score=tool_details["reusability_score"]
                        )
                        db.add(tool)
                        await db.flush()
                        tool_id = tool.id
                        
                        # Trigger price fetching in background
                        try:
                            from api.service.tool_pricing import ToolPricingService
                            pricing_service = ToolPricingService(db)
                            await pricing_service.update_tool_prices(tool_id)
                            logger.info(f"💰 Updated prices for tool: {tool_name}")
                        except Exception as price_error:
                            logger.warning(f"⚠️ Failed to fetch prices for {tool_name}: {price_error}")

                    # Link tool to this document
                    db.add(DocumentTool(document_id=new_pdf.id, tool_id=tool_id))

                await db.commit()
                logger.info(f"🔧 Extracted and saved {len(tools)} tools for PDF {new_pdf.id}")

        except Exception as e:
            logger.warning(f"⚠️ Failed to process chunks/tools for {new_pdf.id}: {e}")

        return UploadedPdfOut.model_validate(new_pdf)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Upload error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected upload error")


@router.delete("/{document_id}")
async def delete_pdf(
    document_id: uuid.UUID,
    user_id: uuid.UUID = Query(..., description="User ID who owns the document"),
    db: AsyncSession = Depends(db_dependency)
):
    """
    Delete an uploaded PDF and all related data (chunks, tools, messages).
    Only the owner can delete their own documents.
    """
    try:
        # Verify the document exists and belongs to the user
        result = await db.execute(
            select(UploadedPdf).where(
                UploadedPdf.id == document_id, 
                UploadedPdf.user_id == user_id
            )
        )
        pdf_document = result.scalar_one_or_none()
        
        if not pdf_document:
            raise HTTPException(
                status_code=404, 
                detail="Document not found or you don't have permission to delete it"
            )
        
        # Delete the document (cascade will handle related data)
        await db.delete(pdf_document)
        await db.commit()
        
        logger.info(f"📄 Deleted PDF {document_id} for user {user_id}")
        
        return {
            "message": "PDF deleted successfully",
            "document_id": str(document_id),
            "title": pdf_document.title
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting PDF: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
