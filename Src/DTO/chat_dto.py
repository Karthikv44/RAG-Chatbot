from pydantic import BaseModel, Field
from typing import Any


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    conversation_id: str | None = None  # None = start new conversation


class CitationSchema(BaseModel):
    source: str
    page: int | None = None


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    citations: list[CitationSchema]


class ConversationResponse(BaseModel):
    id: str
    title: str | None
    created_at: str


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    sources: list[Any] | None
    created_at: str
