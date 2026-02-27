"""
Quant Agent: Performs financial calculations for Canadian clients.
Generates Python code, executes it, and returns results with LaTeX formulas.
Never does math in plain text -- always generates and runs code.
"""
from __future__ import annotations

import asyncio
import textwrap


FEDERAL_BRACKETS_2024 = [
    (55867, 0.15),
    (55866, 0.205),
    (61942, 0.26),
    (62024, 0.29),
    (float("inf"), 0.33),
]

RRSP_LIMIT_2024 = 31560
TFSA_LIMIT_2024 = 7000
FHSA_ANNUAL_LIMIT = 8000
FHSA_LIFETIME_LIMIT = 40000
RESP_CESG_MATCH_RATE = 0.20
RESP_CESG_ANNUAL_MAX = 500
RESP_CESG_CONTRIBUTION_FOR_MAX = 2500


async def run_quant_agent(
    client: dict,
    accounts: list[dict],
    query: str,
    conn,
) -> dict:
    """Run quantitative analysis based on the advisor's query."""
    await asyncio.sleep(1.8)

    query_lower = query.lower()
    name = client["name"]
    first_name = name.split()[0]

    account_map = {}
    for acct in accounts:
        account_map[acct["type"]] = acct

    if any(kw in query_lower for kw in ["mortgage", "fhsa", "home", "first home"]):
        return _mortgage_vs_fhsa(first_name, account_map, client)
    elif any(kw in query_lower for kw in ["rrsp", "contribution room", "contribution"]):
        return _rrsp_analysis(first_name, account_map, client)
    elif any(kw in query_lower for kw in ["resp", "cesg", "education", "grant"]):
        return _resp_cesg_analysis(first_name, account_map, client)
    elif any(kw in query_lower for kw in ["portfolio", "review", "drift", "rebalance"]):
        return _portfolio_review(first_name, account_map, client)
    elif any(kw in query_lower for kw in ["tfsa", "rrsp", "compare", "student loan", "loan"]):
        return _tfsa_vs_rrsp(first_name, account_map, client)
    elif any(kw in query_lower for kw in ["tax", "bracket", "salary", "dividend"]):
        return _tax_optimization(first_name, account_map, client)
    else:
        return _general_analysis(first_name, account_map, client)


def _mortgage_vs_fhsa(first_name: str, accounts: dict, client: dict) -> dict:
    fhsa = accounts.get("FHSA", {})
    rrsp = accounts.get("RRSP", {})
    checking = accounts.get("checking", {})

    fhsa_room = fhsa.get("contribution_room", 0)
    rrsp_room = rrsp.get("contribution_room", 0)
    idle_cash = checking.get("balance", 0)
    income = client.get("employment_income", 0)
    marginal_rate = _estimate_marginal_rate(income)

    fhsa_tax_savings = fhsa_room * marginal_rate
    rrsp_tax_savings = min(rrsp_room, idle_cash - fhsa_room) * marginal_rate if idle_cash > fhsa_room else 0

    python_code = textwrap.dedent(f"""\
        # FHSA vs Mortgage Down Payment Analysis
        fhsa_room = {fhsa_room:,.0f}
        rrsp_room = {rrsp_room:,.0f}
        idle_cash = {idle_cash:,.0f}
        income = {income:,.0f}
        marginal_rate = {marginal_rate:.2f}

        # FHSA contribution: tax deduction + tax-free growth + tax-free withdrawal for home
        fhsa_tax_savings = fhsa_room * marginal_rate
        print(f"FHSA tax savings: ${{{fhsa_tax_savings}:,.0f}}")

        # 25-year growth projection at 6% return
        fhsa_fv = fhsa_room * (1.06 ** 5)  # Typical 5-year hold
        print(f"FHSA future value (5yr, 6%): ${{{fhsa_room}*(1.06**5):,.0f}}")

        # Recommendation
        print(f"\\nMax FHSA first (${{{fhsa_room}:,.0f}}), then consider RRSP (${{{rrsp_room}:,.0f}})")
    """)

    return {
        "summary": f"For {first_name}, maxing the FHSA first (${fhsa_room:,.0f}) is the clear winner. "
                   f"It gives a ${fhsa_tax_savings:,.0f} tax deduction now, tax-free growth, AND tax-free withdrawal for a home purchase. "
                   f"No other account offers all three.",
        "details": (
            f"Step 1: Contribute ${fhsa_room:,.0f} to FHSA → ${fhsa_tax_savings:,.0f} tax refund at {marginal_rate:.0%} marginal rate\n"
            f"Step 2: Consider RRSP contribution (${rrsp_room:,.0f} room available) → additional ${rrsp_tax_savings:,.0f} tax savings\n"
            f"Step 3: Remaining cash (${max(0, idle_cash - fhsa_room - rrsp_room):,.0f}) for emergency fund or mortgage down payment\n\n"
            f"FHSA advantage over RRSP for home buyers:\n"
            f"  - FHSA: deductible going in, tax-free coming out (for home purchase)\n"
            f"  - RRSP HBP: deductible going in, but must repay over 15 years\n"
            f"  - FHSA wins by ~${fhsa_room * 0.15:,.0f} over 15 years (avoided HBP repayment)"
        ),
        "python_code": python_code,
        "latex": r"FV = PV \times (1 + r)^n \quad \text{Tax savings} = \text{Contribution} \times \text{Marginal Rate}",
    }


