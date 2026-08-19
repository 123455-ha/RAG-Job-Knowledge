def test_upload_and_list(client):
    response = client.post(
        "/api/v1/documents/upload",
        files={
            "file": (
                "notes.md",
                b"# RAG\nRetrieval augmented generation",
                "text/markdown",
            )
        },
    )
    assert response.status_code == 200
    doc_id = response.json()["data"]["document_id"]
    assert client.get("/api/v1/documents").status_code == 200
    assert client.get(f"/api/v1/documents/{doc_id}").json()["data"]["chunk_count"] >= 1
    assert client.delete(f"/api/v1/documents/{doc_id}").status_code == 200


def test_reject_extension(client):
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("bad.exe", b"x", "application/octet-stream")},
    )
    assert response.status_code == 400
    assert response.json()["code"] == 4001
