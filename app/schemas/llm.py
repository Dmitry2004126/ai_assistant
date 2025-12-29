from datetime import datetime

from pydantic import BaseModel

from app.core.docs.llm import LLMMsgBodyDocs


class LLMMsgBody(BaseModel, LLMMsgBodyDocs):
    """
    Модель запроса для взаимодействия с Large Language Model.

    Attributes:
        question: Текст вопроса пользователя к языковой модели.

    Example:
        >>> request = LLMMsgBody(question="Что такое ИИ?")
        >>> request.question
        'Что такое ИИ?'
    """
    question: str


class LLMResponse(BaseModel):
    """
       Модель ответа от Large Language Model.

       Attributes:
           message: Ответ, сгенерированный языковой моделью.

       Example:
           >>> response = LLMResponse(message="Искусственный интеллект - это...")
           >>> response.message
           'Искусственный интеллект - это...'
       """
    message: str


class MsgSchema(BaseModel):
    """
       Базовая модель сообщения.

       Attributes:
           message: Текст сообщения.
           question: Флаг, указывающий, является ли сообщение вопросом.

       Example:
           >>> msg = MsgSchema(message="Привет", question=False)
           >>> msg.message
           'Привет'
           >>> msg.question
           False
       """
    message: str
    question: bool


class MsgResponse(MsgSchema):
    """
        Расширенная модель сообщения с метаданными.

        Наследует все поля от MsgSchema и добавляет метаданные сообщения.

        Attributes:
            message: Текст сообщения (унаследовано).
            question: Флаг вопроса (унаследовано).
            date: Дата и время создания сообщения.
            user_id: Идентификатор пользователя, отправившего сообщение.

        Example:
            >>> from datetime import datetime
            >>> response = MsgResponse(
            ...     message="2+2=?",
            ...     question=True,
            ...     date=datetime.now(),
            ...     user_id=123
            ... )
            >>> response.user_id
            123
        """
    date: datetime
    user_id: int

