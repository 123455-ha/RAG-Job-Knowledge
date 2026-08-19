import time
import logging
from datetime import datetime, timezone
from backend.app.database.database import execute
from backend.app.services.llm_service import LLMService
from backend.app.services.retrieval_service import RetrievalService
from backend.app.utils.id_utils import new_id
from backend.app.rag.context_builder import build_context
from backend.app.rag.query_rewriter import QueryRewriter


class RagService:
    def __init__(self) -> None:
        self.retrieval = RetrievalService()
        self.llm = LLMService()
        self.query_rewriter = QueryRewriter()

    def chat(self, question: str, conversation_id: str | None = None) -> dict:
        started = time.perf_counter()
        conv = conversation_id or new_id("conv_")
        rewritten_question = self.query_rewriter.rewrite(question, conversation_id)
        retrieval_started = time.perf_counter()
        results = self.retrieval.retrieve(rewritten_question)
        retrieval_ms = int((time.perf_counter() - retrieval_started) * 1000)
        llm_started = time.perf_counter()
        answer = self.llm.answer(question, build_context(results), results)
        llm_ms = int((time.perf_counter() - llm_started) * 1000)
        sources = [
            {
                "document_id": r["document_id"],
                "file_name": r["file_name"],
                "page": r.get("page"),
                "chunk_id": r["chunk_id"],
                "score": round(float(r.get("score", 0)), 4),
                "snippet": r["content"][:300],
            }
            for r in results
        ]
        if "没有找到足够的信息" in answer:
            sources = []
        now = datetime.now(timezone.utc).isoformat()
        execute(
            "INSERT INTO messages(conversation_id,role,content,created_at) VALUES (?,?,?,?)",
            (conv, "user", question, now),
        )
        execute(
            "INSERT INTO messages(conversation_id,role,content,created_at) VALUES (?,?,?,?)",
            (conv, "assistant", answer, now),
        )
        total_ms = int((time.perf_counter() - started) * 1000)
        logging.getLogger(__name__).info(
            "rag_request request_id=%s question=%r embedding_time=0 rerank_time=0 retrieval_time=%s llm_time=%s total_time=%s retrieval_count=%s",
            new_id("req_"),
            question[:200],
            retrieval_ms,
            llm_ms,
            total_ms,
            len(results),
        )
        return {
            "answer": answer,
            "sources": sources,
            "retrieval_count": len(results),
            "latency_ms": total_ms,
            "conversation_id": conv,
        }
