"use client";

import { useChat } from "@/providers/chat-provider";
import type { ConnectionStatus } from "@/lib/types";
import { cn } from "@/lib/utils";

const STATUS_LABELS: Record<ConnectionStatus, string> = {
  idle: "Idle",
  connecting: "Connecting…",
  connected: "Connected",
  disconnected: "Offline",
  error: "Error",
};

const STATUS_COLORS: Record<ConnectionStatus, string> = {
  idle: "bg-slate-400",
  connecting: "bg-amber-400 animate-pulse",
  connected: "bg-emerald-500",
  disconnected: "bg-slate-400",
  error: "bg-red-500",
};

interface ConnectionStatusBadgeProps {
  className?: string;
}

export function ConnectionStatusBadge({ className }: ConnectionStatusBadgeProps) {
  const { connectionStatus } = useChat();

  return (
    <div
      className={cn(
        "flex items-center gap-1.5 rounded-full border border-slate-200 bg-slate-50 px-2.5 py-1 text-[11px] font-medium text-slate-600",
        className,
      )}
    >
      <span
        className={cn("h-1.5 w-1.5 rounded-full", STATUS_COLORS[connectionStatus])}
      />
      {STATUS_LABELS[connectionStatus]}
    </div>
  );
}
