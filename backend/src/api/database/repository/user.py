from api.database.repository.base import BaseRepository
from api.database.table_models import User


class UserRepository(BaseRepository[User]):
    model = User
