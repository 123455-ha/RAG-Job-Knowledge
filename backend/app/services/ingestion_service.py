from backend.app.services.document_service import DocumentService


class IngestionService:
    def __init__(self) -> None:
        self.documents = DocumentService()

    def ingest(self, file_name: str, file_type: str, path: str) -> dict:
        return self.documents.create(file_name, file_type, path)
