"use client";

import { useState, useEffect } from "react";
import { X, Bell } from "lucide-react";
import { useAppStore } from "@/lib/store";

export function ProactiveToast() {
  const { alerts, setSelectedClientId, removeAlert } = useAppStore();
  const [visible, setVisible] = useState<string[]>([]);
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());

  useEffect(() => {
    const pending = alerts
      .filter((a) => a.status === "pending" && !dismissed.has(a.id))
      .map((a) => a.id);
    setVisible(pending.slice(0, 2));
  }, [alerts, dismissed]);

  const handleDismiss = (alertId: string) => {
    setDismissed((prev) => new Set(prev).add(alertId));
    setVisible((prev) => prev.filter((id) => id !== alertId));
  };

  const handleAccept = (alertId: string) => {
    const alert = alerts.find((a) => a.id === alertId);
    if (alert) {
      setSelectedClientId(alert.client_id);
    }
    handleDismiss(alertId);
  };

  const visibleAlerts = alerts.filter((a) => visible.includes(a.id));

  if (visibleAlerts.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 space-y-3 w-[380px]">
      {visibleAlerts.map((alert) => (
        <div
          key={alert.id}
          className="bg-card border border-border rounded-2xl shadow-lg p-4 animate-slide-in"
        >
          <div className="flex items-start gap-3">
            <div className="h-8 w-8 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center shrink-0">
              <Bell className="h-4 w-4" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-2">
                <p className="text-sm font-medium text-foreground">{alert.title}</p>
                <button
                  onClick={() => handleDismiss(alert.id)}
                  className="shrink-0 h-5 w-5 rounded flex items-center justify-center hover:bg-accent transition-colors"
                >
                  <X className="h-3.5 w-3.5 text-muted-foreground" />
                </button>
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {alert.client_name}
              </p>
              <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                {alert.description}
              </p>
              <div className="flex items-center gap-2 mt-3">
                <button
                  onClick={() => handleAccept(alert.id)}
                  className="text-xs font-medium px-3 py-1.5 rounded-lg bg-primary text-primary-foreground
                           hover:bg-primary/90 transition-colors"
                >
                  Look into this
                </button>
                <button
                  onClick={() => handleDismiss(alert.id)}
                  className="text-xs font-medium px-3 py-1.5 rounded-lg text-muted-foreground
                           hover:text-foreground hover:bg-accent transition-colors"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
