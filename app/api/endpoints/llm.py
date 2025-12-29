from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.docs.llm import LLM10MsgsBodyDocs
from app.core.auth.users import current_user
from app.core.db import get_async_session
from app.crud.msg import msg_crud
from app.models import Msg
from app.models.user import User
from app.schemas.llm import LLMMsgBody, LLMResponse, MsgResponse
from app.services.llm import ask_llm


router = APIRouter(prefix='/llm', tags=['llm'])\



@router.post(
    '/msg',
    summary='Новый запрос к LLM',
    description=LLMMsgBody.Config.docstring,
)
async def add_msg(
    question: LLMMsgBody = Body(
        ..., example=LLMMsgBody.Config.json_schema_extra['example']
    ),
    mock_mode: bool = False,
    current_user: User = Depends(current_user),
    async_session: AsyncSession = Depends(get_async_session),
) -> LLMResponse:
    result = await ask_llm(
        mock_mode=mock_mode,
        question=question,
        current_user=current_user,
        async_session=async_session
    )
    return result


@router.get(
    '/ten_msgs',
    summary='Получить последние 10 сообщения',
    description=LLM10MsgsBodyDocs.Config.docstring,
)
async def get_ten_msgs(
    async_session: AsyncSession = Depends(get_async_session),
) -> list[MsgResponse]:
    result = await msg_crud.get_multi_or_404(
        async_session=async_session,
        order_by=(Msg.date.desc(),),
        limit=10
    )
    return result
