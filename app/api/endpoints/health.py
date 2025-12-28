from fastapi import APIRouter

router = APIRouter(prefix='', tags=['root'])


@router.get('/')
def read_root() -> bool:
    """
    Проверка работоспособности сервиса (health check).

    Returns:
        bool: Всегда возвращает True, что означает, что сервис работает
    """
    return True