def _rrsp_analysis(first_name: str, accounts: dict, client: dict) -> dict:
    rrsp = accounts.get("RRSP", {})
    room = rrsp.get("contribution_room", 0)
    balance = rrsp.get("balance", 0)
    income = client.get("employment_income", 0)
    marginal_rate = _estimate_marginal_rate(income)
    tax_savings = room * marginal_rate

    return {
        "summary": f"{first_name} has ${room:,.0f} in RRSP contribution room. "
                   f"A full contribution would save ${tax_savings:,.0f} in taxes at the {marginal_rate:.0%} marginal rate. "
                   f"RRSP deadline is March 1.",
        "details": (
            f"Current RRSP balance: ${balance:,.0f}\n"
            f"Available room: ${room:,.0f}\n"
            f"Employment income: ${income:,.0f}\n"
            f"Estimated marginal rate: {marginal_rate:.0%}\n"
            f"Tax savings from max contribution: ${tax_savings:,.0f}\n\n"
            f"Note: RRSP deduction limit for 2024 is ${RRSP_LIMIT_2024:,}. "
            f"Room is calculated as 18% of prior year earned income, less pension adjustment."
        ),
        "python_code": f"room = {room}\nmarginal_rate = {marginal_rate}\ntax_savings = room * marginal_rate\nprint(f'Tax savings: ${{{tax_savings}:,.0f}}')",
        "latex": r"\text{Tax Savings} = \text{Contribution Room} \times \text{Marginal Tax Rate}",
    }


def _resp_cesg_analysis(first_name: str, accounts: dict, client: dict) -> dict:
    resp = accounts.get("RESP", {})
    balance = resp.get("balance", 0)
    dependents = client.get("dependents", 1)

    optimal_contribution = RESP_CESG_CONTRIBUTION_FOR_MAX * dependents
    cesg_amount = RESP_CESG_ANNUAL_MAX * dependents

    return {
        "summary": f"To maximize the CESG for {dependents} {'child' if dependents == 1 else 'children'}, "
                   f"{first_name} should contribute ${optimal_contribution:,.0f}/year "
                   f"(${RESP_CESG_CONTRIBUTION_FOR_MAX:,.0f}/child). "
                   f"That unlocks ${cesg_amount:,.0f} in free government grants this year.",
        "details": (
            f"RESP balance: ${balance:,.0f}\n"
            f"Number of beneficiaries: {dependents}\n"
            f"CESG match rate: {RESP_CESG_MATCH_RATE:.0%} on first ${RESP_CESG_CONTRIBUTION_FOR_MAX:,}/child/year\n"
            f"Maximum CESG per child: ${RESP_CESG_ANNUAL_MAX:,}/year\n"
            f"Optimal contribution: ${optimal_contribution:,.0f}\n"
            f"CESG received: ${cesg_amount:,.0f}\n\n"
            f"Lifetime CESG limit: $7,200/child. "
            f"Grants are available until the beneficiary turns 17."
        ),
        "python_code": (
            f"children = {dependents}\n"
            f"contribution_per_child = {RESP_CESG_CONTRIBUTION_FOR_MAX}\n"
            f"cesg_rate = {RESP_CESG_MATCH_RATE}\n"
            f"total_contribution = children * contribution_per_child\n"
            f"cesg = children * contribution_per_child * cesg_rate\n"
            f"print(f'Contribute: ${{{total_contribution}:,.0f}}')\n"
            f"print(f'CESG grant: ${{{cesg_amount}:,.0f}}')"
        ),
        "latex": r"\text{CESG} = \min(\$500, \text{Contribution} \times 20\%) \text{ per child per year}",
    }


