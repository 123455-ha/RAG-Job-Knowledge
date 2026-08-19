import hashlib
import math
import re
import httpx
from backend.app.core.exceptions import AppError
from typing import Sequence


def tokenize(text: str) -> list[str]:
    latin = re.findall(r"[a-zA-Z0-9_+#.-]+", text.lower())
    cjk_tokens: list[str] = []
    for sequence in re.findall(r"[\u4e00-\u9fff]+", text):
        if len(sequence) == 1:
            cjk_tokens.append(sequence)
        else:
            cjk_tokens.extend(sequence[i : i + 2] for i in range(len(sequence) - 1))
    return latin + cjk_tokens


class BaseEmbeddingService:
    dimension = 384

    def embed(self, text: str) -> list[float]:
        raise NotImplementedError

    def embed_many(self, texts: Sequence[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]


class LocalEmbeddingService(BaseEmbeddingService):
    """Deterministic hashing embedding for no-key demo and tests."""

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        for token in tokenize(text):
            digest = hashlib.sha256(token.encode()).digest()
            idx = int.from_bytes(digest[:4], "big") % self.dimension
            vector[idx] += 1.0
        norm = math.sqrt(sum(x * x for x in vector)) or 1.0
        return [x / norm for x in vector]


class OpenAIEmbeddingService(LocalEmbeddingService):
    dimension = 1536

    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        self.api_key, self.base_url, self.model = api_key, base_url, model

    def embed(self, text: str) -> list[float]:
        if not self.api_key:
            return super().embed(text)
        url = (
            f"{self.base_url.rstrip('/')}/embeddings"
            if self.base_url
            else "https://api.openai.com/v1/embeddings"
        )
        try:
            response = httpx.post(
                url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": self.model, "input": text},
                timeout=30,
            )
            response.raise_for_status()
            return list(response.json()["data"][0]["embedding"])
        except (httpx.HTTPError, KeyError, IndexError, TypeError) as exc:
            raise AppError(
                f"Embedding 服务调用失败: {type(exc).__name__}", 5002
            ) from exc
