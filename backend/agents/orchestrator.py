"""
Multi-agent orchestrator for FinanceOS.
Classifies advisor queries to determine which agents (if any) to dispatch,
then aggregates results into the Tri-Tiered Output format.
"""
from __future__ import annotations

import json
import uuid
import asyncio
from datetime import datetime
from typing import Optional

import re

from fastapi import WebSocket

from db.database import get_connection, dicts_from_rows
from routes.ws import send_to


ROUTING_PROMPT = """\
You are a query router for a financial advisor's AI assistant.
Given the advisor's message about a client, classify which specialist agents are needed.

Available agents:
- context: Reads client profile, knowledge base, documents, and chat history. Drafts personalized emails. Use for questions about client background, communication, goals, or when a draft message is needed.
- quant: Runs financial calculations (tax brackets, contribution optimization, projections, comparisons). Use ONLY when math, numbers, or financial modeling is explicitly needed.
- compliance: Checks CRA rules, CIRO suitability, contribution limits, regulatory flags. Use ONLY when the question involves regulatory compliance, contribution limits, or tax rule verification.
- researcher: Suggests suitable investment products (ETFs, stocks, asset classes, GICs) and asset allocation based on client risk profile, goals, and accounts. Use when the advisor asks about investments, portfolio composition, stock/ETF suggestions, asset allocation, what to buy/sell, or rebalancing.

Rules:
- If the question is a simple lookup (e.g., "show me the knowledge base", "what accounts does this client have", "summarize this client"), return NO agents — the system can answer directly from the database.
- If the advisor wants to UPDATE the knowledge base (e.g., "remember that...", "note that...", "add to knowledge base...", "she prefers...", "he mentioned...", "update: ..."), set "rag_update" to true and extract the entries to add in "rag_entries" as a list of concise strings. Do NOT dispatch agents for this.
- If the question needs empathy, personalization, or a draft email, include "context".
- If the question involves calculations, comparisons, or projections, include "quant".
- If the question touches on regulations, limits, or compliance, include "compliance".
- If the question involves investment suggestions, ETFs, stocks, portfolio composition, asset allocation, what to buy, or rebalancing, include "researcher".
- Only include agents that are genuinely needed. Most questions need 1-2 agents, not all 4.

Respond in JSON only:
{"agents": ["context", "quant", "compliance", "researcher"], "reasoning": "brief explanation", "direct_answer": false, "rag_update": false, "rag_entries": []}

If NO agents are needed (simple lookup), respond:
{"agents": [], "reasoning": "brief explanation", "direct_answer": true, "rag_update": false, "rag_entries": []}

If the advisor wants to update the knowledge base, respond:
{"agents": [], "reasoning": "brief explanation", "direct_answer": false, "rag_update": true, "rag_entries": ["concise fact 1", "concise fact 2"]}"""


RAG_PREFIXES = [
    "remember", "note:", "note that", "add to knowledge base",
    "save that", "record that", "keep in mind", "update:",
    "don't forget", "log that", "mark that",
]

def _is_rag_update(query: str) -> bool:
    """Fast keyword check for obvious knowledge base update commands."""
    lower = query.lower().strip()
    for prefix in RAG_PREFIXES:
        if lower.startswith(prefix):
            return True
    return bool(re.match(r"^(he|she|they|client|this client)\s+(mentioned|said|told|prefers?|wants?|needs?|is |has |just )", lower))


def _extract_rag_entries(query: str) -> list:
    """Extract concise entries from a knowledge base update command."""
    lower = query.lower().strip()
    for prefix in RAG_PREFIXES:
        if lower.startswith(prefix):
            remainder = query.strip()[len(prefix):].strip().lstrip(":").strip()
            if remainder:
                return [remainder]
            break
    # Fall back to using the whole message minus obvious prefixes
    cleaned = re.sub(r"^(he|she|they|client|this client)\s+", "", query.strip(), flags=re.IGNORECASE)
    return [cleaned] if cleaned else []


