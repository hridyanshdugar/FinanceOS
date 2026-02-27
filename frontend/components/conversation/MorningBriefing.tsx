"use client";

import { Bell, ArrowRight, DollarSign, TrendingUp, GraduationCap } from "lucide-react";
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

  return (
    <div className="animate-fade-in-up">
      <h2 className="text-2xl font-semibold text-foreground tracking-tight">
        {getGreeting()}, Alex.
      </h2>
      {pendingAlerts.length > 0 ? (
        <p className="text-muted-foreground mt-2 text-[15px]">
          {pendingAlerts.length} thing{pendingAlerts.length !== 1 ? "s" : ""} need
          your attention today.
        </p>
      ) : (
        <p className="text-muted-foreground mt-2 text-[15px]">
          Everything looks good today. Your clients are in great shape.
        </p>
      )}

      {pendingAlerts.length > 0 && (
        <div className="mt-8 space-y-3">
          {pendingAlerts.map((alert) => (
            <button
              key={alert.id}
              onClick={() => {
                const client = clients.find((c) => c.id === alert.client_id);
                if (client) setSelectedClientId(client.id);
              }}
              className="w-full text-left group"
            >
              <div className="flex items-start gap-4 p-4 rounded-2xl bg-card border border-border
                            hover:shadow-sm hover:border-primary/20 transition-all duration-200">
                <div className="h-9 w-9 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center shrink-0 mt-0.5">
                  {ALERT_ICONS[alert.alert_type] || <Bell className="h-4 w-4" />}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium text-foreground">{alert.title}</p>
                    <span className="text-[11px] text-muted-foreground bg-accent px-2 py-0.5 rounded-full">
                      {alert.client_name}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                    {alert.description}
                  </p>
                </div>
                <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors shrink-0 mt-1" />
              </div>
            </button>
          ))}
        </div>
      )}

      {/* Client overview */}
      <div className="mt-10">
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-4">
          Your clients
        </p>
        <div className="grid grid-cols-2 gap-3">
          {clients.slice(0, 4).map((client) => (
            <button
              key={client.id}
              onClick={() => setSelectedClientId(client.id)}
              className="text-left p-4 rounded-2xl bg-card border border-border
                       hover:shadow-sm hover:border-primary/20 transition-all duration-200"
            >
              <p className="text-sm font-medium text-foreground">{client.name}</p>
              <p className="text-xs text-muted-foreground mt-1">
                {client.province} · ${(client.total_portfolio ?? 0).toLocaleString("en-CA")}
              </p>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
