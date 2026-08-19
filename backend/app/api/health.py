from fastapi import APIRouter
from backend.app.core.config import get_settings

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {
        "code": 0,
        "message": "success",
        "data": {
            "status": "ok",
            "llm_mode": "external" if get_settings().openai_api_key else "local-demo",
            "llm_model": get_settings().llm_model,
            "embedding_mode": (
                "external"
                if get_settings().embedding_api_key
                and get_settings().embedding_base_url
                else "local-demo"
            ),
        },
    }
