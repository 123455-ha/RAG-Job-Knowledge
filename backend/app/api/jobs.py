from fastapi import APIRouter
from backend.app.schemas.job import (
    JobAnalyzeRequest,
    SkillMatchRequest,
    InterviewRequest,
)
from backend.app.services.job_service import JobService

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])
service = JobService()


@router.post("/analyze")
def analyze(request: JobAnalyzeRequest) -> dict:
    return {
        "code": 0,
        "message": "success",
        "data": service.analyze(request.jd).model_dump(),
    }


@router.post("/match")
def match(request: SkillMatchRequest) -> dict:
    return {
        "code": 0,
        "message": "success",
        "data": service.match(request.jd, request.skills).model_dump(),
    }


@router.post("/interview-questions")
def interview_questions(request: InterviewRequest) -> dict:
    return {
        "code": 0,
        "message": "success",
        "data": service.interview_questions(
            request.job_title, request.difficulty, request.count
        ),
    }
