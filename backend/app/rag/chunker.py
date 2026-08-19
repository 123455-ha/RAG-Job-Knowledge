from typing import Any
from backend.app.core.config import get_settings
from backend.app.utils.id_utils import new_id
from backend.app.utils.text_utils import clean_text


def chunk_documents(
    pages: list[dict[str, Any]], document_id: str, file_name: str
) -> list[dict[str, Any]]:
    settings = get_settings()
    chunks: list[dict[str, Any]] = []
    for page in pages:
        text = clean_text(str(page.get("content", "")))
        if not text:
            continue
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter

            parts = RecursiveCharacterTextSplitter(
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap,
                separators=["\n\n", "\n", "。", ". ", " ", ""],
            ).split_text(text)
        except ImportError:
            step = max(1, settings.chunk_size - settings.chunk_overlap)
            parts = [
                text[i : i + settings.chunk_size] for i in range(0, len(text), step)
            ]
        for index, content in enumerate(parts):
            chunks.append(
                {
                    "chunk_id": new_id("chunk_"),
                    "chunk_index": index,
                    "content": content.strip(),
                    "document_id": document_id,
                    "file_name": file_name,
                    "page": page.get("page"),
                    "source": file_name,
                }
            )
    return chunks
