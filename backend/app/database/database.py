import sqlite3
from pathlib import Path
from typing import Any
from backend.app.core.config import get_settings


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(get_settings().database_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    Path(get_settings().database_path).parent.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS documents (
          document_id TEXT PRIMARY KEY, file_name TEXT NOT NULL, file_type TEXT NOT NULL,
          file_path TEXT NOT NULL, uploaded_at TEXT NOT NULL, chunk_count INTEGER DEFAULT 0,
          status TEXT DEFAULT 'ready', error TEXT
        );
        CREATE TABLE IF NOT EXISTS messages (
          id INTEGER PRIMARY KEY AUTOINCREMENT, conversation_id TEXT NOT NULL,
          role TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL
        );
        """)


def execute(sql: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
    with connect() as conn:
        cur = conn.execute(sql, params)
        rows = cur.fetchall()
        conn.commit()
        return rows
