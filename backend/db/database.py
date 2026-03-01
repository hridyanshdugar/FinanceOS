from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import List

_SRC_DIR = Path(__file__).parent
SCHEMA_PATH = _SRC_DIR / "schema.sql"

_db_dir = os.environ.get("DB_DIR", str(_SRC_DIR))
DB_PATH = Path(_db_dir) / "ws_shadow.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_connection()
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    # Migration: add status column to chat_history if missing
    cols = [row[1] for row in conn.execute("PRAGMA table_info(chat_history)").fetchall()]
    if "status" not in cols:
        conn.execute("ALTER TABLE chat_history ADD COLUMN status TEXT NOT NULL DEFAULT 'pending'")
        conn.commit()
    conn.close()


def dicts_from_rows(rows: List[sqlite3.Row]) -> List[dict]:
    return [dict(r) for r in rows]


# ── Client RAG helpers ───────────────────────────────────────────────

def get_client_rag(client_id: str) -> List[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM client_rag WHERE client_id = ? ORDER BY created_at ASC",
        (client_id,),
    ).fetchall()
    conn.close()
    return dicts_from_rows(rows)


def add_client_rag(client_id: str, content: str, source: str = "advisor") -> dict:
    import uuid
    entry_id = str(uuid.uuid4())
    conn = get_connection()
    conn.execute(
        "INSERT INTO client_rag (id, client_id, content, source, created_at) VALUES (?,?,?,?,datetime('now'))",
        (entry_id, client_id, content, source),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM client_rag WHERE id = ?", (entry_id,)).fetchone()
    conn.close()
    return dict(row)


def delete_client_rag(entry_id: str) -> bool:
    conn = get_connection()
    cur = conn.execute("DELETE FROM client_rag WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()
    return cur.rowcount > 0
