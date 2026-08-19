from pathlib import Path
from fastapi import APIRouter, File, UploadFile
from backend.app.core.config import get_settings
from backend.app.core.exceptions import AppError, UnsupportedFileError
from backend.app.core.security import ALLOWED_EXTENSIONS, safe_filename
from backend.app.services.document_service import DocumentService
from backend.app.services.ingestion_service import IngestionService
from backend.app.utils.file_utils import extension

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])
service = DocumentService()
ingestion = IngestionService()


@router.post("/upload")
async def upload(file: UploadFile = File(...)) -> dict:
    name = safe_filename(file.filename or "upload.txt")
    ext = extension(name)
    if ext not in ALLOWED_EXTENSIONS:
        raise UnsupportedFileError("仅支持 PDF、TXT、MD、DOCX 文件")
    data = await file.read()
    limit = get_settings().max_file_size_mb * 1024 * 1024
    if len(data) > limit:
        raise AppError(f"文件超过 {get_settings().max_file_size_mb}MB 限制", 4002)
    path = Path(get_settings().upload_dir) / name
    path.write_bytes(data)
    result = ingestion.ingest(name, ext.lstrip("."), str(path))
    return {"code": 0, "message": "success", "data": result}


@router.get("")
def list_documents() -> dict:
    return {"code": 0, "message": "success", "data": service.list()}


@router.get("/{document_id}")
def get_document(document_id: str) -> dict:
    doc = service.get(document_id)
    if not doc:
        raise AppError("文档不存在", 4040)
    return {"code": 0, "message": "success", "data": doc}


@router.delete("/{document_id}")
def delete_document(document_id: str) -> dict:
    if not service.delete(document_id):
        raise AppError("文档不存在", 4040)
    return {"code": 0, "message": "success", "data": {"document_id": document_id}}
