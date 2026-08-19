import threading
import logging
from uuid import NAMESPACE_URL, uuid5
from typing import Any
from backend.app.services.embedding_service import (
    BaseEmbeddingService,
    LocalEmbeddingService,
    OpenAIEmbeddingService,
    tokenize,
)
from backend.app.core.config import get_settings

logger = logging.getLogger(__name__)


class LocalVectorStore:
    def __init__(self, embedding: BaseEmbeddingService | None = None) -> None:
        self.embedding = embedding or LocalEmbeddingService()
        self._items: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()

    def upsert(self, chunks: list[dict[str, Any]]) -> None:
        vectors = self.embedding.embed_many([c["content"] for c in chunks])
        with self._lock:
            for chunk, vector in zip(chunks, vectors):
                self._items[chunk["chunk_id"]] = {"vector": vector, "payload": chunk}

    def delete_document(self, document_id: str) -> None:
        with self._lock:
            self._items = {
                k: v
                for k, v in self._items.items()
                if v["payload"].get("document_id") != document_id
            }

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        q = self.embedding.embed(query)
        rows = []
        query_tokens = set(tokenize(query))
        for item in self._items.values():
            vector = item["vector"]
            cosine = sum(a * b for a, b in zip(q, vector))
            content_tokens = set(tokenize(item["payload"]["content"]))
            keyword = len(query_tokens & content_tokens) / max(len(query_tokens), 1)
            rows.append(
                {**item["payload"], "vector_score": cosine, "keyword_score": keyword}
            )
        for row in rows:
            row["score"] = 0.7 * row["vector_score"] + 0.3 * row["keyword_score"]
        relevant = [row for row in rows if row["score"] >= 0.08]
        return sorted(relevant, key=lambda x: x["score"], reverse=True)[:top_k]


class QdrantVectorStore(LocalVectorStore):
    """Qdrant-backed index with an in-process fallback for offline development."""

    def __init__(self, embedding: BaseEmbeddingService | None = None) -> None:
        settings = get_settings()
        selected = embedding or (
            OpenAIEmbeddingService(
                settings.embedding_api_key,
                settings.embedding_base_url,
                settings.embedding_model,
            )
            if settings.embedding_api_key and settings.embedding_base_url
            else LocalEmbeddingService()
        )
        super().__init__(selected)
        self.client = None
        self.collection = get_settings().qdrant_collection
        try:
            from qdrant_client import QdrantClient

            self.client = QdrantClient(
                url=get_settings().qdrant_url, timeout=1, check_compatibility=False
            )
        except ImportError:
            logger.info("qdrant-client unavailable; using local vector index")

    def _ensure_collection(self) -> None:
        if self.client is None:
            return
        from qdrant_client.models import Distance, VectorParams

        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                self.collection,
                vectors_config=VectorParams(
                    size=self.embedding.dimension, distance=Distance.COSINE
                ),
            )

    def upsert(self, chunks: list[dict[str, Any]]) -> None:
        super().upsert(chunks)
        if self.client is None or not chunks:
            return
        try:
            from qdrant_client.models import PointStruct

            self._ensure_collection()
            points = [
                PointStruct(
                    id=str(uuid5(NAMESPACE_URL, c["chunk_id"])),
                    vector=self._items[c["chunk_id"]]["vector"],
                    payload=c,
                )
                for c in chunks
            ]
            self.client.upsert(
                collection_name=self.collection, points=points, wait=True
            )
        except Exception as exc:
            logger.warning(
                "Qdrant unavailable; local index remains active (%s)",
                type(exc).__name__,
            )
            self.client = None

    def delete_document(self, document_id: str) -> None:
        super().delete_document(document_id)
        if self.client is None:
            return
        try:
            from qdrant_client.models import FieldCondition, Filter, MatchValue

            self.client.delete(
                collection_name=self.collection,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="document_id", match=MatchValue(value=document_id)
                        )
                    ]
                ),
                wait=True,
            )
        except Exception as exc:
            logger.warning("Qdrant delete skipped (%s)", type(exc).__name__)


store = QdrantVectorStore()
