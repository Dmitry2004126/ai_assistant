from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
if TYPE_CHECKING:
    from app.models.user import User


class Msg(Base):
    """
       Модель сообщений (Msg) в базе данных.

       Содержит информацию о вопросах пользователей и ответов LLM.

       Columns:
           id (int, PK): Уникальный ID сообщения
           message (text): Текст сообщения
           date (datetime): Дата/время создания
           question (bool): Флаг вопроса (True/False)
           user_id (int, FK): Ссылка на пользователя
    """
    message: Mapped[str]
    date: Mapped[datetime] = mapped_column(default=datetime.now)
    question: Mapped[bool] = mapped_column(default=True)

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    user: Mapped['User'] = relationship(back_populates='msgs')
