from backend.app.loaders.loader import load_file


def load_pdf(path: str) -> list[dict]:
    return load_file(path)
