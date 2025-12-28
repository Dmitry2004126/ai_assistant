from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

from app.core.config import settings
from app.models.user import User

bearer_transport = BearerTransport(tokenUrl='/auth/login')


def get_access_jwt_strategy() -> JWTStrategy[User, int]:
    """
    Фабрика для создания стратегии JWT для access токенов.

    Создает и возвращает конфигурацию JWT стратегии, используемую
    для генерации и валидации access токенов аутентификации.

    Returns:
        JWTStrategy[User, int]: Стратегия JWT с настройками из конфигурации.

    Configuration:
        - secret: Секретный ключ для подписи токенов
        - lifetime_seconds: Время жизни access токена
        - token_audience: Аудитория токена (список допустимых получателей)
    """
    return JWTStrategy(
        secret=settings.jwt.SECRET,
        lifetime_seconds=settings.jwt.ACCESS_TOKEN_LIFETIME_SECONDS,
        token_audience=['fastapi-users:auth'],
    )


auth_backend = AuthenticationBackend(
    name='jwt',
    transport=bearer_transport,
    get_strategy=get_access_jwt_strategy,
)
