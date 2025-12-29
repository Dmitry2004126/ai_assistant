from datetime import datetime

from pydantic import BaseModel

from app.core.docs.llm import LLMMsgBodyDocs


class LLMMsgBody(BaseModel, LLMMsgBodyDocs):
    question: str


class LLMResponse(BaseModel):
    message: str


class MsgSchema(BaseModel):
    message: str
    question: bool


class MsgResponse(MsgSchema):
    date: datetime
    user_id: int

