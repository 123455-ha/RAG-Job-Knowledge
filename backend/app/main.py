from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.app.api import health, chat, documents, search, jobs, evaluation
from backend.app.core.exceptions import AppError
from backend.app.core.logging import configure_logging
from backend.app.database.database import init_db
from pathlib import Path
from backend.app.services.document_service import DocumentService
from backend.app.vectorstore.qdrant import store

configure_logging()
init_db()
_documents = DocumentService()
if not store._items:
    _documents.rebuild_index()
if not _documents.list():
    for _path in sorted(Path("data/demo").glob("*")):
        if _path.suffix.lower() in {".md", ".txt"}:
            try:
                _documents.create(_path.name, _path.suffix.lstrip("."), str(_path))
            except Exception:
                pass
app = FastAPI(
    title="RAG Job Knowledge Assistant",
    version="1.0.0",
    description="可部署的 RAG 求职知识库助手",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(search.router)
app.include_router(jobs.router)
app.include_router(evaluation.router)


@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=400 if exc.code < 4000 else 404 if exc.code == 4040 else 400,
        content={"code": exc.code, "message": exc.message, "data": None},
    )


@app.exception_handler(Exception)
async def generic_error_handler(_: Request, __: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500, content={"code": 5000, "message": "服务内部错误", "data": None}
    )
