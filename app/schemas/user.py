from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    """
    Модель для чтения данных пользователя.
    """
    pass


class UserCreate(schemas.BaseUserCreate):
    """
    Модель для создания нового пользователя.
    """
    pass
