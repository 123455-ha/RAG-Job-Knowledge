from backend.app.rag.retriever import retrieve


def hybrid_search(query: str, top_k: int) -> list[dict]:
    return retrieve(query, top_k)
