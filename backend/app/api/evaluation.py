from fastapi import APIRouter
from backend.app.schemas.evaluation import EvaluationRequest
from backend.app.services.evaluation_service import EvaluationService

router = APIRouter(prefix="/api/v1/evaluation", tags=["evaluation"])
service = EvaluationService()


@router.post("/run")
def run_evaluation(request: EvaluationRequest) -> dict:
    return {
        "code": 0,
        "message": "success",
        "data": service.run(request.questions_path),
    }
