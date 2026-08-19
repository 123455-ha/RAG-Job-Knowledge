from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None


class Source(BaseModel):
    document_id: str
    file_name: str
    page: int | None = None
    chunk_id: str
    score: float
    snippet: str


class ChatData(BaseModel):
    answer: str
    sources: list[Source]
    retrieval_count: int
    latency_ms: int
    conversation_id: str
