from __future__ import annotations
import json
from fastapi import APIRouter, HTTPException
from db.database import get_connection, dicts_from_rows
from models.alert import AlertActionRequest

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.post("/scan")
async def trigger_backtest() -> dict:
    from services.shadow_backtest import run_shadow_backtest
    new_alerts = await run_shadow_backtest()
    return {"new_alerts": len(new_alerts)}


@router.get("")
def list_alerts(status: str = "pending") -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        """SELECT a.*, c.name as client_name
           FROM alerts a JOIN clients c ON a.client_id = c.id
           WHERE a.status = ?
           ORDER BY a.created_at DESC""",
        (status,),
    ).fetchall()
    alerts = dicts_from_rows(rows)
    for alert in alerts:
        alert["drafted_action"] = json.loads(alert["drafted_action"]) if alert["drafted_action"] else {}
    conn.close()
    return alerts


@router.post("/{alert_id}/action")
def act_on_alert(alert_id: str, req: AlertActionRequest) -> dict:
    conn = get_connection()
    row = conn.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Alert not found")

    conn.execute(
        "UPDATE alerts SET status = ? WHERE id = ?",
        (req.action, alert_id),
    )
    conn.commit()
    conn.close()
    return {"status": "ok", "alert_id": alert_id, "action": req.action}
