from backend.app.rag.chunker import chunk_documents


def test_chunker_metadata():
    chunks = chunk_documents([{"content": "hello " * 200, "page": 2}], "doc1", "a.md")
    assert len(chunks) > 1
    assert chunks[0]["document_id"] == "doc1"
    assert chunks[0]["page"] == 2
