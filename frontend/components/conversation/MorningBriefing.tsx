"use client";

import {
  Bell,
  ArrowRight,
  DollarSign,
  TrendingUp,
  GraduationCap,
  Users,
  AlertTriangle,
  CheckCircle2,
  Clock,
} from "lucide-react";
import { useAppStore } from "@/lib/store";

const ALERT_ICONS: Record<string, React.ReactNode> = {
  idle_cash: <DollarSign className="h-4 w-4" />,
  portfolio_drift: <TrendingUp className="h-4 w-4" />,
  cesg_optimization: <GraduationCap className="h-4 w-4" />,
};

function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

export function MorningBriefing() {
  const { alerts, clients, setSelectedClientId } = useAppStore();
  const pendingAlerts = alerts.filter((a) => a.status === "pending");
  const isLoading = clients.length === 0;

  const totalClients = clients.length;
  const totalPortfolio = clients.reduce(
    (sum, c) => sum + (c.total_portfolio ?? 0),
    0
  );
  const totalAlerts = pendingAlerts.length;

  if (isLoading) {
    return (
      <div className="flex-1 overflow-y-auto">
        <div className="p-6 max-w-6xl mx-auto space-y-6">
          <div>
            <div className="h-7 w-56 rounded-lg animate-shimmer" />
            <div className="h-4 w-72 rounded-lg animate-shimmer mt-3" />
          </div>
          <div className="grid grid-cols-4 gap-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-20 rounded-2xl animate-shimmer" />
            ))}
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div className="col-span-2 h-48 rounded-2xl animate-shimmer" />
            <div className="h-48 rounded-2xl animate-shimmer" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="p-6 max-w-6xl mx-auto space-y-6 animate-fade-in-up">
        {/* Header */}
        <div>
          <h2 className="text-2xl font-semibold text-foreground tracking-tight">
            {getGreeting()}, Alex.
          </h2>
          <p className="text-muted-foreground mt-1 text-[15px]">
            Here&apos;s your workspace overview.
          </p>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-4 gap-3">
          <div className="bg-card border border-border rounded-2xl p-4">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <Users className="h-3.5 w-3.5" />
              <span className="text-xs font-medium uppercase tracking-wider">Clients</span>
            </div>
            <p className="text-2xl font-semibold text-foreground">{totalClients}</p>
          </div>
          <div className="bg-card border border-border rounded-2xl p-4">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <DollarSign className="h-3.5 w-3.5" />
              <span className="text-xs font-medium uppercase tracking-wider">AUM</span>
            </div>
            <p className="text-2xl font-semibold text-foreground">
              ${(totalPortfolio / 1_000_000).toFixed(1)}M
            </p>
          </div>
          <div className="bg-card border border-border rounded-2xl p-4">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <AlertTriangle className="h-3.5 w-3.5" />
              <span className="text-xs font-medium uppercase tracking-wider">Action Items</span>
            </div>
            <p className="text-2xl font-semibold text-foreground">{totalAlerts}</p>
          </div>
          <div className="bg-card border border-border rounded-2xl p-4">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <CheckCircle2 className="h-3.5 w-3.5" />
              <span className="text-xs font-medium uppercase tracking-wider">Status</span>
            </div>
            <p className="text-lg font-semibold text-green-600">All systems go</p>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          {/* Action Items */}
          <div className="col-span-2">
            {pendingAlerts.length > 0 && (
              <div className="bg-card border border-border rounded-2xl p-5">
                <div className="flex items-center gap-2 mb-4">
                  <Bell className="h-4 w-4 text-amber-600" />
                  <h3 className="text-sm font-semibold text-foreground">Action Items</h3>
                  <span className="ml-auto text-[10px] px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 font-medium">
                    {pendingAlerts.length} pending
                  </span>
                </div>
                <div className="space-y-2">
                  {pendingAlerts.map((alert) => (
                    <button
                      key={alert.id}
                      onClick={() => {
                        const client = clients.find((c) => c.id === alert.client_id);
                        if (client) setSelectedClientId(client.id);
                      }}
                      className="w-full text-left group"
                    >
                      <div className="flex items-start gap-3 p-3 rounded-xl hover:bg-accent/50 transition-colors">
                        <div className="h-8 w-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center shrink-0 mt-0.5">
                          {ALERT_ICONS[alert.alert_type] || <Bell className="h-3.5 w-3.5" />}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <p className="text-sm font-medium text-foreground">{alert.title}</p>
                            <span className="text-[10px] text-muted-foreground bg-accent px-2 py-0.5 rounded-full">
                              {alert.client_name}
                            </span>
                          </div>
                          <p className="text-xs text-muted-foreground mt-0.5 line-clamp-1">
                            {alert.description}
                          </p>
                        </div>
                        <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors shrink-0 mt-1" />
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {pendingAlerts.length === 0 && (
              <div className="bg-card border border-border rounded-2xl p-8 text-center">
                <CheckCircle2 className="h-8 w-8 text-green-500 mx-auto mb-3" />
                <p className="text-sm font-medium text-foreground">You&apos;re all caught up</p>
                <p className="text-xs text-muted-foreground mt-1">No pending action items. Your clients are in great shape.</p>
              </div>
            )}
          </div>

          {/* Client List */}
          <div className="bg-card border border-border rounded-2xl p-5">
            <div className="flex items-center gap-2 mb-4">
              <Users className="h-4 w-4 text-primary" />
              <h3 className="text-sm font-semibold text-foreground">Clients</h3>
            </div>
            <div className="space-y-1">
              {clients.map((client) => (
                <button
                  key={client.id}
                  onClick={() => setSelectedClientId(client.id)}
                  className="w-full text-left flex items-center gap-3 p-2.5 rounded-xl hover:bg-accent/50 transition-colors group"
                >
                  <div className="h-8 w-8 rounded-lg bg-accent flex items-center justify-center text-xs font-semibold text-foreground">
                    {client.name.split(" ").map((n) => n[0]).join("")}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground">{client.name}</p>
                    <p className="text-[11px] text-muted-foreground">
                      {client.province} · ${(client.total_portfolio ?? 0).toLocaleString("en-CA")}
                    </p>
                  </div>
                  {(client.pending_alerts ?? 0) > 0 && (
                    <div className="h-2 w-2 rounded-full bg-amber-500 shrink-0" />
                  )}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
