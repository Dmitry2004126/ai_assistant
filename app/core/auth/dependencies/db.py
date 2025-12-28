from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.models.user import User


async def get_user_db(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[SQLAlchemyUserDatabase[User, int], None]:
    """
    Dependency для получения экземпляра SQLAlchemyUserDatabase.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy,
                               получаемая через зависимость get_async_session.

    Yields:
        SQLAlchemyUserDatabase[User, int]: Адаптер базы данных для SQLAlchemy.
    """
    yield SQLAlchemyUserDatabase(session, User)
