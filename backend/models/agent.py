from __future__ import annotations
from pydantic import BaseModel
from typing import Optional, Any


class AgentTask(BaseModel):
    id: str
    client_id: Optional[str] = None
    agent_type: str
    status: str = "pending"
    input_data: Any = {}
    output_data: Any = {}
    advisor_action: Optional[str] = None
    advisor_note: str = ""
    created_at: str = ""
    completed_at: Optional[str] = None


class AgentDispatchRequest(BaseModel):
    client_id: str
    query: str


class AgentActionRequest(BaseModel):
    task_id: str
    action: str  # approved, edited, rejected
    note: str = ""
    edited_content: Optional[str] = None


class WSMessage(BaseModel):
    type: str  # agent_dispatch, agent_update, agent_complete, alert_new, error, chat_response
    agent: Optional[str] = None
    client_id: Optional[str] = None
    task_id: Optional[str] = None
    payload: Any = {}
