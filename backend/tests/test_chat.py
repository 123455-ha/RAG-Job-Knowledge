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
