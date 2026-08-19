from pydantic import BaseModel, Field
from backend.app.schemas.chat import Source


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    top_k: int | None = Field(default=None, ge=1, le=20)


class SearchData(BaseModel):
    results: list[Source]
