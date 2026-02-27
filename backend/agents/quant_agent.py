"""
Quant Agent: Uses GPT-4o to perform financial calculations for Canadian clients.
Generates Python code, executes it in a sandbox, and returns results with formulas.
Never does math in plain text — always generates and runs code.
"""
from __future__ import annotations

import json
import subprocess
import tempfile
import os
from services.llm import call_gpt4o_json

SYSTEM_PROMPT = """\
You are the Quant Agent in a wealth advisor's AI assistant for Canadian clients.
Your job is to perform precise financial calculations based on the advisor's question
and the client's REAL financial data provided below.

ZERO-HALLUCINATION RULES:
- ONLY use numbers, balances, contribution rooms, and income figures from the data provided below.
- If a piece of data is not provided (e.g., a specific account balance, a contribution room), output "UNKNOWN" for that value. NEVER guess or make up numbers.
- All amounts are in Canadian dollars (CAD).
- Reference the client by name and cite specific account types and balances.

CANADIAN TAX RULES (2024):
- Federal brackets: $0-$55,867 at 15%, $55,867-$111,733 at 20.5%, $111,733-$173,675 at 26%, $173,675-$235,699 at 29%, $235,699+ at 33%
- RRSP annual limit: $31,560. TFSA limit: $7,000. FHSA annual: $8,000, lifetime: $40,000.
- CESG: 20% match on first $2,500/child/year, max $500/child/year, lifetime $7,200/child.
- HBP (Home Buyers' Plan): up to $35,000 RRSP withdrawal, must repay over 15 years.

CODE EXECUTION:
- Always generate complete, executable Python 3 code that performs the calculation.
- The code must print its results clearly with labels.
- Use only standard library modules (math, decimal, etc.) — no external packages.

Respond in JSON with this exact structure:
{
  "summary": "Plain-English summary of the key finding (1-3 sentences, cite specific $ amounts from the data)",
  "details": "Step-by-step explanation of the calculation referencing the client's actual numbers",
  "python_code": "Complete, executable Python 3 code that performs the calculation and prints results",
  "latex": "Key formula in LaTeX notation"
}"""


async def run_quant_agent(
    client: dict,
    accounts: list[dict],
    documents: list[dict],
    recent_chat: list[dict],
    query: str,
    conn,
) -> dict:
    """Run quantitative analysis via GPT-4o with code execution."""
    name = client["name"]
    income = client.get("employment_income", 0)
    province = client.get("province", "")
    risk = client.get("risk_profile", "")
    dependents = client.get("dependents", 0)
    goals = client.get("goals", [])
    marital = client.get("marital_status", "")
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

ACCOUNTS (verified balances from database):
{chr(10).join(account_lines) if account_lines else '  No accounts on file.'}

TAX DOCUMENTS:
{chr(10).join(doc_lines) if doc_lines else '  No documents on file.'}

RECENT CONVERSATION HISTORY:
{chr(10).join(chat_lines) if chat_lines else '  No prior conversations.'}
"""

    try:
        result = await call_gpt4o_json(SYSTEM_PROMPT, user_message)

        python_code = result.get("python_code", "")
        if python_code:
            execution_output = _execute_python_safely(python_code)
            if execution_output:
                result["details"] = result.get("details", "") + "\n\n--- Code Output ---\n" + execution_output

        return result
    except Exception as e:
        return {
            "summary": f"Calculation encountered an issue: {str(e)[:100]}. Please verify manually.",
            "details": str(e),
            "python_code": "",
            "latex": "",
        }


BLOCKED_IMPORTS = {"os", "subprocess", "sys", "shutil", "socket", "http", "urllib", "requests", "pathlib", "glob", "signal", "ctypes"}


def _execute_python_safely(code: str, timeout: int = 10) -> str:
    """Execute Python code in a restricted subprocess and capture output."""
    for mod in BLOCKED_IMPORTS:
        if f"import {mod}" in code or f"from {mod}" in code:
            return f"[Blocked: import of '{mod}' is not allowed in sandbox]"

    if "open(" in code or "__import__" in code or "eval(" in code or "exec(" in code:
        return "[Blocked: unsafe operation detected (open/eval/exec/__import__)]"

    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            tmp_path = f.name

        safe_env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "PYTHONDONTWRITEBYTECODE": "1",
            "HOME": "/tmp",
        }

        result = subprocess.run(
            ["python3", tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=safe_env,
        )

        os.unlink(tmp_path)

        output = result.stdout.strip()
        if result.stderr:
            output += "\n[stderr]: " + result.stderr.strip()
        return output
    except subprocess.TimeoutExpired:
        return "[Code execution timed out after 10 seconds]"
    except Exception as e:
        return f"[Execution error: {str(e)[:200]}]"
