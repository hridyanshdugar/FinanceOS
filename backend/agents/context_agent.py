"""
Context Agent: Uses Claude to RAG through client history, documents, and chat logs.
Generates a contextual summary and a personalized draft message to the client.
"""
from __future__ import annotations

import json
from services.llm import call_claude_json

SYSTEM_PROMPT = """\
You are the Context Agent in a wealth advisor's AI assistant called "FinanceOS."
Your job is to analyze all available client context and produce two things:
1. A brief contextual summary for the advisor (what's relevant to their question).
2. A personalized draft email to the client, written as if from the advisor "Alex."

Rules:
- You will receive analysis results from other specialist agents (quant calculations, compliance checks, investment research). INCORPORATE their findings into the draft email — reference specific numbers, recommendations, and compliance notes.
- The draft message must be empathetic, warm, and reference specific personal details (goals, life events, past conversations).
- Never fabricate facts. Only reference information present in the provided context and agent results.
- If information is missing, say so — never guess account balances or contribution room.
- The tone should match the client's communication style from past chats.
- Keep the draft concise (under 200 words) and end with an invitation to chat.
- Sign off as "Alex."

Respond in JSON with this exact structure:
{
  "summary": "Brief contextual summary for the advisor (1-3 sentences)",
  "rag_highlights": ["list of context sources used, e.g. 'client goals', 'NOA 2024', 'recent chat about mortgage'"],
  "draft_message": {
    "to": "Client full name",
    "subject": "Email subject line",
    "body": "The full draft email body",
    "tone": "Tone label, e.g. 'Warm + Encouraging'",
    "rag_highlights": ["same as above"]
  }
}"""


async def run_context_agent(
    client: dict,
    accounts: list[dict],
    documents: list[dict],
    recent_chat: list[dict],
    query: str,
    conn,
    quant_result: dict = None,
    compliance_result: dict = None,
    researcher_result: dict = None,
) -> dict:
    """Analyze client context via Claude and generate a personalized draft message."""
    name = client["name"]
    goals = client.get("goals", [])
    notes = client.get("advisor_notes", "")
    province = client.get("province", "")
    income = client.get("employment_income", 0)
    risk = client.get("risk_profile", "")
    marital = client.get("marital_status", "")
    dependents = client.get("dependents", 0)
    rag_context = client.get("rag_context", [])

    account_lines = []
    for acct in accounts:
        line = f"  {acct['type']} ({acct.get('label', '')}): balance ${acct['balance']:,.0f}"
        if acct.get("contribution_room", 0) > 0:
            line += f", contribution room ${acct['contribution_room']:,.0f}"
        account_lines.append(line)

    doc_lines = []
    for doc in documents:
        doc_lines.append(f"  {doc['type']} ({doc.get('tax_year', 'N/A')}): {doc['content_text'][:300]}")

    chat_lines = []
    for msg in reversed(recent_chat[:8]):
        chat_lines.append(f"  [{msg['role']}]: {msg['content'][:200]}")

    rag_lines = [f"  - {entry}" for entry in rag_context] if rag_context else ["  No knowledge base entries."]

    agent_results_section = ""
    if quant_result and quant_result.get("summary"):
        agent_results_section += f"\nQUANT AGENT RESULTS:\n  Summary: {quant_result['summary']}\n  Details: {quant_result.get('details', '')[:500]}\n"
    if compliance_result:
        status = compliance_result.get("status", "clear")
        items = compliance_result.get("items", [])
        items_text = "\n".join(f"  - {i.get('message', '')}" for i in items[:5]) if items else "  No issues."
        agent_results_section += f"\nCOMPLIANCE AGENT RESULTS (status: {status}):\n{items_text}\n"
    if researcher_result and researcher_result.get("summary"):
        suggestions = researcher_result.get("suggestions", [])
        suggestions_text = "\n".join(f"  - {s.get('ticker', '')}: {s.get('rationale', '')[:100]}" for s in suggestions[:5])
        agent_results_section += f"\nRESEARCHER AGENT RESULTS:\n  Summary: {researcher_result['summary']}\n{suggestions_text}\n  Account strategy: {researcher_result.get('account_strategy', '')[:200]}\n"

    user_message = f"""ADVISOR'S QUESTION: {query}

CLIENT PROFILE:
  Name: {name}
  Province: {province}
  Income: ${income:,.0f}
  Risk profile: {risk}
  Marital status: {marital}
  Dependents: {dependents}
  Goals: {json.dumps(goals)}
  Advisor notes: {notes}

CLIENT KNOWLEDGE BASE (advisor-curated context about this client):
{chr(10).join(rag_lines)}

ACCOUNTS:
{chr(10).join(account_lines) if account_lines else '  No accounts on file.'}

TAX DOCUMENTS:
{chr(10).join(doc_lines) if doc_lines else '  No documents on file.'}

RECENT CONVERSATION HISTORY:
{chr(10).join(chat_lines) if chat_lines else '  No prior conversations.'}
{agent_results_section}"""

    try:
        result = await call_claude_json(SYSTEM_PROMPT, user_message)
        if "draft_message" not in result:
            result["draft_message"] = {
                "to": name,
                "subject": "Following up",
                "body": result.get("summary", "I wanted to follow up on our conversation."),
                "tone": "Warm + Professional",
                "rag_highlights": result.get("rag_highlights", []),
            }
        return result
    except Exception as e:
        return {
            "summary": f"Context analysis encountered an issue: {str(e)[:100]}",
            "rag_highlights": [],
            "draft_message": {
                "to": name,
                "subject": "Following up",
                "body": f"Hi {name.split()[0]},\n\nI wanted to follow up on your recent question. Let me look into this further and get back to you.\n\nBest,\nAlex",
                "tone": "Warm + Professional",
                "rag_highlights": [],
            },
        }
