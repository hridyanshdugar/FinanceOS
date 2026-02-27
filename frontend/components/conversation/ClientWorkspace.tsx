"use client";

import { useEffect, useState } from "react";
import {
  MessageSquare,
  LayoutDashboard,
  DollarSign,
  FileText,
  Mail,
  TrendingUp,
  Shield,
  ChevronRight,
  User,
  Briefcase,
  MapPin,
  RotateCcw,
  Brain,
  Plus,
  X,
} from "lucide-react";
import { useAppStore } from "@/lib/store";
import { api } from "@/lib/api";
import { ConversationThread } from "./ConversationThread";
import { InputBar, ACTION_SUGGESTIONS, useSendMessage } from "./InputBar";
import type { ClientDetail, ConversationMessage, RagEntry } from "@/lib/types";

export function ClientWorkspace() {
  const {
    selectedClientId,
    clientDetail,
    setClientDetail,
    setConversation,
    activePanel,
    setActivePanel,
    alerts,
  } = useAppStore();

  useEffect(() => {
    if (!selectedClientId) return;
    api.getClient(selectedClientId).then((data) => {
      const detail = data as unknown as ClientDetail;
      setClientDetail(detail);
      const existingMessages: ConversationMessage[] = detail.chat_history
        .filter((ch) => ch.role !== "client")
        .map((ch) => ({
          id: ch.id,
          role: ch.role === "advisor" ? "advisor" : "shadow",
          content: ch.content,
          timestamp: ch.created_at,
        }));
      setConversation(existingMessages);
    });
  }, [selectedClientId, setClientDetail, setConversation]);

  if (!clientDetail) {
    return (
      <div className="flex-1 overflow-y-auto">
        <div className="p-6 max-w-6xl mx-auto space-y-6">
          {/* Header skeleton */}
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="h-12 w-12 rounded-2xl animate-shimmer" />
              <div>
                <div className="h-5 w-40 rounded-lg animate-shimmer" />
                <div className="h-3 w-56 rounded-lg animate-shimmer mt-2" />
              </div>
            </div>
            <div className="h-10 w-32 rounded-xl animate-shimmer" />
          </div>
          {/* Stats skeleton */}
          <div className="grid grid-cols-4 gap-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-20 rounded-2xl animate-shimmer" />
            ))}
          </div>
          {/* Content skeleton */}
          <div className="grid grid-cols-3 gap-4">
            <div className="col-span-2 space-y-4">
              <div className="h-48 rounded-2xl animate-shimmer" />
              <div className="h-32 rounded-2xl animate-shimmer" />
            </div>
            <div className="space-y-4">
              <div className="h-36 rounded-2xl animate-shimmer" />
              <div className="h-28 rounded-2xl animate-shimmer" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  const { client } = clientDetail;
  const clientAlerts = alerts.filter(
    (a) => a.client_id === selectedClientId && a.status === "pending"
  );
  const clientNotes = clientDetail.chat_history.filter((m) => m.role === "client");
  const totalPortfolio = clientDetail.total_portfolio;

  const latestRequest = clientNotes.length > 0 ? clientNotes[clientNotes.length - 1] : null;

  if (activePanel === "chat") {
    return (
      <div className="flex-1 flex flex-col h-full">
        {/* Chat header with back button */}
        <div className="border-b border-border bg-card px-6 py-3 flex items-center gap-3">
          <button
            onClick={() => setActivePanel("overview")}
            className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <ChevronRight className="h-4 w-4 rotate-180" />
            Back
          </button>
          <div className="h-4 w-px bg-border" />
          <MessageSquare className="h-4 w-4 text-primary" />
          <span className="text-sm font-medium text-foreground">
            Shadow Agent — {client.name}
          </span>
          <button
            onClick={() => setConversation([])}
            className="ml-auto flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            Clear
          </button>
        </div>
        {latestRequest && (
          <div className="border-b border-amber-100 bg-amber-50/60 px-6 py-3">
            <div className="max-w-3xl mx-auto flex items-start gap-3">
              <Mail className="h-4 w-4 text-amber-600 mt-0.5 shrink-0" />
              <div>
                <p className="text-[11px] font-semibold text-amber-700 uppercase tracking-wider mb-0.5">
                  Client Request
                </p>
                <p className="text-sm text-foreground leading-relaxed">
                  {latestRequest.content}
                </p>
              </div>
            </div>
          </div>
        )}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-3xl mx-auto w-full px-6 py-6">
            <ConversationThread />
          </div>
        </div>
        <ChatSuggestions clientName={client.name} />
        <InputBar />
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="p-6 max-w-6xl mx-auto space-y-6 animate-fade-in-up">
        {/* Client Header */}
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3">
              <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-amber-100 to-amber-50 flex items-center justify-center text-amber-700 font-semibold text-lg">
                {client.name.split(" ").map((n) => n[0]).join("")}
              </div>
              <div>
                <h2 className="text-xl font-semibold text-foreground tracking-tight">
                  {client.name}
                </h2>
                <div className="flex items-center gap-2 mt-0.5 text-sm text-muted-foreground">
                  <MapPin className="h-3 w-3" />
                  <span>{client.province}</span>
                  <span className="text-border">·</span>
                  <Briefcase className="h-3 w-3" />
                  <span>{client.employer || "Self-employed"}</span>
                  <span className="text-border">·</span>
                  <span className="capitalize">{client.risk_profile}</span>
                </div>
              </div>
            </div>
          </div>
          <button
            onClick={() => setActivePanel("chat")}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-foreground text-white text-sm font-medium
                     hover:bg-foreground/90 transition-colors shadow-sm"
          >
            <MessageSquare className="h-4 w-4" />
            Ask Shadow
          </button>
        </div>

        {/* Quick Stats Row */}
        <div className="grid grid-cols-4 gap-3">
          <div className="bg-card border border-border rounded-2xl p-4">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <DollarSign className="h-3.5 w-3.5" />
              <span className="text-xs font-medium uppercase tracking-wider">Portfolio</span>
            </div>
            <p className="text-xl font-semibold text-foreground">
              ${totalPortfolio.toLocaleString("en-CA")}
            </p>
          </div>
          <div className="bg-card border border-border rounded-2xl p-4">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <TrendingUp className="h-3.5 w-3.5" />
              <span className="text-xs font-medium uppercase tracking-wider">Income</span>
            </div>
            <p className="text-xl font-semibold text-foreground">
              ${client.employment_income.toLocaleString("en-CA")}
            </p>
          </div>
          <div className="bg-card border border-border rounded-2xl p-4">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <User className="h-3.5 w-3.5" />
              <span className="text-xs font-medium uppercase tracking-wider">Dependents</span>
            </div>
            <p className="text-xl font-semibold text-foreground">
              {client.dependents}
            </p>
          </div>
          <div className="bg-card border border-border rounded-2xl p-4">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <Shield className="h-3.5 w-3.5" />
              <span className="text-xs font-medium uppercase tracking-wider">Risk</span>
            </div>
            <p className="text-xl font-semibold text-foreground capitalize">
              {client.risk_profile}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          {/* Left column: Accounts + Goals */}
          <div className="col-span-2 space-y-4">
            {/* Accounts */}
            <div className="bg-card border border-border rounded-2xl p-5">
              <div className="flex items-center gap-2 mb-4">
                <LayoutDashboard className="h-4 w-4 text-primary" />
                <h3 className="text-sm font-semibold text-foreground">Accounts</h3>
              </div>
              <div className="space-y-2">
                {clientDetail.accounts.map((acct) => (
                  <div
                    key={acct.id}
                    className="flex items-center justify-between py-2.5 px-3 rounded-xl hover:bg-accent/50 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="h-8 w-8 rounded-lg bg-accent flex items-center justify-center">
                        <span className="text-xs font-semibold text-foreground">
                          {acct.type.slice(0, 3).toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-foreground">{acct.type}</p>
                        <p className="text-xs text-muted-foreground">{acct.label}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-foreground">
                        ${acct.balance.toLocaleString("en-CA")}
                      </p>
                      {acct.contribution_room > 0 && (
                        <p className="text-xs text-primary">
                          ${acct.contribution_room.toLocaleString("en-CA")} room
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Knowledge Base (RAG) */}
            <RagPanel clientId={selectedClientId!} entries={clientDetail.rag_entries ?? []} onUpdate={setClientDetail} clientDetail={clientDetail} />

            {/* Documents */}
            {clientDetail.documents.length > 0 && (
              <div className="bg-card border border-border rounded-2xl p-5">
                <div className="flex items-center gap-2 mb-4">
                  <FileText className="h-4 w-4 text-primary" />
                  <h3 className="text-sm font-semibold text-foreground">Documents</h3>
                </div>
                <div className="space-y-2">
                  {clientDetail.documents.map((doc) => (
                    <div key={doc.id} className="flex items-center gap-3 py-2 px-3 rounded-xl hover:bg-accent/50 transition-colors">
                      <div className="h-8 w-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
                        <FileText className="h-3.5 w-3.5" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-foreground">{doc.type}</p>
                        <p className="text-xs text-muted-foreground truncate">{doc.content_text.slice(0, 80)}...</p>
                      </div>
                      <span className="text-xs text-muted-foreground shrink-0">{doc.tax_year}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right column: Client Notes + Alerts + Quick Actions */}
          <div className="space-y-4">
            {/* Client Requests */}
            {clientNotes.length > 0 && (
              <div className="bg-card border border-border rounded-2xl p-5">
                <div className="flex items-center gap-2 mb-4">
                  <Mail className="h-4 w-4 text-primary" />
                  <h3 className="text-sm font-semibold text-foreground">Client Requests</h3>
                </div>
                <div className="space-y-3">
                  {clientNotes.map((note) => (
                    <div key={note.id} className="p-3 rounded-xl bg-amber-50/50 border border-amber-100">
                      <p className="text-sm text-foreground leading-relaxed">{note.content}</p>
                      <p className="text-[10px] text-muted-foreground mt-2">
                        {new Date(note.created_at).toLocaleDateString("en-CA", {
                          month: "short",
                          day: "numeric",
                        })}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Alerts for this client */}
            {clientAlerts.length > 0 && (
              <div className="bg-card border border-border rounded-2xl p-5">
                <div className="flex items-center gap-2 mb-4">
                  <Shield className="h-4 w-4 text-amber-600" />
                  <h3 className="text-sm font-semibold text-foreground">Action Items</h3>
                  <span className="ml-auto text-[10px] px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 font-medium">
                    {clientAlerts.length}
                  </span>
                </div>
                <div className="space-y-2">
                  {clientAlerts.map((alert) => (
                    <div key={alert.id} className="p-3 rounded-xl bg-accent/50 border border-border">
                      <p className="text-xs font-medium text-foreground">{alert.title}</p>
                      <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                        {alert.description}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Ask Shadow CTA */}
            <button
              onClick={() => setActivePanel("chat")}
              className="w-full p-4 rounded-2xl bg-gradient-to-br from-foreground to-foreground/90 text-white text-left hover:from-foreground/95 hover:to-foreground/85 transition-all group"
            >
              <div className="flex items-center gap-2 mb-1">
                <MessageSquare className="h-4 w-4" />
                <span className="text-sm font-semibold">Ask Shadow</span>
              </div>
              <p className="text-xs text-white/60">
                Run analysis, check compliance, or draft a message
              </p>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}


function ChatSuggestions({ clientName }: { clientName: string }) {
  const { selectedClientId, isThinking } = useAppStore();
  const sendMessage = useSendMessage();

  if (!selectedClientId || isThinking) return null;

  const handleClick = (suggestion: string) => {
    sendMessage(`${suggestion} for ${clientName}`);
  };

  return (
    <div className="px-6 py-2 bg-card">
      <div className="max-w-3xl mx-auto flex gap-2 overflow-x-auto no-scrollbar">
        {ACTION_SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => handleClick(s)}
            className="px-3 py-1.5 text-xs rounded-lg border border-border bg-background
                     text-muted-foreground hover:text-foreground hover:border-primary/30
                     hover:bg-accent/50 transition-all duration-150 whitespace-nowrap shrink-0"
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}


function RagPanel({
  clientId,
  entries,
  onUpdate,
  clientDetail,
}: {
  clientId: string;
  entries: RagEntry[];
  onUpdate: (detail: ClientDetail | null) => void;
  clientDetail: ClientDetail;
}) {
  const [newEntry, setNewEntry] = useState("");
  const [isAdding, setIsAdding] = useState(false);

  const handleAdd = async () => {
    const content = newEntry.trim();
    if (!content) return;
    try {
      const created = (await api.addClientRag(clientId, content)) as unknown as RagEntry;
      onUpdate({
        ...clientDetail,
        rag_entries: [...entries, created],
      });
      setNewEntry("");
      setIsAdding(false);
    } catch {
      /* ignore */
    }
  };

  const handleDelete = async (entryId: string) => {
    try {
      await api.deleteClientRag(clientId, entryId);
      onUpdate({
        ...clientDetail,
        rag_entries: entries.filter((e) => e.id !== entryId),
      });
    } catch {
      /* ignore */
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleAdd();
    }
    if (e.key === "Escape") {
      setIsAdding(false);
      setNewEntry("");
    }
  };

  return (
    <div className="bg-card border border-border rounded-2xl p-5">
      <div className="flex items-center gap-2 mb-4">
        <Brain className="h-4 w-4 text-primary" />
        <h3 className="text-sm font-semibold text-foreground">Knowledge Base</h3>
        <span className="ml-auto text-[10px] px-2 py-0.5 rounded-full bg-accent text-muted-foreground font-medium">
          {entries.length} {entries.length === 1 ? "entry" : "entries"}
        </span>
      </div>
      <div className="space-y-1.5">
        {entries.map((entry) => (
          <div
            key={entry.id}
            className="group flex items-start gap-2 py-1.5 px-3 rounded-xl hover:bg-accent/50 transition-colors"
          >
            <div className="h-1.5 w-1.5 rounded-full bg-primary mt-2 shrink-0" />
            <p className="text-sm text-foreground flex-1 leading-relaxed">{entry.content}</p>
            <button
              onClick={() => handleDelete(entry.id)}
              className="opacity-0 group-hover:opacity-100 shrink-0 p-0.5 rounded hover:bg-destructive/10 text-muted-foreground hover:text-destructive transition-all"
            >
              <X className="h-3 w-3" />
            </button>
          </div>
        ))}
      </div>
      {isAdding ? (
        <div className="mt-3 flex items-center gap-2">
          <input
            autoFocus
            value={newEntry}
            onChange={(e) => setNewEntry(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Add context about this client..."
            className="flex-1 text-sm bg-background border border-border rounded-lg px-3 py-2
                     placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
          />
          <button
            onClick={handleAdd}
            disabled={!newEntry.trim()}
            className="px-3 py-2 text-xs font-medium rounded-lg bg-primary text-primary-foreground
                     hover:bg-primary/90 transition-colors disabled:opacity-30"
          >
            Add
          </button>
          <button
            onClick={() => { setIsAdding(false); setNewEntry(""); }}
            className="px-2 py-2 text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            Cancel
          </button>
        </div>
      ) : (
        <button
          onClick={() => setIsAdding(true)}
          className="mt-3 flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
        >
          <Plus className="h-3 w-3" />
          Add entry
        </button>
      )}
    </div>
  );
}
