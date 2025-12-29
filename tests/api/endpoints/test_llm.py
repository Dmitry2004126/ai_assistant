import pytest
from openai import APIError
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.llm import ask_llm


# Тест 1: Проверка mock-режима
@pytest.mark.asyncio
async def test_ask_llm_mock_mode():
    """Тестирование работы функции в mock-режиме"""
    mock_async_session = AsyncMock(spec=AsyncSession)
    mock_user = MagicMock()
    mock_user.id = 1

    question_mock = MagicMock()
    question_mock.question = "Тестовый вопрос"

    result = await ask_llm(
        mock_mode=True,
        question=question_mock,
        async_session=mock_async_session,
        current_user=mock_user
    )

    assert result.message == "Это тестовый ответ, так как включен Mock-режим"
    mock_async_session.assert_not_called()


# Тест 2: Успешный вызов LLM API
@pytest.mark.asyncio
@patch('app.core.config.settings.openrouter.key', 'test_key')
@patch('app.services.llm.AsyncOpenAI')
async def test_ask_llm_success(mock_openai_class):
    """Тестирование успешного запроса к реальному API"""
    mock_async_session = AsyncMock(spec=AsyncSession)
    mock_user = MagicMock()
    mock_user.id = 1

    question_mock = MagicMock()
    question_mock.question = "Как дела?"

    with patch('app.crud.msg.msg_crud.create', new_callable=AsyncMock) as mock_create:
        mock_openai_instance = AsyncMock()
        mock_openai_class.return_value = mock_openai_instance

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Всё отлично, спасибо!"))
        ]
        mock_openai_instance.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await ask_llm(
            mock_mode=False,
            question=question_mock,
            async_session=mock_async_session,
            current_user=mock_user
        )

    assert result.message == "Всё отлично, спасибо!"
    assert mock_create.call_count == 2
    mock_async_session.commit.assert_awaited_once()


# Тест 3: Обработка ошибок от API
@pytest.mark.asyncio
@patch('app.core.config.settings.openrouter.key', 'test_key')
@patch('app.services.llm.AsyncOpenAI')
async def test_ask_llm_api_exception(mock_openai_class):
    """Тестирование обработки ошибок от внешнего API"""
    mock_async_session = AsyncMock(spec=AsyncSession)
    mock_user = MagicMock()
    mock_user.id = 1

    question_mock = MagicMock()
    question_mock.question = "Как дела?"

    mock_openai_instance = AsyncMock()
    mock_openai_class.return_value = mock_openai_instance

    mock_response = MagicMock()
    mock_response.status_code = 429

    api_error = APIError(
        message="Rate limit exceeded",
        request=MagicMock(),
        body={"error": {"message": "Rate limit exceeded"}}
    )
    api_error.status_code = 429

    mock_openai_instance.chat.completions.create = AsyncMock(side_effect=api_error)

    with pytest.raises(HTTPException) as exc_info:
        await ask_llm(
            mock_mode=False,
            question=question_mock,
            async_session=mock_async_session,
            current_user=mock_user
        )

    assert exc_info.value.status_code == 429
    assert "Rate limit exceeded" in str(exc_info.value.detail) or "API Error" in str(exc_info.value.detail)
