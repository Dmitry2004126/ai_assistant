from fastapi import APIRouter

from app.core.auth.backend import auth_backend
from app.core.auth.users import fastapi_users
from app.schemas.user import UserRead, UserCreate


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
