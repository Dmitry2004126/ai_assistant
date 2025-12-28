from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users.db import BaseUserDatabase

from app.core.auth.dependencies.db import get_user_db
from app.core.auth.manager import UserManager
from app.models.user import User


async def get_user_manager(
    user_db: BaseUserDatabase[User, int] = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    """
    Dependency для получения менеджера пользователей.

    Предоставляет экземпляр UserManager, который отвечает за:
    - Создание и валидацию пользователей
    - Управление паролями

    Args:
        user_db (BaseUserDatabase[User, int]): Адаптер бд пользователей,
                                              получаемый через зависимость get_user_db.

    Yields:
        UserManager: Менеджер пользователей.
    """
    yield UserManager(user_db)
