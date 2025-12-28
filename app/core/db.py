import re
from typing import AsyncGenerator

from sqlalchemy import BigInteger, Identity, MetaData
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from app.core.config import settings


class Base(AsyncAttrs, DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy.

    Предоставляет общую конфигурацию для ORM моделей, включая:
    - Асинхронные атрибуты через AsyncAttrs
    - Автоматическую генерацию имен таблиц
    - Единую схему именования ограничений
    - Стандартный первичный ключ

    Attributes:
        __abstract__ (bool): Указывает, что это абстрактный базовый класс.
        metadata (MetaData): Метаданные с конвенцией именования ограничений.

    Class Attributes:
        id (Mapped[int]): Первичный ключ типа BigInteger с автоинкрементом.

    Inheritance:
        AsyncAttrs: Добавляет поддержку асинхронного доступа к атрибутам отношений.
        DeclarativeBase: Базовый класс для declarative модели SQLAlchemy.
    """

    __abstract__ = True

    metadata = MetaData(
        naming_convention={
            'ix': 'ix_%(column_0_label)s',
            'uq': 'uq_%(table_name)s_%(column_0_N_name)s',
            'ck': 'ck_%(table_name)s_%(constraint_name)s',
            'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
            'pk': 'pk_%(table_name)s',
        },
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: N805
        """
        Автоматически генерирует имя таблицы на основе имени класса.

        Преобразует CamelCase в snake_case:
        - UserProfile → user_profile
        - APIEndpoint → api_endpoint
        - UserAPI → user_api

        Args:
            cls: Класс модели.

        Returns:
            str: Имя таблицы в snake_case.
        """
        name = cls.__name__
        name = re.sub(r'([A-Z]+)(?=[A-Z][a-z]|\d|\W|$)|\B([A-Z])', r'_\1\2', name)
        name = name.lower()
        name = name.lstrip('_')
        name = re.sub(r'_{2,}', '_', name)
        return name

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)


engine = create_async_engine(
    url=settings.db.url,
    echo=settings.db.ECHO,
    pool_size=settings.db.POOL_SIZE,
    max_overflow=settings.db.MAX_OVERFLOW,
    pool_timeout=settings.db.POOL_TIMEOUT,
    pool_pre_ping=settings.db.POOL_PRE_PING,
    pool_recycle=settings.db.POOL_RECYCLE,
)
"""
Асинхронный движок SQLAlchemy для подключения к базе данных.

Конфигурируется на основе настроек из app.core.config.settings.db.

Example URL:
    postgresql+asyncpg://user:password@localhost:5432/database
"""

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
"""
Фабрика асинхронных сессий SQLAlchemy.

Создает и конфигурирует сессии для работы с базой данных.
Использует движок engine для установки соединений.

Parameters:
    engine: Асинхронный движок SQLAlchemy.
    class_: Класс сессии (AsyncSession для асинхронной работы).
    expire_on_commit (bool): Если False, объекты не истекают после коммита,
                            что позволяет продолжать работу с ними.
"""


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения асинхронной сессии базы данных.

    Создает и предоставляет сессию для использования в FastAPI dependencies.
    Гарантирует корректное закрытие сессии после завершения работы.

    Yields:
        AsyncSession: Асинхронная сессия SQLAlchemy.

    Returns:
        AsyncGenerator[AsyncSession, None]: Генератор асинхронных сессий.
    """
    async with AsyncSessionLocal() as async_session:
        yield async_session
