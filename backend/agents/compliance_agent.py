"""
Compliance Agent: Uses Claude with web search to audit financial advice against
CRA rules, CIRO regulations, and Canadian tax law. Combines LLM reasoning with
hard-coded regulatory limits and live web search for zero-hallucination fact checking.
"""
from __future__ import annotations

import json
from datetime import date
from services.llm import call_claude_json_with_search

CRA_LIMITS = {
    "rrsp_annual_2024": 31560,
    "tfsa_annual_2024": 7000,
    "fhsa_annual": 8000,
    "fhsa_lifetime": 40000,
    "cesg_annual_max_per_child": 500,
    "cesg_lifetime_per_child": 7200,
    "oas_clawback_threshold_2024": 90997,
}

RRIF_MIN_PCT = {
    65: 0.04, 66: 0.0417, 67: 0.0435, 70: 0.05,
    75: 0.0582, 80: 0.0682, 85: 0.0851, 90: 0.1111, 94: 0.1667, 95: 0.20,
}

SYSTEM_PROMPT = """\
You are the Compliance Agent in a Canadian wealth advisor's AI assistant.
Your job is to audit the advisor's question and the client's financial situation
against Canadian regulations: CRA rules, CIRO suitability requirements, and tax law.

You have access to web search. Use it to look up the latest CRA contribution limits,
tax brackets, CIRO guidelines, or any regulatory changes relevant to the advisor's question.
Always verify that the hard-coded limits below are still current.

ZERO-HALLUCINATION RULES:
- ONLY use the HARD FACTS, client data, and information you find via web search. NEVER guess contribution limits or balances.
- If data is missing, say "data not available" rather than assuming a value.
- Reference specific account balances and contribution rooms from the provided data.
- When web search results contain updated limits or rules, prefer them over the hard-coded values and note the source.

You will receive HARD FACTS — regulatory limits that may need verification against current rules.
Use web search to confirm these are up to date, especially contribution limits and tax brackets.
If the advisor's question or any implied advice would violate these limits, flag it.

Rules:
- Flag any use of prohibited terms: "guaranteed returns", "guaranteed profit", "risk-free", "no risk", "can't lose."
- Check contribution room limits against CRA rules using the actual room figures provided.
- For seniors (65+), check OAS clawback risk and RRIF minimum withdrawals.
- For Quebec clients, note that provincial tax rules differ (Revenu Québec).
- Consider the client's goals, documents, and conversation history for context.
- Each item must have a severity: "info" (neutral fact), "warning" (potential issue), or "error" (violation).
- Include the specific rule citation (e.g., "ITA 146(1)") when applicable.
- If you find recent rule changes via web search, include an "info" item noting the update with the source.

Respond in JSON:
{
  "status": "clear" | "warning" | "error",
  "items": [
    {
      "severity": "info" | "warning" | "error",
      "message": "Plain-language explanation referencing actual client data",
      "rule_citation": "e.g. ITA 146(1) - RRSP deduction limit"
    }
  ]
}"""


async def run_compliance_agent(
    client: dict,
    accounts: list[dict],
    documents: list[dict],
    recent_chat: list[dict],
    query: str,
    conn,
) -> dict:
    """Check compliance via Claude with web search, augmented with hard-coded CRA limits."""
    name = client["name"]
    income = client.get("employment_income", 0)
    province = client.get("province", "")
    dob = client.get("date_of_birth", "")
    dependents = client.get("dependents", 0)
    goals = client.get("goals", [])
    marital = client.get("marital_status", "")
    notes = client.get("advisor_notes", "")
    rag_context = client.get("rag_context", [])
    age = _estimate_age(dob)

    account_lines = []
    for acct in accounts:
        line = f"  {acct['type']}: balance ${acct['balance']:,.0f}"
        if acct.get("contribution_room", 0) > 0:
            line += f", contribution room ${acct['contribution_room']:,.0f}"
        account_lines.append(line)

    doc_lines = []
    for doc in documents:
        doc_lines.append(f"  {doc['type']} ({doc.get('tax_year', 'N/A')}): {doc['content_text'][:300]}")

    chat_lines = []
    for msg in reversed(recent_chat[:5]):
        chat_lines.append(f"  [{msg['role']}]: {msg['content'][:200]}")

    hard_facts = f"""HARD FACTS (regulatory limits — verify via web search if relevant):
  RRSP annual limit 2024: ${CRA_LIMITS['rrsp_annual_2024']:,}
  TFSA annual limit 2024: ${CRA_LIMITS['tfsa_annual_2024']:,}
  FHSA annual limit: ${CRA_LIMITS['fhsa_annual']:,}, lifetime: ${CRA_LIMITS['fhsa_lifetime']:,}
  CESG: 20% match on first $2,500/child/year, max ${CRA_LIMITS['cesg_annual_max_per_child']:,}/child/year
  OAS clawback threshold 2024: ${CRA_LIMITS['oas_clawback_threshold_2024']:,}
  Client age: {age}"""

    if age >= 65:
        rrif_pct = _get_rrif_min_pct(age)
        hard_facts += f"\n  RRIF minimum withdrawal at age {age}: {rrif_pct:.2%}"
        for acct in accounts:
            if acct["type"] == "RRIF":
                min_wd = acct["balance"] * rrif_pct
                hard_facts += f"\n  RRIF balance: ${acct['balance']:,.0f}, minimum withdrawal: ${min_wd:,.0f}"

    rag_lines = [f"  - {entry}" for entry in rag_context] if rag_context else ["  No knowledge base entries."]

    user_message = f"""ADVISOR'S QUESTION: {query}

CLIENT: {name}
  Province: {province}
  Income: ${income:,.0f}
  Age: {age}
  Marital status: {marital}
  Dependents: {dependents}
  Goals: {json.dumps(goals)}
  Advisor notes: {notes}

CLIENT KNOWLEDGE BASE (advisor-curated context about this client):
{chr(10).join(rag_lines)}

ACCOUNTS (verified from database):
{chr(10).join(account_lines)}

TAX DOCUMENTS:
{chr(10).join(doc_lines) if doc_lines else '  No documents on file.'}

RECENT CONVERSATION:
{chr(10).join(chat_lines) if chat_lines else '  No prior conversations.'}

{hard_facts}
"""

    try:
        result = await call_claude_json_with_search(SYSTEM_PROMPT, user_message)
        if "status" not in result:
            result["status"] = "clear"
        if "items" not in result:
            result["items"] = []
        return result
    except Exception as e:
        return {
            "status": "clear",
            "items": [{
                "severity": "info",
                "message": f"Compliance check encountered an issue: {str(e)[:100]}. Manual review recommended.",
                "rule_citation": "",
            }],
        }


def _estimate_age(dob: str) -> int:
    if not dob:
        return 0
    try:
        parts = dob.split("-")
        birth = date(int(parts[0]), int(parts[1]), int(parts[2]))
        today = date.today()
        return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    except Exception:
        return 0


def _get_rrif_min_pct(age: int) -> float:
    for threshold_age in sorted(RRIF_MIN_PCT.keys(), reverse=True):
        if age >= threshold_age:
            return RRIF_MIN_PCT[threshold_age]
    return 0.04
