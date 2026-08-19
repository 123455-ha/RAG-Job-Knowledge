from pathlib import Path


def extension(filename: str) -> str:
    return Path(filename).suffix.lower()
