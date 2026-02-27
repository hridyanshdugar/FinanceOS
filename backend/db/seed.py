"""Seed the database with 8 diverse Canadian client profiles."""

import json
import uuid
from datetime import datetime, timedelta
from db.database import get_connection, init_db


def _id() -> str:
    return str(uuid.uuid4())


def seed():
    init_db()
    conn = get_connection()
    cur = conn.cursor()

    # Check if already seeded
    cur.execute("SELECT COUNT(*) FROM clients")
    if cur.fetchone()[0] > 0:
        conn.close()
        return

    now = datetime.now().isoformat()

    # ── Client 1: Sarah Chen ────────────────────────────────────────────
    sarah_id = _id()
    cur.execute(
        """INSERT INTO clients (id, name, email, phone, province, sin_last4, date_of_birth,
           risk_profile, goals, marital_status, dependents, employment_income, employer, onboarded_at, advisor_notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (sarah_id, "Sarah Chen", "sarah.chen@email.com", "416-555-0123", "ON", "4821",
         "1994-06-15", "growth",
         json.dumps(["Buy a cottage near Lake Muskoka", "Max FHSA before first home purchase", "Build long-term wealth"]),
         "single", 0, 145000, "Shopify", now,
         "Very engaged client. Asks detailed questions. Prefers email communication. First-time home buyer."),
    )
    sarah_accounts = [
        (_id(), sarah_id, "TFSA", "TFSA", 42000, 7000, now),
        (_id(), sarah_id, "FHSA", "FHSA", 16000, 8000, now),
        (_id(), sarah_id, "RRSP", "RRSP", 28000, 18500, now),
        (_id(), sarah_id, "checking", "TD Chequing", 23500, 0, now),
    ]
    for a in sarah_accounts:
        cur.execute("INSERT INTO accounts (id, client_id, type, label, balance, contribution_room, last_updated) VALUES (?,?,?,?,?,?,?)", a)

    cur.execute("INSERT INTO documents (id, client_id, type, content_text, tax_year, uploaded_at) VALUES (?,?,?,?,?,?)",
                (_id(), sarah_id, "T4", "Employer: Shopify Inc. Employment income: $145,000. CPP contributions: $3,867. EI premiums: $1,049. Income tax deducted: $32,450.", 2024, now))
    cur.execute("INSERT INTO documents (id, client_id, type, content_text, tax_year, uploaded_at) VALUES (?,?,?,?,?,?)",
                (_id(), sarah_id, "NOA", "Total income: $145,000. Taxable income: $131,500. RRSP deduction limit: $18,500. TFSA room: $7,000. Federal tax: $22,180. Ontario tax: $10,270.", 2024, now))

    cur.execute("INSERT INTO chat_history (id, client_id, role, content, created_at) VALUES (?,?,?,?,?)",
                (_id(), sarah_id, "client", "I've been thinking about buying my first home. Should I keep putting money into my FHSA or start saving in my RRSP? I also have about $23K just sitting in my chequing account.", (datetime.now() - timedelta(days=2)).isoformat()))
    cur.execute("INSERT INTO chat_history (id, client_id, role, content, created_at) VALUES (?,?,?,?,?)",
                (_id(), sarah_id, "advisor", "Great question Sarah! Let me look into the numbers on FHSA vs RRSP for your situation. The FHSA is particularly interesting since you're a first-time buyer. I'll put together an analysis.", (datetime.now() - timedelta(days=2, hours=-1)).isoformat()))

    # ── Client 2: James Park ────────────────────────────────────────────
    james_id = _id()
    cur.execute(
        """INSERT INTO clients (id, name, email, phone, province, sin_last4, date_of_birth,
           risk_profile, goals, marital_status, dependents, employment_income, employer, onboarded_at, advisor_notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (james_id, "James Park", "james.park@parkdental.ca", "604-555-0456", "BC", "7193",
         "1973-09-22", "balanced",
         json.dumps(["Retire at 60", "Fund daughter's UBC tuition via RESP", "Income splitting with spouse", "Minimize corporate tax"]),
         "married", 1, 310000, "Self-employed (Park Dental)", now,
         "Self-employed dentist. Incorporated. Spouse Lisa is a homemaker. Daughter Emily, age 16, starting UBC in 2 years."),
    )
    james_accounts = [
        (_id(), james_id, "RRSP", "Personal RRSP", 485000, 52000, now),
        (_id(), james_id, "TFSA", "TFSA", 88000, 0, now),
        (_id(), james_id, "RESP", "Emily RESP", 62000, 0, now),
        (_id(), james_id, "corporate", "Park Dental Corp Investment", 220000, 0, now),
        (_id(), james_id, "checking", "Business Chequing", 45000, 0, now),
    ]
    for a in james_accounts:
        cur.execute("INSERT INTO accounts (id, client_id, type, label, balance, contribution_room, last_updated) VALUES (?,?,?,?,?,?,?)", a)

    cur.execute("INSERT INTO documents (id, client_id, type, content_text, tax_year, uploaded_at) VALUES (?,?,?,?,?,?)",
                (_id(), james_id, "T4A", "Self-employment income: $310,000. Professional income from Park Dental Inc.", 2024, now))
    cur.execute("INSERT INTO documents (id, client_id, type, content_text, tax_year, uploaded_at) VALUES (?,?,?,?,?,?)",
                (_id(), james_id, "T2", "Corporate net income: $220,000. Small business deduction applied. Corporate tax payable: $27,500.", 2024, now))

    # ── Client 3: Priya Sharma ──────────────────────────────────────────
    priya_id = _id()
    cur.execute(
        """INSERT INTO clients (id, name, email, phone, province, sin_last4, date_of_birth,
           risk_profile, goals, marital_status, dependents, employment_income, employer, onboarded_at, advisor_notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (priya_id, "Priya Sharma", "priya.sharma@email.com", "403-555-0789", "AB", "3456",
         "1997-03-10", "aggressive",
         json.dumps(["Early retirement (FIRE)", "Aggressive savings rate (60%+)", "Considering rental property in Edmonton"]),
         "single", 0, 118000, "Suncor Energy", now,
         "FIRE enthusiast. Very financially literate. Tracks every dollar. Prefers data-heavy analysis. No Alberta provincial tax advantage awareness needed - she knows."),
    )
    priya_accounts = [
        (_id(), priya_id, "TFSA", "TFSA", 55000, 0, now),
        (_id(), priya_id, "RRSP", "RRSP", 38000, 22000, now),
        (_id(), priya_id, "non_registered", "Non-Registered Investment", 67000, 0, now),
        (_id(), priya_id, "savings", "High-Interest Savings", 31000, 0, now),
    ]
    for a in priya_accounts:
        cur.execute("INSERT INTO accounts (id, client_id, type, label, balance, contribution_room, last_updated) VALUES (?,?,?,?,?,?,?)", a)

    cur.execute("INSERT INTO documents (id, client_id, type, content_text, tax_year, uploaded_at) VALUES (?,?,?,?,?,?)",
                (_id(), priya_id, "T4", "Employer: Suncor Energy. Employment income: $118,000. CPP: $3,867. EI: $1,049.", 2024, now))
    cur.execute("INSERT INTO documents (id, client_id, type, content_text, tax_year, uploaded_at) VALUES (?,?,?,?,?,?)",
                (_id(), priya_id, "T5", "Investment income: $4,200 (dividends: $2,800, interest: $1,400). Capital gains realized: $8,500.", 2024, now))

    # ── Client 4: Michel Tremblay ───────────────────────────────────────
    michel_id = _id()
    cur.execute(
        """INSERT INTO clients (id, name, email, phone, province, sin_last4, date_of_birth,
           risk_profile, goals, marital_status, dependents, employment_income, employer, onboarded_at, advisor_notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (michel_id, "Michel Tremblay", "michel.tremblay@videotron.ca", "514-555-0321", "QC", "8834",
         "1958-11-03", "conservative",
         json.dumps(["Minimize tax on RRIF withdrawals", "Maximize OAS/GIS", "Leave inheritance for 3 grandchildren"]),
         "married", 0, 0, "Retired (formerly CSDM teacher)", now,
         "Retired teacher. Pension from RREGOP. Wife Claudette, age 65. 3 grandchildren. Prefers French but comfortable in English. Quebec tax rules apply (Revenu Québec)."),
    )
    michel_accounts = [
        (_id(), michel_id, "RRIF", "RRIF (converted from RRSP)", 340000, 0, now),
        (_id(), michel_id, "TFSA", "TFSA", 95000, 0, now),
        (_id(), michel_id, "non_registered", "Joint Non-Registered", 120000, 0, now),
        (_id(), michel_id, "LIF", "LIF (from LIRA)", 85000, 0, now),
    ]
    for a in michel_accounts:
        cur.execute("INSERT INTO accounts (id, client_id, type, label, balance, contribution_room, last_updated) VALUES (?,?,?,?,?,?,?)", a)

    cur.execute("INSERT INTO documents (id, client_id, type, content_text, tax_year, uploaded_at) VALUES (?,?,?,?,?,?)",
                (_id(), michel_id, "T4A", "RREGOP pension income: $52,000/year. Quebec pension plan.", 2024, now))
    cur.execute("INSERT INTO documents (id, client_id, type, content_text, tax_year, uploaded_at) VALUES (?,?,?,?,?,?)",
                (_id(), michel_id, "T4RIF", "RRIF withdrawals: $18,200 (minimum withdrawal for age 66). Withholding tax: $3,640.", 2024, now))

    # ── Client 5: Aisha Hassan ──────────────────────────────────────────
    aisha_id = _id()
    cur.execute(
        """INSERT INTO clients (id, name, email, phone, province, sin_last4, date_of_birth,
           risk_profile, goals, marital_status, dependents, employment_income, employer, onboarded_at, advisor_notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (aisha_id, "Aisha Hassan", "aisha.hassan@email.com", "613-555-0654", "ON", "5567",
         "1986-08-20", "balanced",
         json.dumps(["Pay off mortgage on Barrhaven home in 10 years", "Start RESP for newborn twins", "Build emergency fund"]),
         "married", 2, 96000, "Canada Revenue Agency (CRA)", now,
         "Federal government employee. Spouse Yusuf works at DND, earns $88,000. Newborn twins born 3 months ago. Mortgage: $420,000 remaining at 5.2%. Just opened RESP."),
    )
    aisha_accounts = [
        (_id(), aisha_id, "RRSP", "RRSP", 72000, 14000, now),
        (_id(), aisha_id, "TFSA", "TFSA", 35000, 14000, now),
        (_id(), aisha_id, "RESP", "Twins RESP (family plan)", 0, 0, now),
        (_id(), aisha_id, "checking", "Joint Chequing", 18000, 0, now),
    ]
    for a in aisha_accounts:
        cur.execute("INSERT INTO accounts (id, client_id, type, label, balance, contribution_room, last_updated) VALUES (?,?,?,?,?,?,?)", a)

    cur.execute("INSERT INTO documents (id, client_id, type, content_text, tax_year, uploaded_at) VALUES (?,?,?,?,?,?)",
                (_id(), aisha_id, "T4", "Employer: Canada Revenue Agency. Employment income: $96,000. Pension adjustment: $8,400.", 2024, now))

    cur.execute("INSERT INTO chat_history (id, client_id, role, content, created_at) VALUES (?,?,?,?,?)",
                (_id(), aisha_id, "client", "We just had twins! We opened an RESP but I'm not sure how much to contribute to get the maximum grant. Can you help?", (datetime.now() - timedelta(days=5)).isoformat()))

    # ── Client 6: David Okafor ──────────────────────────────────────────
    david_id = _id()
    cur.execute(
        """INSERT INTO clients (id, name, email, phone, province, sin_last4, date_of_birth,
           risk_profile, goals, marital_status, dependents, employment_income, employer, onboarded_at, advisor_notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (david_id, "David Okafor", "david@okaforrestaurants.ca", "204-555-0987", "MB", "2290",
         "1980-04-12", "growth",
         json.dumps(["Open 4th restaurant location", "Corporate tax optimization", "Spousal RRSP contributions", "Build passive income"]),
         "married", 3, 195000, "Self-employed (Okafor Restaurants)", now,
         "Restaurant chain owner (3 locations in Winnipeg). Wife Ngozi handles bookkeeping. Corporate income $280K. Considering 4th location on Portage Ave. 3 kids ages 8, 11, 14."),
    )
    david_accounts = [
        (_id(), david_id, "RRSP", "Personal RRSP", 110000, 35000, now),
        (_id(), david_id, "spousal_rrsp", "Spousal RRSP (Ngozi)", 45000, 0, now),
        (_id(), david_id, "TFSA", "TFSA", 88000, 0, now),
        (_id(), david_id, "corporate", "Okafor Restaurants Corp", 380000, 0, now),
        (_id(), david_id, "checking", "Business Operating", 92000, 0, now),
    ]
    for a in david_accounts:
        cur.execute("INSERT INTO accounts (id, client_id, type, label, balance, contribution_room, last_updated) VALUES (?,?,?,?,?,?,?)", a)

    cur.execute("INSERT INTO documents (id, client_id, type, content_text, tax_year, uploaded_at) VALUES (?,?,?,?,?,?)",
                (_id(), david_id, "T2", "Okafor Restaurants Inc. Net corporate income: $280,000. Active business income eligible for SBD. Corporate tax: $35,000.", 2024, now))
    cur.execute("INSERT INTO documents (id, client_id, type, content_text, tax_year, uploaded_at) VALUES (?,?,?,?,?,?)",
                (_id(), david_id, "T5", "Eligible dividends paid: $85,000. Non-eligible dividends: $42,000.", 2024, now))

    # ── Client 7: Emily Lawson ──────────────────────────────────────────
    emily_id = _id()
    cur.execute(
        """INSERT INTO clients (id, name, email, phone, province, sin_last4, date_of_birth,
           risk_profile, goals, marital_status, dependents, employment_income, employer, onboarded_at, advisor_notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (emily_id, "Emily Lawson", "emily.lawson@email.com", "902-555-0135", "NS", "6712",
         "2001-12-05", "growth",
         json.dumps(["Pay off $28K student loan (NSLSC)", "Build emergency fund", "Start investing for long-term"]),
         "single", 0, 62000, "Clearwater Seafoods", now,
         "New grad, first real job. $28K NSLSC student loan at 4.5%. No financial literacy background but very eager to learn. Needs basics explained clearly."),
    )
    emily_accounts = [
        (_id(), emily_id, "TFSA", "TFSA", 4500, 40500, now),
        (_id(), emily_id, "RRSP", "RRSP", 0, 8200, now),
        (_id(), emily_id, "checking", "Chequing", 3200, 0, now),
        (_id(), emily_id, "savings", "Savings", 1800, 0, now),
    ]
    for a in emily_accounts:
        cur.execute("INSERT INTO accounts (id, client_id, type, label, balance, contribution_room, last_updated) VALUES (?,?,?,?,?,?,?)", a)

    cur.execute("INSERT INTO documents (id, client_id, type, content_text, tax_year, uploaded_at) VALUES (?,?,?,?,?,?)",
                (_id(), emily_id, "T4", "Employer: Clearwater Seafoods. Employment income: $62,000. First full year of employment.", 2024, now))

    cur.execute("INSERT INTO chat_history (id, client_id, role, content, created_at) VALUES (?,?,?,?,?)",
                (_id(), emily_id, "client", "I just started my first real job and I have no idea where to begin with saving. I have $28K in student loans. Should I pay that off first or start investing? What's the difference between a TFSA and RRSP?", (datetime.now() - timedelta(days=7)).isoformat()))
    cur.execute("INSERT INTO chat_history (id, client_id, role, content, created_at) VALUES (?,?,?,?,?)",
                (_id(), emily_id, "advisor", "Welcome Emily! These are exactly the right questions to be asking. Let me break it down simply. At your income level in Nova Scotia, there's actually a clear best path. Let me run the numbers for you.", (datetime.now() - timedelta(days=7, hours=-2)).isoformat()))

    # ── Client 8: Wei Zhang ─────────────────────────────────────────────
    wei_id = _id()
    cur.execute(
        """INSERT INTO clients (id, name, email, phone, province, sin_last4, date_of_birth,
           risk_profile, goals, marital_status, dependents, employment_income, employer, onboarded_at, advisor_notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (wei_id, "Wei Zhang", "wei.zhang@importexport.ca", "604-555-0246", "BC", "9105",
         "1970-07-28", "balanced",
         json.dumps(["Transition rental properties to passive investments", "Estate planning for 2 adult children in Toronto", "Lifetime capital gains exemption planning"]),
         "married", 2, 175000, "Self-employed (Zhang Import/Export)", now,
         "Complex client. Real estate investor (3 rental properties in Richmond). Import/export business via holding company. 2 adult children (Kevin 28, Lisa 25) in Toronto. Estate planning priority. Wife Min, age 53."),
    )
    wei_accounts = [
        (_id(), wei_id, "RRSP", "RRSP", 290000, 8000, now),
        (_id(), wei_id, "TFSA", "TFSA", 88000, 0, now),
        (_id(), wei_id, "non_registered", "Non-Registered Portfolio", 520000, 0, now),
        (_id(), wei_id, "LIRA", "LIRA (former employer)", 65000, 0, now),
        (_id(), wei_id, "corporate", "Zhang Holdings Corp", 1200000, 0, now),
    ]
    for a in wei_accounts:
        cur.execute("INSERT INTO accounts (id, client_id, type, label, balance, contribution_room, last_updated) VALUES (?,?,?,?,?,?,?)", a)

    cur.execute("INSERT INTO documents (id, client_id, type, content_text, tax_year, uploaded_at) VALUES (?,?,?,?,?,?)",
                (_id(), wei_id, "T776", "Rental income: 3 properties in Richmond BC. Gross rental: $84,000. Net rental after expenses: $31,000.", 2024, now))
    cur.execute("INSERT INTO documents (id, client_id, type, content_text, tax_year, uploaded_at) VALUES (?,?,?,?,?,?)",
                (_id(), wei_id, "T2", "Zhang Holdings Corp. Net income: $420,000. Passive investment income: $180,000. Active business income: $240,000.", 2024, now))

    # ── Proactive Alerts (pre-seeded) ───────────────────────────────────
    cur.execute(
        "INSERT INTO alerts (id, client_id, alert_type, title, description, drafted_action, status, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (_id(), sarah_id, "idle_cash", "Idle cash in chequing account",
         "Sarah has $23,500 sitting in her TD Chequing account. Her FHSA has $8,000 in contribution room and the RRSP deadline is approaching March 1. Consider moving funds to maximize tax-advantaged accounts.",
         json.dumps({"type": "email_draft", "subject": "Quick thought on your savings",
                     "body": "Hi Sarah,\n\nI was reviewing your accounts and noticed you have about $23,500 in your chequing account. Given your goal of buying your first home, I think we should talk about topping up your FHSA (you have $8,000 in room) before the end of the year. This would give you both the tax deduction now and tax-free growth for your future home.\n\nWould you have 15 minutes this week to chat?\n\nBest,\nAlex"}),
         "pending", now)),

    cur.execute(
        "INSERT INTO alerts (id, client_id, alert_type, title, description, drafted_action, status, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (_id(), james_id, "portfolio_drift", "Portfolio drift: tech overweight",
         "James's portfolio has drifted to 42% tech allocation after the recent rally, above his 30% target for a balanced risk profile. Consider rebalancing into fixed income or Canadian dividend stocks.",
         json.dumps({"type": "rebalance_suggestion", "current_tech_pct": 42, "target_tech_pct": 30}),
         "pending", now)),

    cur.execute(
        "INSERT INTO alerts (id, client_id, alert_type, title, description, drafted_action, status, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (_id(), aisha_id, "cesg_optimization", "RESP: maximize CESG for twins",
         "Aisha's family RESP has $0. To maximize the Canada Education Savings Grant ($500/child/year), she should contribute $2,500 per child ($5,000 total) before December 31. That's $1,000 in free government money.",
         json.dumps({"type": "email_draft", "subject": "Free money for the twins' education",
                     "body": "Hi Aisha,\n\nCongratulations again on the twins! I wanted to flag something time-sensitive: if you contribute $2,500 per child to the RESP before year-end, the government will match 20% — that's $1,000 in free grants through the CESG program.\n\nThe total contribution would be $5,000. Would you like me to set this up?\n\nBest,\nAlex"}),
         "pending", now)),

    conn.commit()
    conn.close()


if __name__ == "__main__":
    seed()
    print("Database seeded successfully.")
