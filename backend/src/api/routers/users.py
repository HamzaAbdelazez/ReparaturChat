from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.routers.dependencies import db_dependency
from api.models.user import UserIn, UserOut, UserLoginIn, UserLoginOut
from api.service.user import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    path="/",
    operation_id="createUser",
    status_code=status.HTTP_201_CREATED,
    response_model=UserOut,
)
async def create_user(
        user_in: UserIn,
        db: AsyncSession = Depends(db_dependency),
):
    user_service = UserService(db=db)
    return await user_service.create_user(user_in=user_in)


@router.get(
    path="/",
    operation_id="getUsers",
    status_code=status.HTTP_200_OK,
    response_model=list[UserOut],
)
async def get_users(
        db: AsyncSession = Depends(db_dependency),
):
    user_service = UserService(db=db)
    return await user_service.get_all_users()


@router.post(
    path="/login",
    operation_id="loginUser",
    response_model=UserLoginOut,
)
async def login_user(
        credentials: UserLoginIn,
        db: AsyncSession = Depends(db_dependency),
):
    user_service = UserService(db=db)
    user = await user_service.authenticate_user(
        username=credentials.username,
        password=credentials.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or password",
        )

    return UserLoginOut(id=user.id, username=user.username)
