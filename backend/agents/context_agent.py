"""
Context Agent: RAGs through client history, documents, and chat logs
to pull goals, constraints, and generate personalized draft messages.
"""
from __future__ import annotations

import json
import asyncio
from typing import Optional


async def run_context_agent(
    client: dict,
    accounts: list[dict],
    documents: list[dict],
    recent_chat: list[dict],
    query: str,
    conn,
) -> dict:
    """Analyze client context and generate a personalized response with draft message."""
    await asyncio.sleep(1.2)

    goals = client.get("goals", [])
    name = client["name"]
    first_name = name.split()[0]
    notes = client.get("advisor_notes", "")

    chat_context = []
    for msg in recent_chat[:5]:
        chat_context.append(f"{msg['role']}: {msg['content']}")

    doc_summaries = []
    for doc in documents:
        doc_summaries.append(f"{doc['type']} ({doc.get('tax_year', 'N/A')}): {doc['content_text'][:200]}")

    rag_highlights = []
    if goals:
        rag_highlights.append(f"goals: {', '.join(goals[:2])}")
    if notes:
        rag_highlights.append(f"advisor notes")
    if chat_context:
        rag_highlights.append(f"recent conversations")

    account_summary = []
    for acct in accounts:
        parts = [f"{acct['type']}: ${acct['balance']:,.0f}"]
        if acct.get("contribution_room", 0) > 0:
            parts.append(f"room: ${acct['contribution_room']:,.0f}")
        account_summary.append(" | ".join(parts))

    goal_text = ""
    if goals:
        goal_text = f" I know {first_name}'s goals include {goals[0].lower()}"
        if len(goals) > 1:
            goal_text += f" and {goals[1].lower()}"
        goal_text += "."

    summary = f"Based on {first_name}'s profile and our past conversations, here's the context that's relevant.{goal_text}"

    query_lower = query.lower()

    subject = "Following up on our conversation"
    tone = "Warm + Professional"

    if "rrsp" in query_lower or "contribution" in query_lower:
        subject = f"Quick thought on your RRSP"
        tone = "Warm + Informative"
    elif "mortgage" in query_lower or "home" in query_lower or "fhsa" in query_lower:
        subject = f"Thinking about your home purchase"
        tone = "Warm + Encouraging"
    elif "portfolio" in query_lower or "review" in query_lower:
        subject = f"Your portfolio review"
        tone = "Professional + Reassuring"
    elif "resp" in query_lower or "education" in query_lower:
        subject = f"Education savings update"
        tone = "Warm + Encouraging"
    elif "tax" in query_lower:
        subject = f"Tax planning thoughts"
        tone = "Professional + Informative"

    body_parts = [f"Hi {first_name},\n"]
    body_parts.append(f"I've been looking into your question about {_simplify_query(query)}.\n")

    if goals:
        body_parts.append(
            f"Keeping in mind your goal of {goals[0].lower()}, here's what I'd recommend:\n"
        )

    body_parts.append("[Analysis details will be filled in by the Numbers section]\n")
    body_parts.append("I'd love to walk you through this in more detail. Would you have 15 minutes this week to chat?\n")
    body_parts.append("Best,\nAlex")

    draft_body = "\n".join(body_parts)

    return {
        "summary": summary,
        "rag_highlights": rag_highlights,
        "client_context": {
            "goals": goals,
            "accounts": account_summary,
            "documents": doc_summaries,
        },
        "draft_message": {
            "to": name,
            "subject": subject,
            "body": draft_body,
            "tone": tone,
            "rag_highlights": rag_highlights,
        },
    }


def _simplify_query(query: str) -> str:
    """Turn the advisor's query into a client-friendly phrase."""
    q = query.lower().strip().rstrip(".")
    if len(q) > 80:
        q = q[:80] + "..."
    for prefix in ["what's the best move for", "check", "run a", "compare", "draft a"]:
        if q.startswith(prefix):
            q = q[len(prefix):].strip()
    return q
