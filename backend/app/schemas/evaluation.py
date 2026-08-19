from pydantic import BaseModel


class EvaluationRequest(BaseModel):
    questions_path: str = "data/evaluation/questions.json"


class EvaluationResult(BaseModel):
    total: int
    retrieval_hit_rate: float
    answer_correctness: float
    citation_correctness: float
    unknown_handling_rate: float
    average_latency_ms: float
    details: list[dict]
