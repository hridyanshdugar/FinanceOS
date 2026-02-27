from __future__ import annotations
from pydantic import BaseModel
from typing import Optional


class AgentActionRequest(BaseModel):
    task_id: str
    action: str  # approved, edited, rejected
    note: str = ""
    edited_content: Optional[str] = None
