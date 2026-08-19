from datetime import datetime
from pydantic import BaseModel


class DocumentOut(BaseModel):
    document_id: str
    file_name: str
    file_type: str
    uploaded_at: datetime
    chunk_count: int
    status: str


class ChunkOut(BaseModel):
    chunk_id: str
    chunk_index: int
    content: str
    page: int | None = None
    source: str


class DocumentDetail(DocumentOut):
    chunks: list[ChunkOut]


class UploadData(BaseModel):
    document_id: str
    file_name: str
    chunks: int
