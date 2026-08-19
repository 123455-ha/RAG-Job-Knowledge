from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.app.services.evaluation_service import EvaluationService
from backend.app.services.document_service import DocumentService
from backend.app.database.database import init_db


if __name__ == "__main__":
    init_db()
    DocumentService().rebuild_index()
    print(EvaluationService().run("data/evaluation/questions.json"))
