import uuid
import logging
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_201_CREATED

from api.routers.dependencies import db_dependency
from api.models.uploaded_pdf import UploadedPdfOut
from api.database.table_models import UploadedPdf
from api.service.rag import extract_text_from_pdf_bytes, chunk_text, store_chunks_in_db

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
    db: AsyncSession = Depends(db_dependency),  # ✅ AsyncSession, not Session
):
    """
    Upload a PDF file:
    1. Validate the uploaded file is a PDF.
    2. Save it to the database (async).
    3. Extract text from the PDF.
    4. Split the text into chunks and store them with embeddings (async).
    """
    try:
        # 1. Validate file type
        if file.content_type != "application/pdf" or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Invalid file. Must be a PDF.")

        # Read PDF bytes
        content_bytes = await file.read()

        # 2. Save PDF metadata + content into DB
        new_pdf = UploadedPdf(
            id=uuid.uuid4(),
            title=file.filename,
            content=content_bytes,
            file_size=len(content_bytes),
            user_id=uuid.UUID(user_id),
        )
        db.add(new_pdf)
        await db.commit()         # ✅ must await
        await db.refresh(new_pdf) # ✅ load DB defaults (uploaded_at)

        # 3. Extract text from PDF and 4. store chunks
        try:
            text = extract_text_from_pdf_bytes(content_bytes)
            if text.strip():
                chunks = chunk_text(text)
                await store_chunks_in_db(chunks, new_pdf.id, db)  # ✅ async call
        except Exception as e:
            logger.warning(f"⚠️ Failed to process chunks: {e}")

        return UploadedPdfOut.model_validate(new_pdf)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Upload error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected upload error")
