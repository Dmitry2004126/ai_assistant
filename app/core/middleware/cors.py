from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def add_cors_middleware(app: FastAPI) -> None:
    """
    Добавляет CORS middleware к FastAPI приложению.

    Args:
        app (FastAPI): Экземпляр FastAPI приложения.

    Configuration:
        - allow_origins: ['*'] - Разрешает запросы с любых источников
        - allow_credentials: True - Разрешает отправку учетных данных
        - allow_methods: ['*'] - Разрешает все HTTP методы
        - allow_headers: ['*'] - Разрешает все заголовки
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
