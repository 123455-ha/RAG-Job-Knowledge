from pathlib import Path
from uuid import uuid4

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".markdown", ".docx"}


def safe_filename(name: str) -> str:
    clean = Path(name).name.replace("\x00", "")
    stem = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in clean)
    return stem[:180] or f"upload_{uuid4().hex}.txt"
