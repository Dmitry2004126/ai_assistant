from http import HTTPStatus
from typing import Any, Generic, Sequence, Type, TypeVar

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import ColumnElement
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import Base

PydanticSchema = TypeVar('PydanticSchema', bound=BaseModel)
SQLAlchemyModel = TypeVar('SQLAlchemyModel', bound=Base)


class CRUDBase(Generic[SQLAlchemyModel]):
    """При наследовании от базового класса нужно указывать в квадратных скобках модель
    с которой будет работать новый класс, и которая будет хранится в `self.model`.

    Example:
    ```
    # Наследование будет не таким
    class CRUDUser(CRUDBase):
    # а таким:
    class CRUDUser(CRUDBase[User]):
    ```
    """

    def __init__(self, model: Type[SQLAlchemyModel]) -> None:
        self.model = model

    async def get_multi(
        self,
        async_session: AsyncSession,
        order_by: tuple[ColumnElement[Any], ...] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        **filter_by: Any,
    ) -> Sequence[SQLAlchemyModel]:
        """Получает список элементов с простыми условиями.

        Args:
            async_session (AsyncSession): Асинхронная сессия
            order_by (tuple[ColumnElement, ...] | None, optional): Кортеж столбцов для
                сортировки. Используйте .asc() для сортировки по возрастанию и .desc()
                для убывания. По умолчанию None.
            limit (int | None): Максимальное количество записей
            offset (int | None): Смещение для пагинации
            **filter_by (Any): Именованные аргументы для фильтрации в формате
                поле=значение

        Returns:
            Sequence[SQLAlchemyModel]: Список найденных объектов или [], если объекты не
                найдены

        Example:
        ```
            # Все записи
            users = await crud.get_multi(session)

            # С фильтрацией
            active_users = await crud.get_multi(session, is_active=True)

            # Сортировка по одному полю по возрастанию
            users = await crud.get_multi(
                session,
                order_by=(User.created_at.asc(),)
            )

            # Сортировка по нескольким полям с фильтрацией
            users = await crud.get_multi(
                session,
                order_by=(User.role.asc(), User.created_at.desc()),
                is_active=True,
                role='admin'
            )

            # С пагинацией
            users = await crud.get_multi(
                session,
                limit=10,
                offset=20,
                is_active=True
            )
        ```
        """
        query = select(self.model).filter_by(**filter_by)

        if order_by:
            query = query.order_by(*order_by)

        if offset is not None:
            query = query.offset(offset)

        if limit is not None:
            query = query.limit(limit)

        db_objs = await async_session.execute(query)
        return db_objs.scalars().unique().all()

    async def get_multi_or_404(
        self,
        async_session: AsyncSession,
        order_by: tuple[ColumnElement[Any], ...] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        *,
        _detail: str | None = None,
        **filter_by: Any,
    ) -> Sequence[SQLAlchemyModel]:
        """Получает список элементов с простыми условиями или возвращает 404 ошибку.

        Args:
            async_session (AsyncSession): Асинхронная сессия
            order_by (tuple[ColumnElement, ...] | None, optional): Кортеж столбцов для
                сортировки
            limit (int | None): Максимальное количество записей
            offset (int | None): Смещение для пагинации
            _detail (str | None): Кастомное сообщение об ошибке
            **filter_by (Any): Именованные аргументы для фильтрации

        Returns:
            Sequence[SQLAlchemyModel]: Список найденных объектов (не пустой)

        Raises:
            HTTPException: 404 если объекты не найдены

        Example:
        ```
            # Получить всех админов (ошибка если нет ни одного)
            admins = await crud.get_multi_or_404(session, role="admin")

            # С кастомной ошибкой
            active_users = await crud.get_multi_or_404(
                session,
                _detail="Нет активных пользователей",
                is_active=True
            )

            # С сортировкой и лимитом
            recent_posts = await crud.get_multi_or_404(
                session,
                order_by=(Post.created_at.desc(),),
                limit=5,
                published=True
            )
        ```
        """
        db_objs = await self.get_multi(
            async_session, order_by=order_by, limit=limit, offset=offset, **filter_by
        )

        if not db_objs:
            if _detail:
                error_detail = _detail
            else:
                # Формируем красивое сообщение об ошибке
                if filter_by:
                    filter_parts = [f"{k}={v}" for k, v in filter_by.items()]
                    filter_str = ', '.join(filter_parts)
                    error_detail = f"No {self.model.__name__} found with {filter_str}"
                else:
                    error_detail = f"No {self.model.__name__} found"

            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=error_detail,
            )

        return db_objs

    async def create(
        self,
        async_session: AsyncSession,
        obj_in: PydanticSchema,
        user_id: int | None = None,
    ) -> SQLAlchemyModel:
        """Создает новый объект.

        Args:
            async_session (AsyncSession): Асинхронная сессия
            obj_in (PydanticSchema): Pydantic объект, который будет создан.
            user_id (int | None, optional): ИД пользователя, к которому будет привязан
                объект. По умолчанию None.

        Returns:
            SQLAlchemyModel: Созданный объект
        """
        obj_in_data = obj_in.model_dump()
        if user_id is not None:
            obj_in_data['user_id'] = user_id
        db_obj = self.model(**obj_in_data)
        async_session.add(db_obj)
        await async_session.flush()
        await async_session.refresh(db_obj)
        return db_obj
