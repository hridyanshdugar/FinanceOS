from __future__ import annotations
from pydantic import BaseModel
from typing import Optional, List


class Client(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    province: str
    sin_last4: Optional[str] = None
    date_of_birth: str
    risk_profile: str
    goals: List[str] = []
    marital_status: Optional[str] = None
    dependents: int = 0
    employment_income: float = 0
    employer: Optional[str] = None
    onboarded_at: str = ""
    advisor_notes: str = ""


class Account(BaseModel):
    id: str
    client_id: str
    type: str
    label: str = ""
    balance: float = 0
    contribution_room: float = 0
    last_updated: str = ""


class Document(BaseModel):
    id: str
    client_id: str
    type: str
    content_text: str = ""
    tax_year: Optional[int] = None
    file_path: str = ""
    uploaded_at: str = ""


class ChatMessage(BaseModel):
    id: str
    client_id: str
    role: str
    content: str
    created_at: str = ""


class SendMessageRequest(BaseModel):
    content: str
    client_id: str


class ClientDetail(BaseModel):
    client: Client
    accounts: List[Account] = []
    documents: List[Document] = []
    chat_history: List[ChatMessage] = []
    total_portfolio: float = 0
