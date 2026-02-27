from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Optional, List

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
    conn.close()


def dict_from_row(row: Optional[sqlite3.Row]) -> Optional[dict]:
    if row is None:
        return None
    return dict(row)


def dicts_from_rows(rows: List[sqlite3.Row]) -> List[dict]:
    return [dict(r) for r in rows]
