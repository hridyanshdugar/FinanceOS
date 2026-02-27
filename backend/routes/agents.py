from __future__ import annotations
import json
from fastapi import APIRouter
from db.database import get_connection, dicts_from_rows
from models.agent import AgentActionRequest

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("/tasks")
def list_tasks(status: str = None, client_id: str = None, limit: int = 20) -> list[dict]:
    conn = get_connection()
    query = "SELECT * FROM agent_tasks WHERE 1=1"
    params = []
    if status:
        query += " AND status = ?"
        params.append(status)
    if client_id:
        query += " AND client_id = ?"
        params.append(client_id)
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    tasks = dicts_from_rows(rows)
    for t in tasks:
        t["input_data"] = json.loads(t["input_data"]) if t["input_data"] else {}
        t["output_data"] = json.loads(t["output_data"]) if t["output_data"] else {}
    conn.close()
    return tasks


@router.post("/tasks/{task_id}/action")
def act_on_task(task_id: str, req: AgentActionRequest) -> dict:
    conn = get_connection()
    conn.execute(
        "UPDATE agent_tasks SET advisor_action = ?, advisor_note = ? WHERE id = ?",
        (req.action, req.note, task_id),
    )
    conn.commit()
    conn.close()
    return {"status": "ok", "task_id": task_id, "action": req.action}
