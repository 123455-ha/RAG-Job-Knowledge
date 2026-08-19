class BaseReranker:
    def rerank(self, query: str, results: list[dict]) -> list[dict]:
        return results


class ScoreReranker(BaseReranker):
    def rerank(self, query: str, results: list[dict]) -> list[dict]:
        terms = set(query.lower().split())
        for row in results:
            overlap = sum(t in row["content"].lower() for t in terms)
            row["score"] = min(1.0, max(0.0, row.get("score", 0.0) + overlap * 0.02))
        return sorted(results, key=lambda x: x["score"], reverse=True)
