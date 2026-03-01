export interface Client {
  id: string;
  name: string;
  email: string | null;
  phone: string | null;
  province: string;
  sin_last4: string | null;
  date_of_birth: string;
  risk_profile: "conservative" | "balanced" | "growth" | "aggressive";
  goals: string[];
  marital_status: string | null;
  dependents: number;
  employment_income: number;
  employer: string | null;
  onboarded_at: string;
  advisor_notes: string;
  total_portfolio?: number;
  pending_requests?: number;
}

export interface Account {
  id: string;
  client_id: string;
  type: string;
  label: string;
  balance: number;
  contribution_room: number;
  last_updated: string;
}

export interface Document {
  id: string;
  client_id: string;
  type: string;
  content_text: string;
  tax_year: number | null;
  file_path: string;
  uploaded_at: string;
}

export interface ChatMessage {
  id: string;
  client_id: string;
  role: "advisor" | "client" | "system";
  content: string;
  status: "pending" | "completed";
  created_at: string;
}

export interface RagEntry {
  id: string;
  client_id: string;
  content: string;
  source: string;
  created_at: string;
}

export interface ClientDetail {
  client: Client;
  accounts: Account[];
  documents: Document[];
  chat_history: ChatMessage[];
  rag_entries: RagEntry[];
  total_portfolio: number;
}

export interface Alert {
  id: string;
  client_id: string;
  client_name: string;
  alert_type: string;
  title: string;
  description: string;
  drafted_action: Record<string, unknown>;
  status: string;
  created_at: string;
}

export interface AgentTask {
  id: string;
  client_id: string | null;
  agent_type: string;
  status: "pending" | "running" | "completed" | "failed";
  input_data: Record<string, unknown>;
  output_data: Record<string, unknown>;
  advisor_action: string | null;
  advisor_note: string;
  created_at: string;
  completed_at: string | null;
}

export interface ResearchSuggestion {
  ticker: string;
  name: string;
  allocation_pct: number;
  rationale: string;
}

export interface ResearchOutput {
  summary: string;
  suggestions: ResearchSuggestion[];
  asset_mix: {
    equity_pct: number;
    fixed_income_pct: number;
    alternatives_pct: number;
  };
  account_strategy?: string;
}

export interface TriTieredOutput {
  numbers: {
    summary: string;
    details: string;
    python_code?: string;
  };
  compliance: {
    status: "clear" | "warning" | "error";
    items: Array<{
      severity: "info" | "warning" | "error";
      message: string;
      rule_citation?: string;
    }>;
  };
  draft_message: {
    to: string;
    subject: string;
    body: string;
    tone: string;
    rag_highlights: string[];
  };
  research?: ResearchOutput | null;
}

export interface ConversationMessage {
  id: string;
  role: "advisor" | "shadow";
  content: string;
  timestamp: string;
  analysis?: TriTieredOutput;
  task_id?: string;
}
