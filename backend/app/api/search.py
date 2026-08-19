from fastapi import APIRouter
from backend.app.schemas.search import SearchRequest
from backend.app.services.retrieval_service import RetrievalService

router = APIRouter(prefix="/api/v1", tags=["search"])
service = RetrievalService()


@router.post("/search")
def search(request: SearchRequest) -> dict:
    rows = service.retrieve(request.query, request.top_k)
    results = [
        {
            "document_id": r["document_id"],
            "file_name": r["file_name"],
            "page": r.get("page"),
            "chunk_id": r["chunk_id"],
            "score": round(float(r["score"]), 4),
            "snippet": r["content"][:300],
        }
        for r in rows
    ]
    return {"code": 0, "message": "success", "data": {"results": results}}
