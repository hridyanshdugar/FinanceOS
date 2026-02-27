from __future__ import annotations
from pydantic import BaseModel
from typing import Optional, Any


class Alert(BaseModel):
    id: str
    client_id: str
    alert_type: str
    title: str
    description: str
    drafted_action: Any = {}
    status: str = "pending"
    created_at: str = ""


class AlertActionRequest(BaseModel):
    action: str  # approved, rejected, dismissed
    note: str = ""
