"""
Shadow Backtest: Background scanner that proactively identifies
opportunities and risks across all client accounts.
Runs periodically and generates alerts with pre-drafted outreach emails.
"""
from __future__ import annotations

import json
import uuid
import asyncio
from datetime import datetime, date

from db.database import get_connection, dicts_from_rows


IDLE_CASH_THRESHOLD = 10000
RRSP_DEADLINE_MONTH = 3  # March
RRSP_DEADLINE_DAY = 1


async def run_shadow_backtest():
    """Scan all clients for proactive opportunities. Returns list of new alerts."""
    conn = get_connection()
    clients = dicts_from_rows(conn.execute("SELECT * FROM clients").fetchall())
    new_alerts = []

    for client in clients:
        client_id = client["id"]
        name = client["name"]
        first_name = name.split()[0]
        goals = json.loads(client["goals"]) if client["goals"] else []
        income = client.get("employment_income", 0)
        dob = client.get("date_of_birth", "")
        age = _estimate_age(dob)

        accounts = dicts_from_rows(
            conn.execute("SELECT * FROM accounts WHERE client_id = ?", (client_id,)).fetchall()
        )

        existing_alerts = dicts_from_rows(
            conn.execute(
                "SELECT alert_type FROM alerts WHERE client_id = ? AND status = 'pending'",
                (client_id,),
            ).fetchall()
        )
        existing_types = {a["alert_type"] for a in existing_alerts}

        account_map = {a["type"]: a for a in accounts}

        # 1. Idle cash check
        for acct in accounts:
            if acct["type"] in ("checking", "savings") and acct["balance"] > IDLE_CASH_THRESHOLD:
                if "idle_cash" not in existing_types:
                    tax_advantaged = []
                    for t in ["FHSA", "TFSA", "RRSP"]:
                        if t in account_map and account_map[t].get("contribution_room", 0) > 0:
                            tax_advantaged.append(f"{t} (${account_map[t]['contribution_room']:,.0f} room)")

                    if tax_advantaged:
                        alert = _create_alert(
                            client_id, "idle_cash",
                            f"Idle cash in {acct['label'] or acct['type']}",
                            f"{first_name} has ${acct['balance']:,.0f} in their {acct['label'] or acct['type']}. "
                            f"Available tax-advantaged room: {', '.join(tax_advantaged)}.",
                            _draft_idle_cash_email(first_name, name, acct["balance"], tax_advantaged),
                        )
                        new_alerts.append(alert)
                        existing_types.add("idle_cash")

        # 2. RRSP deadline approaching
        today = date.today()
        if today.month in (1, 2) and "RRSP" in account_map:
            rrsp_room = account_map["RRSP"].get("contribution_room", 0)
            if rrsp_room > 0 and "rrsp_deadline" not in existing_types:
                alert = _create_alert(
                    client_id, "rrsp_deadline",
                    "RRSP deadline approaching",
                    f"{first_name} has ${rrsp_room:,.0f} in unused RRSP room. "
                    f"The contribution deadline for the current tax year is March 1.",
                    _draft_rrsp_deadline_email(first_name, name, rrsp_room),
                )
                new_alerts.append(alert)

        # 3. RESP CESG optimization
        dependents = client.get("dependents", 0)
        if dependents > 0 and "RESP" in account_map:
            resp = account_map["RESP"]
            if resp["balance"] < 2500 * dependents and "cesg_optimization" not in existing_types:
                optimal = 2500 * dependents
                cesg = 500 * dependents
                alert = _create_alert(
                    client_id, "cesg_optimization",
                    f"RESP: maximize CESG for {'child' if dependents == 1 else f'{dependents} children'}",
                    f"To get the maximum ${cesg:,} in CESG grants, {first_name} should contribute "
                    f"${optimal:,} ($2,500/child) before December 31.",
                    _draft_cesg_email(first_name, name, optimal, cesg, dependents),
                )
                new_alerts.append(alert)

        # 4. OAS clawback risk for seniors
        if age >= 65 and "oas_clawback" not in existing_types:
            rrif = account_map.get("RRIF", {})
            pension_income = income
            if rrif:
                min_pct = _get_rrif_min_pct(age)
                pension_income += rrif.get("balance", 0) * min_pct

            if pension_income > 90997:
                alert = _create_alert(
                    client_id, "oas_clawback",
                    "OAS clawback risk",
                    f"{first_name}'s estimated income (${pension_income:,.0f}) exceeds the OAS clawback threshold ($90,997). "
                    f"Consider income splitting or TFSA strategies to reduce the clawback.",
                    _draft_oas_email(first_name, name, pension_income),
                )
                new_alerts.append(alert)

        # 5. RRIF minimum withdrawal
        if age >= 65 and "RRIF" in account_map and "rrif_minimum" not in existing_types:
            rrif = account_map["RRIF"]
            min_pct = _get_rrif_min_pct(age)
            min_withdrawal = rrif["balance"] * min_pct
            alert = _create_alert(
                client_id, "rrif_minimum",
                "RRIF minimum withdrawal due",
                f"{first_name}'s RRIF minimum withdrawal for this year: ${min_withdrawal:,.0f} "
                f"({min_pct:.2%} of ${rrif['balance']:,.0f}). Must be withdrawn by December 31.",
                None,
            )
            new_alerts.append(alert)

    # Save new alerts
    for alert in new_alerts:
        conn.execute(
            "INSERT INTO alerts (id, client_id, alert_type, title, description, drafted_action, status, created_at) VALUES (?,?,?,?,?,?,?,?)",
            (alert["id"], alert["client_id"], alert["alert_type"], alert["title"],
             alert["description"], json.dumps(alert.get("drafted_action", {})),
             "pending", alert["created_at"]),
        )
    conn.commit()
    conn.close()

    return new_alerts


