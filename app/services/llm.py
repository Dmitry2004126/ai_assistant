import asyncio

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.core.config import settings
from app.crud.msg import msg_crud
from app.models import User
from app.schemas.llm import LLMResponse, MsgSchema, LLMMsgBody


async def ask_llm(
    mock_mode: bool,
    question: LLMMsgBody,
    async_session: AsyncSession,
    current_user: User
) -> LLMResponse:
    """
        Асинхронно обрабатывает запрос к языковой модели (LLM).

        Сохраняет как запрос пользователя, так и ответ LLM в базу данных.

        Args:
            mock_mode: Флаг режима тестирования. Если True, возвращает mock-ответ.
            question: Объект с вопросом пользователя (LLMMsgBody).
            async_session: Асинхронная сессия SQLAlchemy для работы с БД.
            current_user: Текущий аутентифицированный пользователь.

        Returns:
            LLMResponse: Объект с ответом от языковой модели.
        """
    try:
        if mock_mode or settings.openrouter.key is None:
            await asyncio.sleep(1.5)
            return LLMResponse(message='Это тестовый ответ, так как включен Mock-режим')

        client = AsyncOpenAI(
            base_url=settings.openrouter.base_url,
            api_key=settings.openrouter.key,
        )
        await msg_crud.create(
            async_session=async_session,
            obj_in=MsgSchema(message=question.question, question=True),
            user_id=current_user.id
        )

        response = await client.chat.completions.create(
            model="nex-agi/deepseek-v3.1-nex-n1:free",
            messages=[
                {"role": "user", "content": question.question}
            ]
        )
        await msg_crud.create(
            async_session=async_session,
            obj_in=MsgSchema(message=response.choices[0].message.content, question=False),
            user_id=current_user.id
        )
        await async_session.commit()
        return LLMResponse(message=response.choices[0].message.content)
    except Exception as e:
        status = getattr(e, 'status_code', 500)
        raise HTTPException(
            status_code=status,
            detail={
                "message": str(e),
            }
        )
