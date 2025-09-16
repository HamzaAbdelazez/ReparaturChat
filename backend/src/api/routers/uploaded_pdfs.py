import uuid
import logging
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
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
    db: AsyncSession = Depends(db_dependency),
    background_tasks: BackgroundTasks = None,
):
    """
    Upload a PDF:
    1. Validate file type
    2. Save metadata + content to DB
    3. Extract text, split into chunks, store embeddings
    4. Schedule background extraction of tools & parts
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
                chunks = chunk_text(pre_extracted_text)
                await store_chunks_in_db(chunks, new_pdf.id, uuid.UUID(user_id), db)
                logger.info(f"💾 Stored {len(chunks)} chunks for PDF {new_pdf.id}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to process chunks for {new_pdf.id}: {e}")

        return UploadedPdfOut.model_validate(new_pdf)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Upload error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected upload error")
