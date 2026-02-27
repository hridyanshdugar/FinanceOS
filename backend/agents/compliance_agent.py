"""
Compliance Agent: Audits financial advice against CRA rules, CIRO regulations,
and Canadian tax law. Flags issues and validates contribution room limits.
"""
from __future__ import annotations

import asyncio


CRA_RULES = {
    "rrsp_limit_2024": 31560,
    "tfsa_limit_2024": 7000,
    "fhsa_annual_limit": 8000,
    "fhsa_lifetime_limit": 40000,
    "resp_cesg_annual_max_per_child": 500,
    "resp_cesg_lifetime_max_per_child": 7200,
    "oas_clawback_threshold_2024": 90997,
    "rrif_min_pct": {65: 0.04, 66: 0.0417, 67: 0.0435, 70: 0.05, 75: 0.0582, 80: 0.0682, 85: 0.0851, 90: 0.1111, 94: 0.1667, 95: 0.20},
}

PROHIBITED_TERMS = ["guaranteed returns", "guaranteed profit", "risk-free", "no risk", "can't lose"]


async def run_compliance_agent(
    client: dict,
    accounts: list[dict],
    query: str,
    conn,
) -> dict:
    """Check compliance for the given query and client context."""
    await asyncio.sleep(0.8)

    items = []
    query_lower = query.lower()
    income = client.get("employment_income", 0)
    province = client.get("province", "")
    dob = client.get("date_of_birth", "")

    age = _estimate_age(dob)

    # Check contribution room constraints
    for acct in accounts:
        acct_type = acct["type"]
        room = acct.get("contribution_room", 0)

        if acct_type == "RRSP" and room > CRA_RULES["rrsp_limit_2024"]:
            items.append({
                "severity": "info",
                "message": f"RRSP contribution room (${room:,.0f}) exceeds the 2024 annual limit (${CRA_RULES['rrsp_limit_2024']:,}). Room carries forward from prior years.",
                "rule_citation": "ITA 146(1) - RRSP deduction limit",
            })

        if acct_type == "FHSA" and room > 0:
            if "fhsa" in query_lower or "home" in query_lower:
                items.append({
                    "severity": "info",
                    "message": f"FHSA annual contribution limit is ${CRA_RULES['fhsa_annual_limit']:,}. Available room: ${room:,.0f}. Lifetime limit: ${CRA_RULES['fhsa_lifetime_limit']:,}.",
                    "rule_citation": "ITA 146.6 - Tax-Free First Home Savings Account",
                })

        if acct_type == "RESP" and ("resp" in query_lower or "cesg" in query_lower or "education" in query_lower):
            dependents = client.get("dependents", 1)
            items.append({
                "severity": "info",
                "message": f"CESG matches 20% on first $2,500/child/year (max ${CRA_RULES['resp_cesg_annual_max_per_child']:,}/child). With {dependents} {'child' if dependents == 1 else 'children'}, max annual CESG is ${CRA_RULES['resp_cesg_annual_max_per_child'] * dependents:,}.",
                "rule_citation": "Canada Education Savings Act s.5",
            })

    # OAS clawback check for seniors
    if age and age >= 65:
        total_income = income
        for acct in accounts:
            if acct["type"] == "RRIF":
                min_pct = _get_rrif_min_pct(age)
                total_income += acct["balance"] * min_pct
        if total_income > CRA_RULES["oas_clawback_threshold_2024"]:
            items.append({
                "severity": "warning",
                "message": f"Estimated total income (${total_income:,.0f}) exceeds the OAS clawback threshold (${CRA_RULES['oas_clawback_threshold_2024']:,}). OAS benefits may be reduced.",
                "rule_citation": "ITA 180.2 - OAS Recovery Tax",
            })

    # RRIF minimum withdrawal check
    if age and age >= 65:
        for acct in accounts:
            if acct["type"] == "RRIF":
                min_pct = _get_rrif_min_pct(age)
                min_withdrawal = acct["balance"] * min_pct
                items.append({
                    "severity": "info",
                    "message": f"RRIF minimum withdrawal for age {age}: {min_pct:.2%} of ${acct['balance']:,.0f} = ${min_withdrawal:,.0f}.",
                    "rule_citation": "ITA 146.3(1) - Minimum RRIF Withdrawal",
                })

    # Quebec-specific note
    if province == "QC":
        items.append({
            "severity": "info",
            "message": "Quebec tax rules apply (Revenu Québec). Provincial rates differ from federal and other provinces.",
            "rule_citation": "Taxation Act (Quebec) - Provincial income tax",
        })

    # Check for prohibited language
    for term in PROHIBITED_TERMS:
        if term in query_lower:
            items.append({
                "severity": "error",
                "message": f'Flagged term: "{term}". Advice must not imply guaranteed outcomes per CIRO suitability requirements.',
                "rule_citation": "CIRO Rule 3400 - Suitability",
            })

    status = "clear"
    if any(item["severity"] == "error" for item in items):
        status = "error"
    elif any(item["severity"] == "warning" for item in items):
        status = "warning"

    return {
        "status": status,
        "items": items,
    }


def _estimate_age(dob: str) -> int:
    """Estimate current age from date of birth string (YYYY-MM-DD)."""
    if not dob:
        return 0
    try:
        from datetime import date
        parts = dob.split("-")
        birth = date(int(parts[0]), int(parts[1]), int(parts[2]))
        today = date.today()
        return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    except Exception:
        return 0


def _get_rrif_min_pct(age: int) -> float:
    """Get RRIF minimum withdrawal percentage for a given age."""
    if age < 65:
        return 0.04
    pct_table = CRA_RULES["rrif_min_pct"]
    for threshold_age in sorted(pct_table.keys(), reverse=True):
        if age >= threshold_age:
            return pct_table[threshold_age]
    return 0.04