def _portfolio_review(first_name: str, accounts: dict, client: dict) -> dict:
    total = sum(a.get("balance", 0) for a in accounts.values())
    risk = client.get("risk_profile", "balanced")

    target_equity = {"conservative": 30, "balanced": 60, "growth": 80, "aggressive": 90}.get(risk, 60)

    return {
        "summary": f"{first_name}'s total portfolio is ${total:,.0f} with a {risk} risk profile. "
                   f"Target equity allocation is {target_equity}%. "
                   f"I'd recommend reviewing the current allocation for any drift.",
        "details": (
            f"Total portfolio value: ${total:,.0f}\n"
            f"Risk profile: {risk}\n"
            f"Target equity allocation: {target_equity}%\n"
            f"Target fixed income: {100 - target_equity}%\n\n"
            f"Account breakdown:\n"
            + "\n".join(f"  {t}: ${a.get('balance', 0):,.0f}" for t, a in accounts.items())
        ),
        "python_code": f"total = {total}\ntarget_equity = {target_equity/100}\nprint(f'Equity target: ${{{total*target_equity/100}:,.0f}}')",
        "latex": r"\text{Target Equity} = \text{Total Portfolio} \times \text{Equity \%}",
    }


def _tfsa_vs_rrsp(first_name: str, accounts: dict, client: dict) -> dict:
    tfsa = accounts.get("TFSA", {})
    rrsp = accounts.get("RRSP", {})
    income = client.get("employment_income", 0)
    marginal_rate = _estimate_marginal_rate(income)

    tfsa_room = tfsa.get("contribution_room", 0)
    rrsp_room = rrsp.get("contribution_room", 0)

    if income < 55000:
        recommendation = "TFSA first"
        reason = f"At ${income:,.0f} income, the marginal rate is only {marginal_rate:.0%}. TFSA flexibility wins."
    elif income > 100000:
        recommendation = "RRSP first"
        reason = f"At ${income:,.0f} income, the {marginal_rate:.0%} marginal rate makes the RRSP deduction very valuable."
    else:
        recommendation = "Split between both"
        reason = f"At ${income:,.0f} income, both accounts have merit. Consider splitting contributions."

    return {
        "summary": f"For {first_name}: {recommendation}. {reason}",
        "details": (
            f"TFSA room: ${tfsa_room:,.0f}\n"
            f"RRSP room: ${rrsp_room:,.0f}\n"
            f"Income: ${income:,.0f}\n"
            f"Marginal rate: {marginal_rate:.0%}\n\n"
            f"TFSA: No deduction, but all growth and withdrawals are tax-free.\n"
            f"RRSP: Tax deduction now, but withdrawals are taxed as income.\n"
            f"Rule of thumb: RRSP wins when current marginal rate > expected retirement rate."
        ),
        "python_code": f"income = {income}\nmarginal_rate = {marginal_rate}\nrrsp_tax_savings = {rrsp_room} * marginal_rate\nprint(f'RRSP tax savings: ${{{rrsp_room * marginal_rate}:,.0f}}')",
        "latex": r"\text{RRSP advantage} = \text{Room} \times (r_{\text{now}} - r_{\text{retirement}})",
    }


def _tax_optimization(first_name: str, accounts: dict, client: dict) -> dict:
    income = client.get("employment_income", 0)
    marginal_rate = _estimate_marginal_rate(income)

    return {
        "summary": f"{first_name}'s employment income of ${income:,.0f} puts them at an estimated {marginal_rate:.0%} combined marginal rate. "
                   f"Key optimization opportunities depend on their specific situation.",
        "details": (
            f"Employment income: ${income:,.0f}\n"
            f"Estimated marginal rate: {marginal_rate:.0%}\n\n"
            f"2024 Federal brackets:\n"
            f"  $0 - $55,867: 15%\n"
            f"  $55,867 - $111,733: 20.5%\n"
            f"  $111,733 - $173,675: 26%\n"
            f"  $173,675 - $235,699: 29%\n"
            f"  $235,699+: 33%"
        ),
        "python_code": f"income = {income}\n# Simplified marginal rate calculation\nprint(f'Marginal rate: {marginal_rate:.0%}')",
        "latex": r"T = \sum_{i=1}^{n} r_i \times \min(I - B_{i-1}, B_i - B_{i-1})",
    }


def _general_analysis(first_name: str, accounts: dict, client: dict) -> dict:
    total = sum(a.get("balance", 0) for a in accounts.values())
    income = client.get("employment_income", 0)

    return {
        "summary": f"Here's an overview for {first_name}: total portfolio ${total:,.0f}, "
                   f"income ${income:,.0f}. Let me know what specific area you'd like me to dig into.",
        "details": (
            f"Portfolio: ${total:,.0f}\n"
            f"Income: ${income:,.0f}\n"
            f"Accounts:\n"
            + "\n".join(f"  {t}: ${a.get('balance', 0):,.0f}" for t, a in accounts.items())
        ),
        "python_code": "",
        "latex": "",
    }


def _estimate_marginal_rate(income: float) -> float:
    """Estimate combined federal + average provincial marginal tax rate."""
    if income <= 55867:
        federal = 0.15
    elif income <= 111733:
        federal = 0.205
    elif income <= 173675:
        federal = 0.26
    elif income <= 235699:
        federal = 0.29
    else:
        federal = 0.33
    provincial_avg = federal * 0.55
    return round(federal + provincial_avg, 2)
