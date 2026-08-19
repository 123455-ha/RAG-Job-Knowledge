from datetime import datetime, timezone
from pathlib import Path
from backend.app.database.database import execute
from backend.app.rag.chunker import chunk_documents
from backend.app.vectorstore.qdrant import store
from backend.app.loaders.loader import load_file
from backend.app.utils.id_utils import new_id


class DocumentService:
    def rebuild_index(self) -> int:
        indexed = 0
        for row in execute("SELECT document_id,file_name,file_path FROM documents"):
            try:
                chunks = chunk_documents(
                    load_file(row["file_path"]), row["document_id"], row["file_name"]
                )
                store.upsert(chunks)
                indexed += len(chunks)
            except (OSError, ValueError):
                continue
        return indexed

    def create(self, file_name: str, file_type: str, path: str) -> dict:
        document_id = new_id("doc_")
        pages = load_file(path)
        chunks = chunk_documents(pages, document_id, file_name)
        store.upsert(chunks)
        uploaded_at = datetime.now(timezone.utc).isoformat()
        execute(
            "INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                document_id,
                file_name,
                file_type,
                path,
                uploaded_at,
                len(chunks),
                "ready",
                None,
            ),
        )
        return {
            "document_id": document_id,
            "file_name": file_name,
            "chunks": len(chunks),
        }

    def list(self) -> list[dict]:
        return [
            dict(row)
            for row in execute(
                "SELECT document_id,file_name,file_type,uploaded_at,chunk_count,status FROM documents ORDER BY uploaded_at DESC"
            )
        ]

    def get(self, document_id: str) -> dict | None:
        rows = execute(
            "SELECT document_id,file_name,file_type,uploaded_at,chunk_count,status FROM documents WHERE document_id=?",
            (document_id,),
        )
        if not rows:
            return None
        doc = dict(rows[0])
        chunks = []
        for item in store._items.values():
            payload = item["payload"]
            if payload.get("document_id") == document_id:
                chunks.append(
                    {
                        k: payload.get(k)
                        for k in (
                            "chunk_id",
                            "chunk_index",
                            "content",
                            "page",
                            "source",
                        )
                    }
                )
        doc["chunks"] = sorted(chunks, key=lambda x: x["chunk_index"])
        return doc

    def delete(self, document_id: str) -> bool:
        rows = execute(
            "SELECT file_path FROM documents WHERE document_id=?", (document_id,)
        )
        if not rows:
            return False
        store.delete_document(document_id)
        execute("DELETE FROM documents WHERE document_id=?", (document_id,))
        try:
            Path(rows[0]["file_path"]).unlink(missing_ok=True)
        except OSError:
            pass
        return True
