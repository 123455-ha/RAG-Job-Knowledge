from backend.app.vectorstore.qdrant import store


def retrieve(query: str, top_k: int) -> list[dict]:
    return store.search(query, top_k)
