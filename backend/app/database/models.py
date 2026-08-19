from dataclasses import dataclass


@dataclass
class Document:
    document_id: str
    file_name: str
    file_type: str
    file_path: str
    uploaded_at: str
    chunk_count: int
    status: str
