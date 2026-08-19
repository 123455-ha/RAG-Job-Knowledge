from pydantic import BaseModel, Field


class JobAnalyzeRequest(BaseModel):
    jd: str = Field(min_length=20, max_length=20000)


class JobAnalysis(BaseModel):
    job_title: str
    responsibilities: list[str]
    required_skills: list[str]
    preferred_skills: list[str]
    education: list[str]
    experience: list[str]


class SkillMatchRequest(BaseModel):
    jd: str = Field(min_length=20)
    skills: list[str] = Field(min_length=1)


class SkillMatch(BaseModel):
    matched_skills: list[str]
    missing_skills: list[str]
    advantage_skills: list[str]
    learning_advice: list[str]
    match_score: float | None = None


class InterviewRequest(BaseModel):
    job_title: str = "AI/RAG Engineer"
    difficulty: str = "medium"
    count: int = Field(default=5, ge=1, le=20)


class InterviewQuestion(BaseModel):
    question: str
    difficulty: str
    answer: str
    sources: list[dict]
