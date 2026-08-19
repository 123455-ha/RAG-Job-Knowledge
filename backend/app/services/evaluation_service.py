import json
import time
from pathlib import Path
from backend.app.services.rag_service import RagService


class EvaluationService:
    def run(self, path: str) -> dict:
        questions = json.loads(Path(path).read_text(encoding="utf-8"))
        rag = RagService()
        details = []
        hits = 0
        unknown = 0
        answerable = 0
        answered = 0
        valid_citations = 0
        latency = []
        for item in questions:
            started = time.perf_counter()
            result = rag.chat(item["question"])
            latency.append((time.perf_counter() - started) * 1000)
            hit = bool(result["sources"])
            is_unknown = item.get("category") == "无答案"
            if not is_unknown:
                answerable += 1
                hits += hit
                answered += "没有找到足够" not in result["answer"]
                valid_citations += bool(result["sources"]) and all(
                    source.get("document_id") and source.get("chunk_id")
                    for source in result["sources"]
                )
            if is_unknown and "没有找到足够" in result["answer"]:
                unknown += 1
            details.append(
                {
                    "question": item["question"],
                    "retrieved": len(result["sources"]),
                    "latency_ms": round(latency[-1], 2),
                    "hit": hit,
                }
            )
        total = len(questions) or 1
        return {
            "total": len(questions),
            "retrieval_hit_rate": round(hits / max(1, answerable), 3),
            "answer_correctness": round(answered / max(1, answerable), 3),
            "citation_correctness": round(valid_citations / max(1, answerable), 3),
            "unknown_handling_rate": round(
                unknown / max(1, sum(i.get("category") == "无答案" for i in questions)),
                3,
            ),
            "average_latency_ms": round(sum(latency) / total, 2),
            "details": details,
        }