async def _classify_query(query: str) -> dict:
    """Use Claude to determine which agents to dispatch, with fast-path for RAG updates."""
    if _is_rag_update(query):
        entries = _extract_rag_entries(query)
        if entries:
            return {"agents": [], "direct_answer": False, "rag_update": True, "rag_entries": entries, "reasoning": "keyword match: knowledge base update"}

    try:
        from services.llm import call_claude_json
        result = await call_claude_json(ROUTING_PROMPT, f"Advisor's message: {query}")
        if "agents" not in result:
            result["agents"] = ["context", "quant", "compliance", "researcher"]
        result["direct_answer"] = result.get("direct_answer", False)
        result["rag_update"] = result.get("rag_update", False)
        result["rag_entries"] = result.get("rag_entries", [])
        return result
    except Exception:
        return {"agents": ["context", "quant", "compliance", "researcher"], "direct_answer": False, "rag_update": False, "rag_entries": [], "reasoning": "classification failed, dispatching all"}


async def _direct_response(ws: WebSocket, client: dict, accounts: list, documents: list, rag_entries: list, recent_chat: list, query: str) -> str:
    """Answer simple lookups directly from the database using Claude, without dispatching agents."""
    from services.llm import call_claude

    name = client["name"]
    rag_lines = [f"  - {r['content']}" for r in rag_entries] if rag_entries else ["  (empty)"]
    account_lines = [f"  {a['type']} ({a.get('label','')}): ${a['balance']:,.0f}" + (f", room ${a['contribution_room']:,.0f}" if a.get('contribution_room', 0) > 0 else "") for a in accounts]
    doc_lines = [f"  {d['type']} ({d.get('tax_year','N/A')}): {d['content_text'][:200]}" for d in documents]
    chat_lines = [f"  [{m['role']}]: {m['content'][:150]}" for m in reversed(recent_chat[:5])]

    system = (
        "You are a concise AI assistant for a wealth advisor. Answer the advisor's question "
        "using ONLY the client data provided below. Be specific and reference actual data. "
        "If information is not in the data, say so. Do not make up information. "
        "Keep your response clear and concise (2-5 sentences)."
    )
    user_msg = f"""Advisor's question about {name}: "{query}"

CLIENT: {name}
  Province: {client.get('province', '')}
  Income: ${client.get('employment_income', 0):,.0f}
  Risk: {client.get('risk_profile', '')}
  Marital: {client.get('marital_status', '')}
  Dependents: {client.get('dependents', 0)}

KNOWLEDGE BASE:
{chr(10).join(rag_lines)}

ACCOUNTS:
{chr(10).join(account_lines) if account_lines else '  None on file.'}

DOCUMENTS:
{chr(10).join(doc_lines) if doc_lines else '  None on file.'}

RECENT CONVERSATION:
{chr(10).join(chat_lines) if chat_lines else '  No prior conversations.'}"""

    return await call_claude(system, user_msg, max_tokens=512, temperature=0.3)


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

    await send_to(ws, {"type": "thinking", "payload": {"step": "Analyzing your question..."}})

    routing = await _classify_query(content)
    needed_agents = routing.get("agents", [])
    is_direct = routing.get("direct_answer", False)
    is_rag_update = routing.get("rag_update", False)
    rag_new_entries = routing.get("rag_entries", [])

    if is_rag_update and rag_new_entries:
        from db.database import add_client_rag
        await send_to(ws, {"type": "thinking", "payload": {"step": f"Updating {client['name']}'s knowledge base..."}})

        added = []
        for entry_text in rag_new_entries:
            entry_text = str(entry_text).strip()
            if entry_text and len(entry_text) <= 500:
                row = add_client_rag(client_id, entry_text, source="advisor")
                added.append(row)

        count = len(added)
        summary = f"Done — added {count} {'entry' if count == 1 else 'entries'} to {client['name']}'s knowledge base:\n\n" + "\n".join(f"- {e['content']}" for e in added)

        conn.execute(
            "INSERT INTO chat_history (id, client_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), client_id, "system", summary, datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()

        await send_to(ws, {
            "type": "chat_response",
            "client_id": client_id,
            "task_id": task_id,
            "payload": {"content": summary, "analysis": None},
        })
        await send_to(ws, {
            "type": "rag_updated",
            "client_id": client_id,
            "payload": {"entries": added},
        })
        return

    if is_direct or len(needed_agents) == 0:
        await send_to(ws, {"type": "thinking", "payload": {"step": f"Answering from {client['name']}'s data..."}})

        try:
            summary = await _direct_response(ws, client, accounts, documents, rag_entries, recent_chat, content)
        except Exception:
            summary = "I couldn't process that request. Please try rephrasing your question."

        conn.execute(
            "INSERT INTO chat_history (id, client_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), client_id, "system", summary, datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()

        await send_to(ws, {
            "type": "chat_response",
            "client_id": client_id,
            "task_id": task_id,
            "payload": {"content": summary, "analysis": None},
        })
        return

    await send_to(ws, {"type": "thinking", "payload": {"step": f"Dispatching {len(needed_agents)} agent{'s' if len(needed_agents) != 1 else ''}..."}})

    from agents.context_agent import run_context_agent
    from agents.quant_agent import run_quant_agent
    from agents.compliance_agent import run_compliance_agent
    from agents.researcher_agent import run_researcher_agent

    agent_map = {
        "context": (run_context_agent, f"Reading {client['name']}'s profile, knowledge base, documents, and conversation history"),
        "quant": (run_quant_agent, f"Running financial calculations on {client['name']}'s accounts and tax situation"),
        "compliance": (run_compliance_agent, f"Checking CRA rules, CIRO suitability, and regulatory limits for {client['name']}"),
        "researcher": (run_researcher_agent, f"Researching suitable investments for {client['name']}'s {client.get('risk_profile', 'balanced')} profile"),
    }

    agent_tasks_list = []
    agent_task_ids = {}

    for agent_name in needed_agents:
        if agent_name not in agent_map:
            continue
        tid = str(uuid.uuid4())
        agent_task_ids[agent_name] = tid
        fn, description = agent_map[agent_name]

        await send_to(ws, {
            "type": "agent_dispatch",
            "agent": agent_name,
            "client_id": client_id,
            "task_id": tid,
            "payload": {"description": description},
        })
        conn.execute(
            "INSERT INTO agent_tasks (id, client_id, agent_type, status, input_data, created_at) VALUES (?,?,?,?,?,?)",
            (tid, client_id, agent_name, "running", json.dumps({"query": content}), datetime.now().isoformat()),
        )
        agent_tasks_list.append(
            _run_agent_with_updates(ws, tid, agent_name, client_id, fn, client, accounts, documents, recent_chat, content, conn)
        )

    conn.commit()

    results = await asyncio.gather(*agent_tasks_list)

    result_map = {}
    for i, agent_name in enumerate(n for n in needed_agents if n in agent_map):
        result_map[agent_name] = results[i]

    context_result = result_map.get("context")
    quant_result = result_map.get("quant")
    compliance_result = result_map.get("compliance")
    researcher_result = result_map.get("researcher")

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
        "research": researcher_result or None,
    }

    summary = await _synthesize_summary(client, content, context_result, quant_result, compliance_result, researcher_result)

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
    researcher_result: Optional[dict] = None,
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
        if researcher_result and researcher_result.get("summary"):
            suggestions_text = ", ".join(s.get("ticker", "") for s in researcher_result.get("suggestions", [])[:5])
            parts.append(f"INVESTMENT RESEARCH: {researcher_result['summary']} Suggestions: {suggestions_text}")

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