def _create_alert(client_id: str, alert_type: str, title: str, description: str, drafted_action) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "client_id": client_id,
        "alert_type": alert_type,
        "title": title,
        "description": description,
        "drafted_action": drafted_action or {},
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }


def _draft_idle_cash_email(first_name, full_name, amount, tax_advantaged):
    return {
        "type": "email_draft",
        "to": full_name,
        "subject": "Quick thought on your savings",
        "body": (
            f"Hi {first_name},\n\n"
            f"I noticed you have about ${amount:,.0f} in your chequing account. "
            f"You still have room in some tax-advantaged accounts that could help your money grow faster:\n\n"
            f"{''.join(f'  - {t}' + chr(10) for t in tax_advantaged)}\n"
            f"Would you like to discuss moving some of those funds? It could make a meaningful difference come tax time.\n\n"
            f"Best,\nAlex"
        ),
    }


def _draft_rrsp_deadline_email(first_name, full_name, room):
    return {
        "type": "email_draft",
        "to": full_name,
        "subject": "RRSP deadline reminder - March 1",
        "body": (
            f"Hi {first_name},\n\n"
            f"Quick reminder: the RRSP contribution deadline for this tax year is March 1. "
            f"You have ${room:,.0f} in available room.\n\n"
            f"Contributing before the deadline means you can claim the deduction on this year's taxes. "
            f"Want me to put together a plan?\n\n"
            f"Best,\nAlex"
        ),
    }


def _draft_cesg_email(first_name, full_name, contribution, cesg, children):
    return {
        "type": "email_draft",
        "to": full_name,
        "subject": "Free money for education savings",
        "body": (
            f"Hi {first_name},\n\n"
            f"I wanted to flag something before year-end: if you contribute ${contribution:,} to the RESP "
            f"($2,500 per child), the government matches 20% through the CESG program. "
            f"That's ${cesg:,} in free grants.\n\n"
            f"This is one of the best guaranteed returns available. Would you like to set this up?\n\n"
            f"Best,\nAlex"
        ),
    }


def _draft_oas_email(first_name, full_name, income):
    return {
        "type": "email_draft",
        "to": full_name,
        "subject": "Strategy to protect your OAS benefits",
        "body": (
            f"Hi {first_name},\n\n"
            f"I've been reviewing your income situation and wanted to flag something: "
            f"your estimated income of ${income:,.0f} puts you above the OAS clawback threshold ($90,997). "
            f"This means some of your OAS benefits may be reduced.\n\n"
            f"There are strategies we can explore — like pension income splitting with your spouse "
            f"or using your TFSA more strategically. Want to discuss?\n\n"
            f"Best,\nAlex"
        ),
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
    table = {65: 0.04, 66: 0.0417, 67: 0.0435, 70: 0.05, 75: 0.0582, 80: 0.0682}
    for threshold_age in sorted(table.keys(), reverse=True):
        if age >= threshold_age:
            return table[threshold_age]
    return 0.04
