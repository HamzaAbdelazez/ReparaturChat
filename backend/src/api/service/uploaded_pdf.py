import logging
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from api.database.repository.uploaded_pdf import UploadedPdfRepository
from api.database.table_models import UploadedPdf
from api.models.uploaded_pdf import UploadedPdfIn, UploadedPdfOut

# NEW: import the extraction function (you'll add this in service/tools_parts.py)
# from api.service.tools_parts import extract_tools_parts_from_doc  

logger = logging.getLogger(__name__)


class UploadedPdfService:
    def __init__(self, db: AsyncSession):
        self.repo = UploadedPdfRepository(db=db)

    async def upload_pdf(self, uploaded_pdf_in: UploadedPdfIn) -> UploadedPdfOut:
        """
        Save a new PDF in the database using the repository layer.
        Returns a response model with the saved PDF metadata.
        Also triggers background extraction of tools & parts (US3).
        """
        try:
            new_pdf = await self.repo.create(
                instance=UploadedPdf(
                    title=uploaded_pdf_in.title,
                    content=uploaded_pdf_in.content,
                    file_size=uploaded_pdf_in.file_size,
                    user_id=uploaded_pdf_in.user_id,
                )
            )

            # OPTIONAL: if you have a chunk/embedding pipeline, call it here first
            # await process_document_chunks_and_embeddings(new_pdf.id)

            #NEW: kick off tools/parts extraction in the background
            # try:
            #     asyncio.create_task(extract_tools_parts_from_doc(str(new_pdf.id)))
            # except Exception as bg_err:
            #     # Don't fail the upload if extraction scheduling fails
            #     logger.warning(
            #         f"[warn] scheduling tools/parts extraction failed for {new_pdf.id}: {bg_err}"
            #     )

            return self.map_to_response_model(uploaded_pdf=new_pdf)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f" Error creating {self.repo.model.__name__}: {e}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    @staticmethod
    def map_to_response_model(uploaded_pdf: UploadedPdf) -> UploadedPdfOut:
        return UploadedPdfOut(
            id=uploaded_pdf.id,
            title=uploaded_pdf.title,
            uploaded_at=uploaded_pdf.uploaded_at,
            file_size=uploaded_pdf.file_size,
            user_id=uploaded_pdf.user_id,
        )
