from pathlib import Path
from typing import Any


def load_file(path: str) -> list[dict[str, Any]]:
    file = Path(path)
    ext = file.suffix.lower()
    if ext in {".txt", ".md", ".markdown"}:
        return [
            {"content": file.read_text(encoding="utf-8", errors="ignore"), "page": None}
        ]
    if ext == ".pdf":
        try:
            from pypdf import PdfReader

            return [
                {"content": page.extract_text() or "", "page": i + 1}
                for i, page in enumerate(PdfReader(str(file)).pages)
            ]
        except ImportError:
            return [
                {
                    "content": "PDF parser unavailable. Install pypdf to parse this document.",
                    "page": None,
                }
            ]
    if ext == ".docx":
        try:
            from docx import Document

            return [
                {
                    "content": "\n".join(
                        p.text for p in Document(str(file)).paragraphs
                    ),
                    "page": None,
                }
            ]
        except ImportError:
            return [
                {
                    "content": "DOCX parser unavailable. Install python-docx to parse this document.",
                    "page": None,
                }
            ]
    raise ValueError(f"Unsupported extension: {ext}")
