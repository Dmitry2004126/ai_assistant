from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
if TYPE_CHECKING:
    from app.models.user import User


class Msg(Base):
    message: Mapped[str]
    date: Mapped[datetime] = mapped_column(default=datetime.now)
    question: Mapped[bool] = mapped_column(default=True)

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    user: Mapped['User'] = relationship(back_populates='msgs')
