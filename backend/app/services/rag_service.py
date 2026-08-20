import logging
import time
from datetime import datetime, timezone

from backend.app.database.database import execute
from backend.app.rag.context_builder import build_context
from backend.app.rag.query_rewriter import QueryRewriter
from backend.app.services.llm_service import LLMService
from backend.app.services.retrieval_service import RetrievalService
from backend.app.services.web_search_service import WebSearchService
from backend.app.utils.id_utils import new_id


class RagService:
    def __init__(self) -> None:
        self.retrieval = RetrievalService()
        self.llm = LLMService()
        self.query_rewriter = QueryRewriter()
        self.web_search = WebSearchService()

    def chat(self, question: str, conversation_id: str | None = None) -> dict:
        started = time.perf_counter()
        conv = conversation_id or new_id("conv_")
        rewritten_question = self.query_rewriter.rewrite(question, conversation_id)
        retrieval_started = time.perf_counter()
        kb_results = self.retrieval.retrieve(rewritten_question)
        has_kb_answer = (
            bool(kb_results)
            and max(float(r.get("score", 0)) for r in kb_results) >= 0.15
        )
        web_results = [] if has_kb_answer else self.web_search.search(question)
        retrieval_ms = int((time.perf_counter() - retrieval_started) * 1000)
        llm_started = time.perf_counter()
        answer = (
            self.llm.answer(question, build_context(kb_results), kb_results)
            if has_kb_answer
            else self.llm.answer_from_web(
                question, build_context(web_results), web_results
            )
        )
        llm_ms = int((time.perf_counter() - llm_started) * 1000)
        displayed_results = kb_results if has_kb_answer else web_results
        sources = [
            {
                "document_id": r["document_id"],
                "file_name": r["file_name"],
                "page": r.get("page"),
                "chunk_id": r["chunk_id"],
                "score": round(float(r.get("score", 0)), 4),
                "snippet": r["content"][:300],
                "source_type": r.get("source_type", "knowledge_base"),
                "url": r.get("url"),
            }
            for r in displayed_results
        ]
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
            "rag_request request_id=%s question=%r retrieval_time=%s llm_time=%s total_time=%s retrieval_count=%s web_fallback=%s",
            new_id("req_"),
            question[:200],
            retrieval_ms,
            llm_ms,
            total_ms,
            len(kb_results),
            not has_kb_answer,
        )
        return {
            "answer": answer,
            "sources": sources,
            "retrieval_count": len(kb_results),
            "latency_ms": total_ms,
            "conversation_id": conv,
        }
