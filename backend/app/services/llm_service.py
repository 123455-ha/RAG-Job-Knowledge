from backend.app.rag.prompts import SYSTEM_PROMPT
from backend.app.core.config import get_settings
import httpx
import logging

logger = logging.getLogger(__name__)


def extract_message_content(payload: dict) -> str:
    """Normalize OpenAI-compatible content formats, including Qwen reasoning responses."""
    choices = payload.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, list):
        content = "".join(
            str(part.get("text", "")) if isinstance(part, dict) else str(part)
            for part in content
        )
    if content and str(content).strip():
        return str(content).strip()
    reasoning = message.get("reasoning_content") or message.get("reasoning")
    return str(reasoning).strip() if reasoning else ""


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
                content = extract_message_content(response.json())
                if content:
                    return content
                logger.warning(
                    "External LLM returned empty content; using local fallback"
                )
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

    def answer_from_web(self, question: str, context: str, results: list[dict]) -> str:
        if not results:
            return "知识库中没有找到相关资料，网络检索也没有返回可用结果。"
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
                            {
                                "role": "system",
                                "content": "你是求职知识助手。知识库没有相关资料，以下是网络检索摘要。只能依据摘要回答，明确说明答案来自网络并提醒用户自行核验，不得编造。",
                            },
                            {
                                "role": "user",
                                "content": f"网络摘要:\n{context}\n\n问题：{question}",
                            },
                        ],
                    },
                    timeout=60,
                )
                response.raise_for_status()
                content = extract_message_content(response.json())
                if content:
                    return (
                        "知识库中没有找到相关资料。以下回答基于网络检索结果，仅供参考：\n\n"
                        + content
                    )
                logger.warning("External web-answer LLM returned empty content")
            except (httpx.HTTPError, KeyError, IndexError, TypeError) as exc:
                logger.warning(
                    "Web-answer LLM failed; using snippets (%s)", type(exc).__name__
                )
        return (
            "知识库中没有找到相关资料。以下是网络检索到的摘要，请结合链接自行核验：\n"
            + "\n".join(f"- {r['file_name']}：{r['snippet'][:300]}" for r in results)
        )
