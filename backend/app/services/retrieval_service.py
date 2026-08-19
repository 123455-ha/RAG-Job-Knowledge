from backend.app.core.config import get_settings
from backend.app.rag.hybrid_retriever import hybrid_search
from backend.app.services.rerank_service import RerankService


class RetrievalService:
    def __init__(self) -> None:
        self.reranker = RerankService()

    def retrieve(self, query: str, top_k: int | None = None) -> list[dict]:
        results = hybrid_search(query, top_k or get_settings().top_k)
        return self.reranker.rerank(query, results)
