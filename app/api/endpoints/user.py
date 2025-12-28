import uuid

from fastapi import APIRouter
from fastapi_users import FastAPIUsers

from app.core.auth.backend import auth_backend
from app.core.auth.dependencies.manager import get_user_manager
from app.models.user import User
from app.schemas.user import UserRead, UserCreate

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

router = APIRouter(prefix='', tags=[])

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix='/auth',
    tags=['auth'],
)
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/auth',
    tags=['auth'],
)
