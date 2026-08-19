from backend.app.loaders.loader import load_file


def load_txt(path: str) -> list[dict]:
    return load_file(path)
