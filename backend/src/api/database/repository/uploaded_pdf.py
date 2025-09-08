from api.database.repository.base import BaseRepository
from api.database.table_models import UploadedPdf


class UploadedPdfRepository(BaseRepository[UploadedPdf]):
    model = UploadedPdf
