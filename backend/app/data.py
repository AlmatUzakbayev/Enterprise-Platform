from pydantic import BaseModel
from datetime import datetime

class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    language: str
    summary: str | None
    chunk_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    question: str
    document_id: int | None = None
    telegram_user_id: int

class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    tokens_used: int
    retrieval_score: float | None = None

class MessageResponse(BaseModel):
    role: str
    content: str
    created_at: datetime


    class Config:
        from_attributes = True