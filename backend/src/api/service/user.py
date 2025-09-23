import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from api.database.repository.user import UserRepository
from api.database.table_models import User
from api.models.user import UserOut, UserIn, UserLoginOut
from api.shared.password_helper import hash_password, verify_password

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db=db)

    async def get_all_users(self) -> list[UserOut]:
        try:
            users = await self.repo.get_all()
            return [self.map_to_response_user_out_model(user=user) for user in users]
        except Exception as e:
            logger.error(f"Error getting all {self.repo.model.__name__}: {e}")
            return []

    async def create_user(self, user_in: UserIn) -> UserOut:
        try:
            existing_user = await self.repo.get_first_by_field(
                field_name="username", field_value=user_in.username
            )
            if existing_user:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST, detail="Username already taken"
                )

            new_user = await self.repo.create(
                instance=User(
                    username=user_in.username,
                    password=hash_password(user_in.password),
                    skill_level=user_in.skill_level,
                    physical_strength=user_in.physical_strength,
                    available_space=user_in.available_space,
                    experience_level=user_in.experience_level,
                    profile_updated_at=datetime.now(timezone.utc)
                )
            )
            return self.map_to_response_user_out_model(user=new_user)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating {self.repo.model.__name__}: {e}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
            )

    async def authenticate_user(self, username: str, password: str) -> UserLoginOut | None:
        try:
            user = await self.repo.get_first_by_field(
                field_name="username", field_value=username
            )
            if not user:
                return None

            if not verify_password(plain_password=password, hashed_password=user.password):
                return None

            return self.map_to_response_user_login_out_model(user=user)
        except Exception as e:
            logger.error(f"Error authenticating user '{username}': {e}")
            return None

    @staticmethod
    def map_to_response_user_out_model(user: User) -> UserOut:
        return UserOut(
            id=user.id,
            username=user.username,
            skill_level=user.skill_level,
            physical_strength=user.physical_strength,
            available_space=user.available_space,
            experience_level=user.experience_level,
            profile_updated_at=user.profile_updated_at
        )

    @staticmethod
    def map_to_response_user_login_out_model(user: User) -> UserLoginOut:
        return UserLoginOut(
            id=user.id,
            username=user.username,
            skill_level=user.skill_level,
            physical_strength=user.physical_strength,
            available_space=user.available_space,
            experience_level=user.experience_level
        )
