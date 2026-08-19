from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.app.services.document_service import DocumentService
from backend.app.database.database import init_db


def main() -> None:
    init_db()
    service = DocumentService()
    for path in sorted(Path("data/demo").glob("*")):
        if path.suffix.lower() in {".md", ".txt"}:
            if not any(d["file_name"] == path.name for d in service.list()):
                service.create(path.name, path.suffix.lstrip("."), str(path))
    service.rebuild_index()
    print(f"Loaded {len(service.list())} demo documents")


if __name__ == "__main__":
    main()
