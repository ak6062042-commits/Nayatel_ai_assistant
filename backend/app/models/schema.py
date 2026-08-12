from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    message: str = Field(..., min_length = 1, description = "user's message")
    session_id: str = Field(..., min_length = 1, description = "unique id for chat session")

class Source(BaseModel):
    title: str
    page: Optional[int] = None

class ChatResponse(BaseModel):
    answer: str
    source: list[Source] = Field(default_factory = list)

class Health(BaseModel):
    status: str
    