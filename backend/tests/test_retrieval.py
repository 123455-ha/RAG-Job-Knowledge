from backend.app.vectorstore.qdrant import store


def test_retrieval():
    store._items.clear()
    store.upsert(
        [
            {
                "chunk_id": "c1",
                "document_id": "d1",
                "file_name": "x.md",
                "content": "RAG uses retrieval and generation",
                "page": None,
                "source": "x.md",
                "chunk_index": 0,
            }
        ]
    )
    rows = store.search("retrieval", 1)
    assert rows and rows[0]["chunk_id"] == "c1"
