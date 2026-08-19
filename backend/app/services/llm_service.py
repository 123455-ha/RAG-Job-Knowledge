from backend.app.rag.prompts import SYSTEM_PROMPT
from backend.app.core.config import get_settings
import httpx
import logging

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self) -> None:
        self.system_prompt = SYSTEM_PROMPT

    def answer(self, question: str, context: str, results: list[dict]) -> str:
        if not results or max(float(r.get("score", 0)) for r in results) < 0.15:
            return "当前知识库中没有找到足够的信息，无法可靠回答这个问题。"
        snippets = [r["content"].strip().replace("\n", " ") for r in results[:3]]
        settings = get_settings()
        if settings.openai_api_key:
            url = (
                f"{settings.openai_base_url.rstrip('/')}/chat/completions"
                if settings.openai_base_url
                else "https://api.openai.com/v1/chat/completions"
            )
            try:
                response = httpx.post(
                    url,
                    headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                    json={
                        "model": settings.llm_model,
                        "temperature": 0.1,
                        "messages": [
                            {"role": "system", "content": self.system_prompt},
                            {
                                "role": "user",
                                "content": f"Context:\n{context}\n\nQuestion: {question}",
                            },
                        ],
                    },
                    timeout=60,
                )
                response.raise_for_status()
                return str(response.json()["choices"][0]["message"]["content"])
            except (httpx.HTTPError, KeyError, IndexError, TypeError) as exc:
                logger.warning(
                    "External LLM request failed; using local fallback (%s)",
                    type(exc).__name__,
                )
        return (
            "基于知识库检索结果：\n"
            + "\n".join(f"- {snippet[:500]}" for snippet in snippets)
            + "\n\n以上结论来自检索到的文档片段。"
        )
