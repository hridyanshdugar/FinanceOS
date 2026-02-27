from __future__ import annotations
from pydantic import BaseModel


class AlertActionRequest(BaseModel):
    action: str  # approved, rejected, dismissed
    note: str = ""
