from __future__ import annotations
import json
from fastapi import APIRouter, HTTPException
from db.database import get_connection, dict_from_row, dicts_from_rows
from models.client import Client, Account, Document, ChatMessage, ClientDetail

router = APIRouter(prefix="/api/clients", tags=["clients"])


@router.get("")
def list_clients() -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM clients ORDER BY name"
    ).fetchall()
    clients = dicts_from_rows(rows)
    for c in clients:
        c["goals"] = json.loads(c["goals"]) if c["goals"] else []
        accts = conn.execute(
            "SELECT COALESCE(SUM(balance), 0) as total FROM accounts WHERE client_id = ?",
            (c["id"],),
        ).fetchone()
        c["total_portfolio"] = accts["total"] if accts else 0
        alert_count = conn.execute(
            "SELECT COUNT(*) as cnt FROM alerts WHERE client_id = ? AND status = 'pending'",
            (c["id"],),
        ).fetchone()
        c["pending_alerts"] = alert_count["cnt"] if alert_count else 0
    conn.close()
    return clients


@router.get("/{client_id}")
def get_client(client_id: str) -> dict:
    conn = get_connection()
    row = conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Client not found")

    client = dict(row)
    client["goals"] = json.loads(client["goals"]) if client["goals"] else []

    accounts = dicts_from_rows(
        conn.execute("SELECT * FROM accounts WHERE client_id = ? ORDER BY type", (client_id,)).fetchall()
    )
    documents = dicts_from_rows(
        conn.execute("SELECT * FROM documents WHERE client_id = ? ORDER BY tax_year DESC", (client_id,)).fetchall()
    )
    chat_history = dicts_from_rows(
        conn.execute("SELECT * FROM chat_history WHERE client_id = ? ORDER BY created_at ASC", (client_id,)).fetchall()
    )
    total = sum(a["balance"] for a in accounts)

    conn.close()
    return {
        "client": client,
        "accounts": accounts,
        "documents": documents,
        "chat_history": chat_history,
        "total_portfolio": total,
    }


@router.get("/{client_id}/accounts")
def get_accounts(client_id: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM accounts WHERE client_id = ? ORDER BY type", (client_id,)
    ).fetchall()
    conn.close()
    return dicts_from_rows(rows)


@router.get("/{client_id}/chat")
def get_chat_history(client_id: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM chat_history WHERE client_id = ? ORDER BY created_at ASC",
        (client_id,),
    ).fetchall()
    conn.close()
    return dicts_from_rows(rows)
