"use client";

import {
  BarChart3,
  Landmark,
  Receipt,
  Sparkles,
} from "lucide-react";

import { PROMPT_CATEGORIES } from "@/data/prompt-categories";
import { useChat } from "@/providers/chat-provider";
import { cn } from "@/lib/utils";

const CATEGORY_ICONS = {
  performance: BarChart3,
  collections: Receipt,
  finance: Landmark,
} as const;

export function SuggestedPrompts() {
  const { sendMessage, isLoading, connectionStatus } = useChat();
  const disabled = isLoading || connectionStatus !== "connected";

  return (
    <div className="mx-auto flex h-full max-w-3xl flex-col justify-center gap-8 px-4 py-10 sm:px-6 sm:py-16">
      <div className="text-center">
        <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-teal-500 to-teal-700 text-white shadow-lg shadow-teal-600/25">
          <Sparkles className="h-8 w-8" />
        </div>
        <h2 className="bg-gradient-to-r from-slate-900 via-slate-800 to-teal-700 bg-clip-text text-2xl font-semibold tracking-tight text-transparent sm:text-3xl">
          Ask anything about your business data
        </h2>
        <p className="mx-auto mt-3 max-w-lg text-sm leading-relaxed text-muted-foreground">
          BillBay Intelligence connects natural language to sales, collections,
          and finance reports — with governed filters and source citations.
        </p>
      </div>

      <div className="space-y-6">
        {PROMPT_CATEGORIES.map((category) => {
          const Icon = CATEGORY_ICONS[category.icon];
          return (
            <section key={category.id}>
              <div className="mb-3 flex items-center gap-2">
                <Icon className="h-4 w-4 text-teal-600" />
                <h3 className="text-xs font-semibold uppercase tracking-widest text-slate-500">
                  {category.label}
                </h3>
              </div>
              <div className="grid gap-2 sm:grid-cols-2">
                {category.prompts.map((prompt) => (
                  <button
                    key={prompt}
                    type="button"
                    disabled={disabled}
                    onClick={() => sendMessage(prompt)}
                    className={cn(
                      "rounded-xl border border-slate-200/80 bg-white px-4 py-3.5 text-left text-sm leading-snug text-slate-700 shadow-sm transition",
                      "hover:-translate-y-0.5 hover:border-teal-200 hover:shadow-md",
                      "disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0",
                    )}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </section>
          );
        })}
      </div>
    </div>
  );
}
