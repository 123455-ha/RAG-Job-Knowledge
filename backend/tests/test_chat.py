def test_chat(client):
    client.post(
        "/api/v1/documents/upload",
        files={
            "file": (
                "rag.txt",
                b"RAG combines retrieval with generation.",
                "text/plain",
            )
        },
    )
    response = client.post("/api/v1/chat", json={"question": "What is RAG?"})
    assert response.status_code == 200
    assert "answer" in response.json()["data"]


def test_web_fallback(client, monkeypatch):
    from backend.app.api.chat import service

    monkeypatch.setattr(service.retrieval, "retrieve", lambda _: [])
    monkeypatch.setattr(
        service.web_search,
        "search",
        lambda _: [
            {
                "document_id": "web",
                "file_name": "Example",
                "page": None,
                "chunk_id": "web_1",
                "score": 0.2,
                "snippet": "A web result",
                "content": "Example\nA web result",
                "source_type": "web",
                "url": "https://example.com",
            }
        ],
    )
    response = client.post(
        "/api/v1/chat", json={"question": "What is an obscure topic?"}
    )
    data = response.json()["data"]
    assert "知识库中没有找到相关资料" in data["answer"]
    assert data["sources"][0]["source_type"] == "web"
    assert data["sources"][0]["url"] == "https://example.com"
