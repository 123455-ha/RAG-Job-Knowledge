from fastapi import APIRouter
from backend.app.schemas.chat import ChatRequest
from backend.app.services.rag_service import RagService

router = APIRouter(prefix="/api/v1", tags=["chat"])
service = RagService()


@router.post("/chat")
def chat(request: ChatRequest) -> dict:
    return {
        "code": 0,
        "message": "success",
        "data": service.chat(request.question, request.conversation_id),
    }
