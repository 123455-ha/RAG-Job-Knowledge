from backend.app.loaders.loader import load_file


def load_markdown(path: str) -> list[dict]:
    return load_file(path)
