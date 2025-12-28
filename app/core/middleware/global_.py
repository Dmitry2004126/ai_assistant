import time
import traceback
from typing import Any
from uuid import uuid4

from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.logs.logs import info_logger, error_logger, debug_logger
from app.core.enums import LogLevel


class TraceLogger:
    """
    Логгер с поддержкой request ID и уровней логирования.

    Этот класс предоставляет структурированное логирование с привязкой
    к конкретному HTTP-запросу через уникальный request ID. Поддерживает
    различные уровни логирования (DEBUG, INFO, ERROR) с фильтрацией
    по минимальному пороговому уровню.

    Attributes:
        request_id (int | str): Уникальный идентификатор запроса.
        level (LogLevel): Минимальный уровень логирования для фильтрации.

    Methods:
        debug: Логирует сообщение на уровне DEBUG.
        info: Логирует сообщение на уровне INFO.
        error: Логирует сообщение на уровне ERROR.
        get_request_id: Статический метод для получения request ID из заголовков.

    Example:
        ```python
        logger = TraceLogger(request_id="12345", level=LogLevel.INFO)
        logger.info("Запрос получен")
        logger.debug("Детальная информация")  # Не будет залогировано, если уровень INFO
        ```
    """

    def __init__(self, request_id: int | str, level: LogLevel) -> None:
        """
        Инициализирует TraceLogger.

        Args:
            request_id: Уникальный идентификатор запроса.
            level: Минимальный уровень логирования. Сообщения с уровнем ниже
                   этого порога не будут залогированы.
        """
        self.request_id = request_id
        self.level = level

    def _should_log(self, message_level: LogLevel) -> bool:
        """
        Проверяет, нужно ли логировать сообщение данного уровня.

        Сравнивает приоритет уровня сообщения с минимальным порогом
        логирования экземпляра.

        Args:
            message_level: Уровень логирования сообщения.

        Returns:
            bool: True если сообщение должно быть залогировано,
                  False в противном случае.

        Note:
            Приоритеты уровней: DEBUG (10) < INFO (20) < ERROR (30).
            Сообщение логируется, если его приоритет >= пороговому значению.
        """
        level_priority = {
            LogLevel.DEBUG: 10,
            LogLevel.INFO: 20,
            LogLevel.ERROR: 30
        }
        return level_priority[message_level] >= level_priority[self.level]

    def debug(self, string: str) -> None:
        """
        Логирует сообщение на уровне DEBUG.

        Args:
            string: Текст сообщения для логирования.

        Note:
            Сообщение будет залогировано только если уровень экземпляра
            установлен в DEBUG или ниже.
        """
        if self._should_log(LogLevel.DEBUG):
            debug_logger.debug(self._create_string(string))

    def info(self, string: str) -> None:
        """
        Логирует сообщение на уровне INFO.

        Args:
            string: Текст сообщения для логирования.

        Note:
            Сообщение будет залогировано только если уровень экземпляра
            установлен в INFO или ниже.
        """
        if self._should_log(LogLevel.INFO):
            info_logger.info(self._create_string(string))

    def error(self, string: str) -> None:
        """
        Логирует сообщение на уровне ERROR.

        Args:
            string: Текст сообщения для логирования.

        Note:
            Сообщение будет залогировано только если уровень экземпляра
            установлен в ERROR или ниже.
        """
        if self._should_log(LogLevel.ERROR):
            error_logger.error(self._create_string(string))

    def _create_string(self, string: str) -> str:
        """
        Форматирует строку для логирования с добавлением request ID.

        Args:
            string: Исходная строка сообщения.

        Returns:
            str: Отформатированная строка с префиксом request ID.

        Example:
            Вход: "Запрос получен"
            Выход: "[request_id=12345] Запрос получен"
        """
        return f"[request_id={self.request_id}] {string}"

    @staticmethod
    def get_request_id(request: Request) -> str:
        """
        Извлекает или генерирует уникальный идентификатор запроса.

        Args:
            request: Объект HTTP запроса FastAPI.

        Returns:
            str: Request ID из заголовка X-Request-ID, если он присутствует,
                 иначе сгенерированный UUID4.
        """
        if 'X-Request-ID' in request.headers:
            return request.headers['X-Request-ID']
        return str(uuid4())


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware для структурированного логирования HTTP запросов и ответов.

    Перехватывает все HTTP запросы, добавляет request ID, логирует детали
    запросов и ответов, измеряет время выполнения и обрабатывает исключения.
    Поддерживает исключение определенных эндпоинтов из логирования.

    Inheritance:
        BaseHTTPMiddleware: Базовый класс middleware из Starlette.

    Environment Configuration:
        Уровень логирования берется из settings.app.LOG_LEVEL
    """

    async def __general_response(
            self,
            request: Request,
            call_next: Any,
            trace_logger: TraceLogger,
            body: str,
    ) -> Response:
        """
        Обрабатывает успешные запросы и логирует ответы.

        Выполняет запрос, логирует результат, перехватывает и логирует тело ответа,
        обрабатывает нестандартные статус-коды.

        Args:
            request: Объект HTTP запроса.
            call_next: Функция для вызова следующего middleware/обработчика.
            trace_logger: Экземпляр логгера для текущего запроса.
            body: Декодированное тело запроса.

        Returns:
            Response: HTTP ответ с сохраненным телом.
        """
        response = await call_next(request)

        trace_logger.info(f"Request completed: {request.method} {request.url}")
        trace_logger.info(f"Status code: {response.status_code}")

        response_body = b''
        async for chunk in response.body_iterator:
            response_body += chunk

        if response.status_code != 200 and response.status_code != 201:
            trace_logger.error(f"Request body: {body}")
            trace_logger.error(f"Response body: {response_body.decode()}")

        return Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

    async def __handle_http_exception(
            self, e: HTTPException, trace_logger: TraceLogger
    ) -> Response:
        """
        Обрабатывает HTTP исключения.

        Логирует детали HTTPException и возвращает структурированный ответ.

        Args:
            e: Пойманное HTTPException.
            trace_logger: Экземпляр логгера для текущего запроса.

        Returns:
            Response: JSON ответ с деталями ошибки и соответствующим статус-кодом.
        """
        trace_logger.error(f"HTTPException occurred: {str(e.detail)}")
        trace_logger.error(f"Traceback: {traceback.format_exc()}")
        return JSONResponse(status_code=e.status_code, content={'detail': e.detail})

    async def __handle_general_exception(
            self,
            e: Exception,
            request: Request,
            trace_logger: TraceLogger,
    ) -> Response:
        """
        Обрабатывает неожиданные исключения (серверные ошибки).

        Логирует детали необработанного исключения и возвращает ответ 500.

        Args:
            e: Пойманное исключение.
            request: Объект HTTP запроса, вызвавшего исключение.
            trace_logger: Экземпляр логгера для текущего запроса.

        Returns:
            Response: JSON ответ с общим сообщением об ошибке и статусом 500.
        """
        trace_logger.error(f"Exception occurred: {str(e)}")
        trace_logger.error(f"Traceback: {traceback.format_exc()}")
        trace_logger.error(f"Request failed: {request.method} {request.url}")

        return JSONResponse(
            status_code=500, content={'detail': 'Internal Server Error'}
        )

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """
        Основной метод middleware для обработки запросов.

        Перехватывает каждый запрос, добавляет логирование, измеряет время
        выполнения и обрабатывает исключения.

        Args:
            request: Объект HTTP запроса.
            call_next: Функция для вызова следующего middleware/обработчика.

        Returns:
            Response: HTTP ответ, возможно модифицированный middleware.
        """
        request_id = TraceLogger.get_request_id(request=request)
        level = settings.app.LOG_LEVEL
        trace_logger = TraceLogger(request_id=request_id, level=level)

        start_time = time.time()
        trace_logger.info(f"Incoming request: {request.method} {request.url}")
        body = await request.body()

        decoded_body = ''
        if body:
            try:
                decoded_body = body.decode('utf-8')
                trace_logger.info(f"Request body: {decoded_body}")
            except UnicodeDecodeError:
                trace_logger.info("Request body: {\n  'body': Объект в base64\n}")

        try:
            return await self.__general_response(
                request=request,
                call_next=call_next,
                trace_logger=trace_logger,
                body=decoded_body,
            )
        except HTTPException as e:
            return await self.__handle_http_exception(
                e=e, trace_logger=trace_logger
            )

        except Exception as e:
            return await self.__handle_general_exception(
                e=e, request=request, trace_logger=trace_logger
            )
        finally:
            process_time = time.time() - start_time
            trace_logger.info(f"Process time: {process_time:.4f} seconds")
