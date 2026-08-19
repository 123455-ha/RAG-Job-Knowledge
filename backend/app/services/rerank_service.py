from backend.app.rag.reranker import ScoreReranker


class RerankService:
    def __init__(self) -> None:
        self.reranker = ScoreReranker()

    def rerank(self, query: str, results: list[dict]) -> list[dict]:
        return self.reranker.rerank(query, results)
