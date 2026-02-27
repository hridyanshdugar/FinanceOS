"""
Researcher Agent: Fetches market data and macroeconomic context.
In the demo, this returns simulated market data.
"""
from __future__ import annotations

import asyncio


SIMULATED_MARKET_DATA = {
    "sp500": {"value": 5892.34, "change_pct": 0.42, "label": "S&P 500"},
    "tsx": {"value": 24156.78, "change_pct": -0.18, "label": "S&P/TSX Composite"},
    "cad_usd": {"value": 0.7342, "change_pct": -0.05, "label": "CAD/USD"},
    "boc_rate": {"value": 4.50, "change_pct": 0.0, "label": "BoC Policy Rate"},
    "cpi_yoy": {"value": 2.8, "change_pct": -0.1, "label": "CPI YoY (Canada)"},
    "oil_wti": {"value": 78.45, "change_pct": 1.2, "label": "WTI Crude"},
}


async def run_researcher_agent(query: str) -> dict:
    """Fetch relevant market data for the query context."""
    await asyncio.sleep(0.6)

    relevant = []
    query_lower = query.lower()

    if any(kw in query_lower for kw in ["rate", "mortgage", "interest", "bond"]):
        relevant.append(SIMULATED_MARKET_DATA["boc_rate"])
    if any(kw in query_lower for kw in ["stock", "portfolio", "equity", "market"]):
        relevant.append(SIMULATED_MARKET_DATA["sp500"])
        relevant.append(SIMULATED_MARKET_DATA["tsx"])
    if any(kw in query_lower for kw in ["oil", "energy", "suncor", "alberta"]):
        relevant.append(SIMULATED_MARKET_DATA["oil_wti"])
    if any(kw in query_lower for kw in ["inflation", "cpi", "price"]):
        relevant.append(SIMULATED_MARKET_DATA["cpi_yoy"])

    if not relevant:
        relevant = [
            SIMULATED_MARKET_DATA["tsx"],
            SIMULATED_MARKET_DATA["boc_rate"],
        ]

    return {
        "market_data": relevant,
        "summary": "Market data as of today (simulated for demo).",
    }
