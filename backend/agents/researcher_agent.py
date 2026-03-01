"""
Researcher Agent: Uses Claude with web search to suggest suitable investment products
(ETFs, stocks, asset classes) based on the client's risk profile,
goals, accounts, knowledge base, and the advisor's question.
Searches the web for current market data and investment research.
Returns structured suggestions with rationale tied to client data.
"""
from __future__ import annotations

import json
from services.llm import call_claude_json_with_search

CANADIAN_INVESTMENT_UNIVERSE = """
CANADIAN ETF / INDEX UNIVERSE (reference list — suggest from these when appropriate):
  EQUITY:
    XIU  – iShares S&P/TSX 60 (large-cap Canadian)
    XIC  – iShares Core S&P/TSX Capped Composite (broad Canadian)
    VFV  – Vanguard S&P 500 (CAD-hedged US large-cap)
    XUU  – iShares Core S&P US Total Market (US broad)
    ZSP  – BMO S&P 500 (CAD)
    XEF  – iShares Core MSCI EAFE (international developed)
    XEC  – iShares Core MSCI Emerging Markets
    VDY  – Vanguard FTSE Canadian High Dividend Yield
    CDZ  – iShares S&P/TSX Canadian Dividend Aristocrats
    XDV  – iShares Dow Jones Canada Select Dividend
  FIXED INCOME:
    XBB  – iShares Core Canadian Universe Bond
    ZAG  – BMO Aggregate Bond
    VSB  – Vanguard Canadian Short-Term Bond
    CLF  – iShares 1-5 Year Laddered Corporate Bond
    XHY  – iShares US High Yield Bond (CAD-hedged)
  BALANCED / ALL-IN-ONE:
    VBAL – Vanguard Balanced ETF Portfolio (60/40)
    VGRO – Vanguard Growth ETF Portfolio (80/20)
    VEQT – Vanguard All-Equity ETF Portfolio (100/0)
    XBAL – iShares Core Balanced (60/40)
    XGRO – iShares Core Growth (80/20)
  ALTERNATIVES / SECTOR:
    XRE  – iShares S&P/TSX Capped REIT (real estate)
    CGL  – iShares Gold Bullion (CAD-hedged)
    ZGI  – BMO Global Infrastructure
  GIC RATES (approximate):
    1-year GIC: ~4.5%   3-year GIC: ~4.0%   5-year GIC: ~3.8%
"""

SYSTEM_PROMPT = f"""\
You are the Researcher Agent in a Canadian wealth advisor's AI assistant called "FinanceOS."
Your job is to suggest suitable investment products and asset allocation strategies
based on the client's complete profile — risk tolerance, goals, accounts, life stage,
income, knowledge base notes, and the advisor's specific question.

{CANADIAN_INVESTMENT_UNIVERSE}

You have access to web search. Use it to look up current ETF performance, yields, MERs,
recent market conditions, GIC rates, and any relevant investment research.
This ensures your suggestions reflect the latest market data rather than stale information.

RULES:
- Match suggestions to the client's ACTUAL risk profile and goals from the data below.
- For conservative clients: emphasize bonds, GICs, dividend ETFs, balanced funds.
- For balanced clients: mix of equity and fixed income ETFs, consider all-in-one portfolios.
- For growth clients: higher equity allocation, broad market ETFs, some international.
- For aggressive clients: all-equity, include emerging markets, sector tilts.
- Consider the client's age, income, dependents, and province for tax efficiency.
- If the knowledge base mentions preferences (e.g., "prefers ETFs", "interested in dividends"), honor them.
- For RRSP: suggest tax-inefficient assets (bonds, REITs, US equities to avoid withholding tax).
- For TFSA: suggest highest-growth assets (equities) since gains are tax-free.
- For RESP: consider time horizon to education withdrawal.
- NEVER guarantee returns. Always frame as "may", "historically", "expected."
- When web search provides current data (yields, MERs, performance), reference it in your rationale.
- Be specific with ticker symbols and allocation percentages.
- Keep suggestions concise and actionable.

Respond in JSON:
{{
  "summary": "1-3 sentence overview of the investment thesis for this client",
  "suggestions": [
    {{
      "ticker": "ETF/product ticker or name",
      "name": "Full product name",
      "allocation_pct": 25,
      "rationale": "Why this fits the client (reference specific profile data)"
    }}
  ],
  "asset_mix": {{
    "equity_pct": 60,
    "fixed_income_pct": 30,
    "alternatives_pct": 10
  }},
  "account_strategy": "Which accounts to hold what and why (tax efficiency)"
}}"""


async def run_researcher_agent(
    client: dict,
    accounts: list[dict],
    documents: list[dict],
    recent_chat: list[dict],
    query: str,
    conn,
) -> dict:
    """Suggest suitable investments based on client profile via Claude with web search."""
    name = client["name"]
    income = client.get("employment_income", 0)
    province = client.get("province", "")
    risk = client.get("risk_profile", "")
    marital = client.get("marital_status", "")
    dependents = client.get("dependents", 0)
    goals = client.get("goals", [])
    notes = client.get("advisor_notes", "")
    dob = client.get("date_of_birth", "")
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

    user_message = f"""ADVISOR'S QUESTION: {query}

CLIENT PROFILE:
  Name: {name}
  Date of birth: {dob}
  Province: {province}
  Employment income: ${income:,.0f}
  Risk profile: {risk}
  Marital status: {marital}
  Dependents: {dependents}
  Goals: {json.dumps(goals)}
  Advisor notes: {notes}

CLIENT KNOWLEDGE BASE (advisor-curated context about this client):
{chr(10).join(rag_lines)}

ACCOUNTS (verified balances):
{chr(10).join(account_lines) if account_lines else '  No accounts on file.'}

TAX DOCUMENTS:
{chr(10).join(doc_lines) if doc_lines else '  No documents on file.'}

RECENT CONVERSATION:
{chr(10).join(chat_lines) if chat_lines else '  No prior conversations.'}
"""

    try:
        result = await call_claude_json_with_search(SYSTEM_PROMPT, user_message)
        if "suggestions" not in result:
            result["suggestions"] = []
        if "asset_mix" not in result:
            result["asset_mix"] = {"equity_pct": 0, "fixed_income_pct": 0, "alternatives_pct": 0}
        return result
    except Exception as e:
        return {
            "summary": f"Research encountered an issue: {str(e)[:100]}. Please review manually.",
            "suggestions": [],
            "asset_mix": {"equity_pct": 0, "fixed_income_pct": 0, "alternatives_pct": 0},
            "account_strategy": "",
        }
