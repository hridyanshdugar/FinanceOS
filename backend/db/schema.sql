CREATE TABLE IF NOT EXISTS clients (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    province TEXT NOT NULL,
    sin_last4 TEXT,
    date_of_birth TEXT NOT NULL,
    risk_profile TEXT NOT NULL CHECK (risk_profile IN ('conservative', 'balanced', 'growth', 'aggressive')),
    goals TEXT DEFAULT '[]',
    marital_status TEXT,
    dependents INTEGER DEFAULT 0,
    employment_income REAL DEFAULT 0,
    employer TEXT,
    onboarded_at TEXT NOT NULL DEFAULT (datetime('now')),
    advisor_notes TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS accounts (
    id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL REFERENCES clients(id),
    type TEXT NOT NULL CHECK (type IN ('RRSP', 'TFSA', 'FHSA', 'RESP', 'LIRA', 'RRIF', 'LIF', 'non_registered', 'corporate', 'checking', 'savings', 'spousal_rrsp')),
    label TEXT DEFAULT '',
    balance REAL NOT NULL DEFAULT 0,
    contribution_room REAL DEFAULT 0,
    last_updated TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS transactions (
    id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL REFERENCES accounts(id),
    amount REAL NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('contribution', 'withdrawal', 'dividend', 'transfer', 'fee', 'interest')),
    description TEXT DEFAULT '',
    date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL REFERENCES clients(id),
    type TEXT NOT NULL CHECK (type IN ('T4', 'T4A', 'T5', 'T776', 'NOA', 'T1', 'T2', 'T4RIF', 'transcript')),
    content_text TEXT DEFAULT '',
    tax_year INTEGER,
    file_path TEXT DEFAULT '',
    uploaded_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS chat_history (
    id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL REFERENCES clients(id),
    role TEXT NOT NULL CHECK (role IN ('advisor', 'client', 'system')),
    content TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS agent_tasks (
    id TEXT PRIMARY KEY,
    client_id TEXT REFERENCES clients(id),
    agent_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    input_data TEXT DEFAULT '{}',
    output_data TEXT DEFAULT '{}',
    advisor_action TEXT CHECK (advisor_action IN ('approved', 'edited', 'rejected', NULL)),
    advisor_note TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS alerts (
    id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL REFERENCES clients(id),
    alert_type TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    drafted_action TEXT DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'dismissed')),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS client_rag (
    id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL REFERENCES clients(id),
    content TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'advisor',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS embeddings (
    id TEXT PRIMARY KEY,
    source_table TEXT NOT NULL,
    source_id TEXT NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding BLOB,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_accounts_client ON accounts(client_id);
CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_documents_client ON documents(client_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_client ON chat_history(client_id);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_client ON agent_tasks(client_id);
CREATE INDEX IF NOT EXISTS idx_alerts_client ON alerts(client_id);
CREATE INDEX IF NOT EXISTS idx_client_rag_client ON client_rag(client_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_source ON embeddings(source_table, source_id);
