"""
Multi-agent orchestrator for WS Shadow.
Routes advisor queries to specialized agents and aggregates results
into the Tri-Tiered Output format.
"""
from __future__ import annotations

import json
import uuid
import asyncio
from datetime import datetime
from typing import Optional

from fastapi import WebSocket

from db.database import get_connection, dicts_from_rows
from routes.ws import send_to


async def handle_chat_message(ws: WebSocket, message: dict):
    """Main entry point: receives a chat message from the advisor and orchestrates agents."""
    client_id = message.get("client_id")
    content = message.get("content", "")
    task_id = str(uuid.uuid4())

    if not client_id or not content:
        await send_to(ws, {
            "type": "error",
            "payload": {"message": "Missing client_id or content"},
        })
        return

    conn = get_connection()

    # Save advisor message to chat history
    conn.execute(
        "INSERT INTO chat_history (id, client_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), client_id, "advisor", content, datetime.now().isoformat()),
    )
    conn.commit()

    # Fetch client context
    client_row = conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
    if not client_row:
        conn.close()
        await send_to(ws, {"type": "error", "payload": {"message": "Client not found"}})
        return

    client = dict(client_row)
    client["goals"] = json.loads(client["goals"]) if client["goals"] else []

    accounts = dicts_from_rows(
        conn.execute("SELECT * FROM accounts WHERE client_id = ?", (client_id,)).fetchall()
    )
    documents = dicts_from_rows(
        conn.execute("SELECT * FROM documents WHERE client_id = ?", (client_id,)).fetchall()
    )
    recent_chat = dicts_from_rows(
        conn.execute(
            "SELECT * FROM chat_history WHERE client_id = ? ORDER BY created_at DESC LIMIT 10",
            (client_id,),
        ).fetchall()
    )

    # Notify: thinking
    await send_to(ws, {"type": "thinking"})

    # Dispatch agents
    context_task_id = str(uuid.uuid4())
    quant_task_id = str(uuid.uuid4())
    compliance_task_id = str(uuid.uuid4())

    for tid, agent_name in [
        (context_task_id, "context"),
        (quant_task_id, "quant"),
        (compliance_task_id, "compliance"),
    ]:
        await send_to(ws, {
            "type": "agent_dispatch",
            "agent": agent_name,
            "client_id": client_id,
            "task_id": tid,
            "payload": {},
        })
        conn.execute(
            "INSERT INTO agent_tasks (id, client_id, agent_type, status, input_data, created_at) VALUES (?,?,?,?,?,?)",
            (tid, client_id, agent_name, "running", json.dumps({"query": content}), datetime.now().isoformat()),
        )
    conn.commit()

    # Run agents in parallel
    from agents.context_agent import run_context_agent
    from agents.quant_agent import run_quant_agent
    from agents.compliance_agent import run_compliance_agent

    context_result, quant_result, compliance_result = await asyncio.gather(
        _run_agent_with_updates(ws, context_task_id, "context", client_id,
                                run_context_agent, client, accounts, documents, recent_chat, content, conn),
        _run_agent_with_updates(ws, quant_task_id, "quant", client_id,
                                run_quant_agent, client, accounts, content, conn),
        _run_agent_with_updates(ws, compliance_task_id, "compliance", client_id,
                                run_compliance_agent, client, accounts, content, conn),
    )

    # Format Tri-Tiered Output
    tri_tiered = {
        "numbers": quant_result or {
            "summary": "No calculations needed for this query.",
            "details": "",
            "python_code": "",
            "latex": "",
        },
        "compliance": compliance_result or {
            "status": "clear",
            "items": [],
        },
        "draft_message": context_result.get("draft_message", {
            "to": client["name"],
            "subject": "Following up",
            "body": context_result.get("summary", "I wanted to follow up on our recent conversation."),
            "tone": "Warm + Professional",
            "rag_highlights": context_result.get("rag_highlights", []),
        }) if context_result else {
            "to": client["name"],
            "subject": "Following up",
            "body": "I wanted to follow up on our conversation.",
            "tone": "Warm + Professional",
            "rag_highlights": [],
        },
    }

    # Build summary response
    summary_parts = []
    if quant_result and quant_result.get("summary"):
        summary_parts.append(quant_result["summary"])
    if context_result and context_result.get("summary"):
        summary_parts.append(context_result["summary"])

    summary = " ".join(summary_parts) if summary_parts else "I've looked into this for you. Here's what I found."

    # Save response to chat history
    conn.execute(
        "INSERT INTO chat_history (id, client_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), client_id, "system", summary, datetime.now().isoformat()),
    )

    # Save master task
    conn.execute(
        "INSERT INTO agent_tasks (id, client_id, agent_type, status, input_data, output_data, created_at, completed_at) VALUES (?,?,?,?,?,?,?,?)",
        (task_id, client_id, "orchestrator", "completed",
         json.dumps({"query": content}), json.dumps(tri_tiered),
         datetime.now().isoformat(), datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()

    # Send chat response
    await send_to(ws, {
        "type": "chat_response",
        "client_id": client_id,
        "task_id": task_id,
        "payload": {
            "content": summary,
            "analysis": tri_tiered,
        },
    })

    # Send tri-tiered output to open the artifact panel
    await send_to(ws, {
        "type": "tri_tiered_output",
        "client_id": client_id,
        "task_id": task_id,
        "payload": tri_tiered,
    })


async def _run_agent_with_updates(
    ws: WebSocket,
    task_id: str,
    agent_name: str,
    client_id: str,
    agent_fn,
    *args,
) -> Optional[dict]:
    """Run an agent function, sending WebSocket updates on progress and completion."""
    try:
        await send_to(ws, {
            "type": "agent_update",
            "agent": agent_name,
            "client_id": client_id,
            "task_id": task_id,
            "payload": {"status": "running"},
        })

        result = await agent_fn(*args)

        conn = get_connection()
        conn.execute(
            "UPDATE agent_tasks SET status = 'completed', output_data = ?, completed_at = ? WHERE id = ?",
            (json.dumps(result or {}), datetime.now().isoformat(), task_id),
        )
        conn.commit()
        conn.close()

        await send_to(ws, {
            "type": "agent_complete",
            "agent": agent_name,
            "client_id": client_id,
            "task_id": task_id,
            "payload": result or {},
        })

        return result
    except Exception as e:
        conn = get_connection()
        conn.execute(
            "UPDATE agent_tasks SET status = 'failed', output_data = ?, completed_at = ? WHERE id = ?",
            (json.dumps({"error": str(e)}), datetime.now().isoformat(), task_id),
        )
        conn.commit()
        conn.close()

        await send_to(ws, {
            "type": "agent_complete",
            "agent": agent_name,
            "client_id": client_id,
            "task_id": task_id,
            "payload": {"error": str(e)},
        })
        return None
