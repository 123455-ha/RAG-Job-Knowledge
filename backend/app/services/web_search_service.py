"""Keyless web-search adapter using Bing RSS."""

import logging
from urllib.parse import quote_plus
from xml.etree import ElementTree
import httpx

logger = logging.getLogger(__name__)


class WebSearchService:
    def __init__(self, limit: int = 5) -> None:
        self.limit = limit

    def search(self, query: str) -> list[dict]:
        try:
            response = httpx.get(
                f"https://www.bing.com/search?format=rss&q={quote_plus(query)}",
                headers={"User-Agent": "RAG-Job-Knowledge-Assistant/1.0"},
                timeout=15,
                follow_redirects=True,
            )
            response.raise_for_status()
            root = ElementTree.fromstring(response.content)
        except (httpx.HTTPError, ElementTree.ParseError) as exc:
            logger.warning("Web search failed (%s)", type(exc).__name__)
            return []
        results = []
        for item in root.findall(".//item")[: self.limit]:
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            snippet = (item.findtext("description") or "").strip()
            if title and link:
                results.append(
                    {
                        "document_id": "web",
                        "file_name": title,
                        "page": None,
                        "chunk_id": f"web_{abs(hash(link))}",
                        "score": 0.2,
                        "snippet": snippet[:500],
                        "content": f"{title}\n{snippet}",
                        "source": link,
                        "source_type": "web",
                        "url": link,
                    }
                )
        return results
