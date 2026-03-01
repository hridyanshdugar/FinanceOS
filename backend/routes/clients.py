from __future__ import annotations
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.database import get_connection, dicts_from_rows, get_client_rag, add_client_rag, delete_client_rag

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
        req_count = conn.execute(
            "SELECT COUNT(*) as cnt FROM chat_history WHERE client_id = ? AND role = 'client' AND status != 'completed'",
            (c["id"],),
        ).fetchone()
        c["pending_requests"] = req_count["cnt"] if req_count else 0
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

    rag_entries = dicts_from_rows(
        conn.execute("SELECT * FROM client_rag WHERE client_id = ? ORDER BY created_at ASC", (client_id,)).fetchall()
    )

    conn.close()
    return {
        "client": client,
        "accounts": accounts,
        "documents": documents,
        "chat_history": chat_history,
        "rag_entries": rag_entries,
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


@router.delete("/{client_id}/chat")
def clear_chat_history(client_id: str) -> dict:
    conn = get_connection()
    conn.execute(
        "DELETE FROM chat_history WHERE client_id = ? AND role != 'client'",
        (client_id,),
    )
    conn.commit()
    conn.close()
    return {"status": "cleared"}


@router.patch("/{client_id}/requests/{message_id}")
def complete_client_request(client_id: str, message_id: str) -> dict:
    conn = get_connection()
    cur = conn.execute(
        "UPDATE chat_history SET status = 'completed' WHERE id = ? AND client_id = ? AND role = 'client'",
        (message_id, client_id),
    )
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Client request not found")
    return {"status": "completed"}


class RagEntryRequest(BaseModel):
    content: str


@router.get("/{client_id}/rag")
def list_client_rag(client_id: str) -> list[dict]:
    return get_client_rag(client_id)


@router.post("/{client_id}/rag")
def create_client_rag(client_id: str, body: RagEntryRequest) -> dict:
    content = body.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Content cannot be empty")
    if len(content) > 500:
        raise HTTPException(status_code=400, detail="Content too long (max 500 characters)")
    return add_client_rag(client_id, content, source="advisor")


@router.delete("/{client_id}/rag/{entry_id}")
def remove_client_rag(client_id: str, entry_id: str) -> dict:
    deleted = delete_client_rag(entry_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="RAG entry not found")
    return {"status": "deleted"}
