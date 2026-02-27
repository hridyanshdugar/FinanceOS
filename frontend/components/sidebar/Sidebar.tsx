"use client";

import { useState } from "react";
import { Search } from "lucide-react";
import { useAppStore } from "@/lib/store";
import { ClientRow } from "./ClientRow";
import { WorkingOn } from "./WorkingOn";
import { ConnectionStatus } from "@/components/shared/ConnectionStatus";

export function Sidebar() {
  const { clients, selectedClientId, setSelectedClientId } = useAppStore();
  const [search, setSearch] = useState("");

  const filtered = clients.filter((c) =>
    c.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <aside className="w-[260px] h-full flex flex-col border-r border-border bg-card shrink-0">
      {/* Logo */}
      <div className="px-5 py-4 border-b border-border">
        <button
          onClick={() => setSelectedClientId(null)}
          className="text-left"
        >
          <h1 className="text-lg font-semibold tracking-tight text-foreground">
            FinanceOS
          </h1>
          <p className="text-xs text-muted-foreground mt-0.5">Alex&apos;s workspace</p>
        </button>
      </div>

      {/* Search */}
      <div className="px-3 py-3">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search clients..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-2 text-sm rounded-xl bg-background border border-border
                       placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20
                       focus:border-primary transition-all"
          />
        </div>
      </div>

      {/* Client List */}
      <div className="flex-1 overflow-y-auto px-2">
        <p className="px-3 py-2 text-[11px] font-medium text-muted-foreground uppercase tracking-wider">
          Clients
        </p>
        {clients.length === 0 ? (
          <div className="space-y-2 px-2">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="flex items-center gap-3 p-2">
                <div className="h-8 w-8 rounded-xl animate-shimmer shrink-0" />
                <div className="flex-1 space-y-1.5">
                  <div className="h-3.5 w-24 rounded animate-shimmer" />
                  <div className="h-2.5 w-16 rounded animate-shimmer" />
                </div>
              </div>
            ))}
          </div>
        ) : (
          filtered.map((client) => (
            <ClientRow
              key={client.id}
              client={client}
              isActive={client.id === selectedClientId}
              onClick={() => setSelectedClientId(client.id)}
            />
          ))
        )}
      </div>

      {/* Working On */}
      <WorkingOn />

      {/* Connection Status */}
      <div className="border-t border-border px-3 py-2">
        <ConnectionStatus />
      </div>
    </aside>
  );
}
