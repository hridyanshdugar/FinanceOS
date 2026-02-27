"""
Multi-agent orchestrator for FinanceOS.
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

    conn.execute(
        "INSERT INTO chat_history (id, client_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), client_id, "advisor", content, datetime.now().isoformat()),
    )
    conn.commit()

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
    rag_entries = dicts_from_rows(
        conn.execute(
            "SELECT * FROM client_rag WHERE client_id = ? ORDER BY created_at ASC",
            (client_id,),
        ).fetchall()
    )
    client["rag_context"] = [r["content"] for r in rag_entries]

    await send_to(ws, {"type": "thinking", "payload": {"step": "Starting analysis..."}})

    context_task_id = str(uuid.uuid4())
    quant_task_id = str(uuid.uuid4())
    compliance_task_id = str(uuid.uuid4())

    agent_descriptions = {
        "context": f"Reading {client['name']}'s profile, knowledge base, documents, and conversation history",
        "quant": f"Running financial calculations on {client['name']}'s accounts, knowledge base, and tax situation",
        "compliance": f"Checking CRA rules, CIRO suitability, and regulatory limits for {client['name']}",
    }

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
            "payload": {"description": agent_descriptions[agent_name]},
        })
        conn.execute(
            "INSERT INTO agent_tasks (id, client_id, agent_type, status, input_data, created_at) VALUES (?,?,?,?,?,?)",
            (tid, client_id, agent_name, "running", json.dumps({"query": content}), datetime.now().isoformat()),
        )
    conn.commit()

    from agents.context_agent import run_context_agent
    from agents.quant_agent import run_quant_agent
    from agents.compliance_agent import run_compliance_agent

    context_result, quant_result, compliance_result = await asyncio.gather(
        _run_agent_with_updates(ws, context_task_id, "context", client_id,
                                run_context_agent, client, accounts, documents, recent_chat, content, conn),
        _run_agent_with_updates(ws, quant_task_id, "quant", client_id,
                                run_quant_agent, client, accounts, documents, recent_chat, content, conn),
        _run_agent_with_updates(ws, compliance_task_id, "compliance", client_id,
                                run_compliance_agent, client, accounts, documents, recent_chat, content, conn),
    )

    await send_to(ws, {"type": "thinking", "payload": {"step": "Synthesizing results..."}})

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

    summary = await _synthesize_summary(client, content, context_result, quant_result, compliance_result)

    conn.execute(
        "INSERT INTO chat_history (id, client_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), client_id, "system", summary, datetime.now().isoformat()),
    )

    conn.execute(
        "INSERT INTO agent_tasks (id, client_id, agent_type, status, input_data, output_data, created_at, completed_at) VALUES (?,?,?,?,?,?,?,?)",
        (task_id, client_id, "orchestrator", "completed",
         json.dumps({"query": content}), json.dumps(tri_tiered),
         datetime.now().isoformat(), datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()

    await send_to(ws, {
        "type": "chat_response",
        "client_id": client_id,
        "task_id": task_id,
        "payload": {
            "content": summary,
            "analysis": tri_tiered,
        },
    })

    await send_to(ws, {
        "type": "tri_tiered_output",
        "client_id": client_id,
        "task_id": task_id,
        "payload": tri_tiered,
    })


async def _synthesize_summary(
    client: dict, query: str,
    context_result: Optional[dict],
    quant_result: Optional[dict],
    compliance_result: Optional[dict],
) -> str:
    """Use Claude to synthesize agent results into a conversational summary for the advisor."""
    try:
        from services.llm import call_claude

        parts = []
        if quant_result and quant_result.get("summary"):
            parts.append(f"QUANT ANALYSIS: {quant_result['summary']}")
        if context_result and context_result.get("summary"):
            parts.append(f"CLIENT CONTEXT: {context_result['summary']}")
        if compliance_result:
            status = compliance_result.get("status", "clear")
            items_text = "; ".join(i.get("message", "") for i in compliance_result.get("items", [])[:3])
            parts.append(f"COMPLIANCE ({status}): {items_text}" if items_text else f"COMPLIANCE: {status}")

        if not parts:
            return "I've looked into this for you. Here's what I found — open the full analysis for details."

        system = (
            "You are a concise AI assistant summarizing financial analysis for a wealth advisor. "
            "Write 2-3 sentences that capture the key insight from the agent results below. "
            "Be specific with numbers. Speak directly to the advisor. "
            "Do NOT include greetings. End with a prompt to open the full analysis panel."
        )
        user_msg = f"Advisor asked about client {client['name']}: \"{query}\"\n\n" + "\n".join(parts)
        return await call_claude(system, user_msg, max_tokens=256, temperature=0.3)
    except Exception:
        summary_parts = []
        if quant_result and quant_result.get("summary"):
            summary_parts.append(quant_result["summary"])
        if context_result and context_result.get("summary"):
            summary_parts.append(context_result["summary"])
        return " ".join(summary_parts) if summary_parts else "I've looked into this for you. Here's what I found."


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
