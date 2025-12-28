from fastapi import Request, Response
from fastapi_users import BaseUserManager, IntegerIDMixin


from app.models.user import User


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """
    Менеджер пользователей для приложения.

    Наследует от BaseUserManager и IntegerIDMixin, предоставляя:
    - CRUD операции над пользователями
    - Управление паролями и их валидацию
    - Интеграцию с FastAPI-Users

    Attributes:
        Inherits all attributes from BaseUserManager and IntegerIDMixin.

    Methods:
        on_after_register: Хук, вызываемый после успешной регистрации пользователя.
        on_after_login: Хук, вызываемый после успешного входа пользователя.
    """
    async def on_after_register(
            self, user: User, request: Request | None = None
    ) -> None:
        pass

    async def on_after_login(
            self,
            user: User,
            request: Request | None = None,
            response: Response | None = None,
    ) -> None:
        pass
