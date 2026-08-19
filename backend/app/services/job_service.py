import re
from backend.app.schemas.job import JobAnalysis, SkillMatch
from backend.app.services.rag_service import RagService


SKILLS = [
    "Python",
    "FastAPI",
    "RAG",
    "LangChain",
    "LLM",
    "Agent",
    "Docker",
    "SQL",
    "Qdrant",
    "向量数据库",
    "Embedding",
    "Transformer",
    "React",
    "Kubernetes",
]


class JobService:
    def __init__(self) -> None:
        self.rag = RagService()

    def analyze(self, jd: str) -> JobAnalysis:
        title_match = re.search(r"(?:职位|岗位|招聘)\s*[:：]?\s*([^\n，,。]+)", jd)
        required = [skill for skill in SKILLS if re.search(re.escape(skill), jd, re.I)]
        responsibilities = [
            x.strip(" -•")
            for x in re.findall(r"(?:负责|工作职责|职责)[:：]?\s*([^\n]+)", jd)
        ]
        if not responsibilities:
            responsibilities = [
                line.strip(" -•")
                for line in jd.splitlines()
                if line.strip().startswith(("负责", "参与", "搭建"))
            ][:8]
        education = re.findall(r"(?:本科|硕士|博士|大专|学历)[^\n，。]*", jd) or []
        experience = re.findall(r"\d+\s*[年以上年经验个月]+", jd) or []
        return JobAnalysis(
            job_title=(title_match.group(1).strip() if title_match else "未识别岗位"),
            responsibilities=responsibilities,
            required_skills=required,
            preferred_skills=[],
            education=education,
            experience=experience,
        )

    def match(self, jd: str, skills: list[str]) -> SkillMatch:
        analysis = self.analyze(jd)
        normalized = {s.lower() for s in skills}
        matched = [s for s in analysis.required_skills if s.lower() in normalized]
        missing = [s for s in analysis.required_skills if s.lower() not in normalized]
        score = (
            round(len(matched) / len(analysis.required_skills), 3)
            if analysis.required_skills
            else None
        )
        advice = [f"补充学习 {s}，并在项目中完成可验证实践" for s in missing]
        return SkillMatch(
            matched_skills=matched,
            missing_skills=missing,
            advantage_skills=[
                s
                for s in skills
                if s.lower() not in {x.lower() for x in analysis.required_skills}
            ],
            learning_advice=advice,
            match_score=score,
        )

    def interview_questions(
        self, title: str, difficulty: str, count: int
    ) -> list[dict]:
        bank = [
            (
                "请解释 RAG 的核心流程以及它如何缓解大模型幻觉？",
                "检索、重排、上下文构造和生成，并通过来源约束回答范围。",
            ),
            (
                "如何选择 chunk size 和 overlap？",
                "结合文档结构、检索粒度和上下文窗口，通过离线评测调整。",
            ),
            (
                "向量检索和关键词检索各有什么优缺点？",
                "向量擅长语义召回，关键词适合精确术语，混合可以互补。",
            ),
            (
                "如何设计引用与无答案拒答？",
                "保留 chunk 元数据，设置相关性阈值，低于阈值返回明确拒答。",
            ),
            (
                "Qdrant 在 RAG 中承担什么职责？",
                "保存向量和 payload，按相似度及元数据过滤召回片段。",
            ),
            (
                "如何评测 RAG 系统？",
                "同时关注检索命中、答案正确性、引用正确性、拒答率和延迟。",
            ),
        ]
        return [
            {"question": q, "difficulty": difficulty, "answer": a, "sources": []}
            for q, a in (bank * ((count + len(bank) - 1) // len(bank)))[:count]
        ]
