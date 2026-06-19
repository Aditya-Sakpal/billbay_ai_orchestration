"use client";

import {
  FileBarChart2,
  PanelLeftClose,
  PanelLeftOpen,
} from "lucide-react";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { PROMPT_CATEGORIES } from "@/data/prompt-categories";
import {
  REPORT_CATALOG,
  REPORT_GROUPS,
} from "@/data/report-catalog";
import { useChat } from "@/providers/chat-provider";
import { cn } from "@/lib/utils";

interface ChatSidebarProps {
  className?: string;
  mobile?: boolean;
  showPrompts?: boolean;
}

export function ChatSidebar({
  className,
  mobile = false,
  showPrompts = true,
}: ChatSidebarProps) {
  const { sendMessage, isLoading, connectionStatus } = useChat();
  const [collapsed, setCollapsed] = useState(false);

  const disabled = isLoading || connectionStatus !== "connected";

  const handleReportClick = (name: string) => {
    sendMessage(`Show me the ${name} report`);
  };

  if (!mobile && collapsed) {
    return (
      <div
        className={cn(
          "flex w-12 flex-col border-r border-slate-800 bg-slate-900",
          className,
        )}
      >
        <Button
          variant="ghost"
          size="icon-sm"
          className="m-2 text-slate-300 hover:bg-slate-800 hover:text-white"
          onClick={() => setCollapsed(false)}
        >
          <PanelLeftOpen className="h-4 w-4" />
        </Button>
      </div>
    );
  }

  return (
    <aside
      className={cn(
        "flex w-72 shrink-0 flex-col border-r border-slate-800 bg-slate-900 text-slate-200",
        mobile && "w-full border-r-0",
        className,
      )}
    >
      {!mobile ? (
        <div className="flex items-center justify-between border-b border-slate-800 px-4 py-3.5">
          <p className="text-[11px] font-semibold uppercase tracking-widest text-slate-400">
            Explore
          </p>
          <Button
            variant="ghost"
            size="icon-sm"
            className="text-slate-400 hover:bg-slate-800 hover:text-white"
            onClick={() => setCollapsed(true)}
          >
            <PanelLeftClose className="h-4 w-4" />
          </Button>
        </div>
      ) : null}

      <ScrollArea className="flex-1">
        <div className="space-y-6 p-4">
          {showPrompts ? (
            <>
              <section>
                <h3 className="mb-3 text-[11px] font-semibold uppercase tracking-widest text-slate-400">
                  Suggested prompts
                </h3>
                <div className="space-y-2">
                  {PROMPT_CATEGORIES.flatMap((category) =>
                    category.prompts.slice(0, 1).map((prompt) => (
                      <button
                        key={prompt}
                        type="button"
                        disabled={disabled}
                        onClick={() => sendMessage(prompt)}
                        className="w-full rounded-xl border border-slate-700/60 bg-slate-800/50 px-3 py-2.5 text-left text-sm leading-snug text-slate-200 transition hover:border-teal-500/40 hover:bg-slate-800 disabled:opacity-50"
                      >
                        {prompt}
                      </button>
                    )),
                  )}
                </div>
              </section>
              <Separator className="bg-slate-800" />
            </>
          ) : null}

          <section>
            <h3 className="mb-3 text-[11px] font-semibold uppercase tracking-widest text-slate-400">
              Report catalog
            </h3>
            <div className="space-y-5">
              {REPORT_GROUPS.map((group) => (
                <div key={group}>
                  <p className="mb-2 text-[10px] font-medium uppercase tracking-widest text-slate-500">
                    {group}
                  </p>
                  <ul className="space-y-1">
                    {REPORT_CATALOG.filter((r) => r.group === group).map(
                      (report) => (
                        <li key={report.id}>
                          <button
                            type="button"
                            disabled={disabled}
                            onClick={() => handleReportClick(report.name)}
                            className="group flex w-full items-start gap-2 rounded-lg border-l-2 border-transparent px-2 py-2 text-left text-sm text-slate-300 transition hover:border-teal-400 hover:bg-slate-800 disabled:opacity-50"
                          >
                            <FileBarChart2 className="mt-0.5 h-4 w-4 shrink-0 text-teal-400" />
                            <span className="leading-snug">{report.name}</span>
                          </button>
                        </li>
                      ),
                    )}
                  </ul>
                </div>
              ))}
            </div>
          </section>

          <div className="rounded-xl border border-slate-700/60 bg-slate-800/40 p-3 text-xs text-slate-400">
            <p className="font-medium text-slate-300">Access levels</p>
            <div className="mt-2 flex flex-wrap gap-1">
              <Badge
                variant="outline"
                className="border-slate-600 bg-slate-800 text-slate-300"
              >
                30 Finance
              </Badge>
              <Badge
                variant="outline"
                className="border-slate-600 bg-slate-800 text-slate-300"
              >
                50 Operations
              </Badge>
            </div>
          </div>
        </div>
      </ScrollArea>
    </aside>
  );
}
