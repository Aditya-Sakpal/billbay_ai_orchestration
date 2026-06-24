"use client";

import { BarChart3 } from "lucide-react";
import { useEffect, useState } from "react";

import { cn } from "@/lib/utils";

const LOADING_STEPS = [
  "Understanding your question…",
  "Matching report from catalog…",
  "Extracting filters…",
  "Querying business data…",
];

interface LoadingIndicatorProps {
  className?: string;
}

export function AssistantAvatar({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-teal-500 to-teal-700 text-white shadow-md shadow-teal-600/20",
        className,
      )}
    >
      <BarChart3 className="h-4 w-4" />
    </div>
  );
}

export function LoadingIndicator({ className }: LoadingIndicatorProps) {
  const [stepIndex, setStepIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setStepIndex((current) => (current + 1) % LOADING_STEPS.length);
    }, 1200);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className={cn("flex justify-start message-enter", className)}>
      <div className="flex max-w-full gap-3 sm:max-w-[92%]">
        <AssistantAvatar />
        <div className="flex-1 rounded-2xl border border-slate-200/80 bg-white px-4 py-4 shadow-md ring-1 ring-slate-200/60">
          <div className="mb-3 flex items-center gap-2">
            <div className="flex gap-1">
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-teal-500 [animation-delay:-0.3s]" />
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-teal-500 [animation-delay:-0.15s]" />
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-teal-500" />
            </div>
            <p className="text-sm font-medium text-slate-800">Analyzing…</p>
          </div>
          <p className="text-xs text-muted-foreground">
            {LOADING_STEPS[stepIndex]}
          </p>
          <div className="mt-3 space-y-2">
            <div className="h-2 w-full animate-pulse rounded-full bg-slate-100" />
            <div className="h-2 w-4/5 animate-pulse rounded-full bg-slate-100" />
            <div className="h-2 w-3/5 animate-pulse rounded-full bg-slate-100" />
          </div>
        </div>
      </div>
    </div>
  );
}
