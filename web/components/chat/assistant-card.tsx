"use client";

import { Copy, Check, FileBarChart2 } from "lucide-react";
import { useState } from "react";

import { DataTable, getTableRowCount, tableToPlainText } from "@/components/chat/data-table";
import { AssistantAvatar } from "@/components/chat/loading-indicator";
import { MarkdownContent } from "@/components/chat/markdown-content";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { classifyAnswerTone, parseAssistantAnswer } from "@/lib/parse-answer";
import { parseMarkdownTable } from "@/lib/parse-markdown-table";
import { cn } from "@/lib/utils";
import type { ChatMessage } from "@/lib/types";

interface AssistantCardProps {
  message: ChatMessage;
}

export function AssistantCard({ message }: AssistantCardProps) {
  const [copiedSummary, setCopiedSummary] = useState(false);
  const [copiedTable, setCopiedTable] = useState(false);
  const { summary, tableMarkdown } = parseAssistantAnswer(message.content);
  const tone = classifyAnswerTone(message.content, message.isError);
  const filters = message.filters ?? {};
  const filterEntries = Object.entries(filters);
  const hasParsedTable =
    tableMarkdown !== null && parseMarkdownTable(tableMarkdown) !== null;
  const rowCount = tableMarkdown ? getTableRowCount(tableMarkdown) : null;

  const handleCopySummary = async () => {
    await navigator.clipboard.writeText(summary || message.content);
    setCopiedSummary(true);
    setTimeout(() => setCopiedSummary(false), 2000);
  };

  const handleCopyTable = async () => {
    if (!tableMarkdown) {
      return;
    }
    const text = tableToPlainText(tableMarkdown) ?? tableMarkdown;
    await navigator.clipboard.writeText(text);
    setCopiedTable(true);
    setTimeout(() => setCopiedTable(false), 2000);
  };

  return (
    <div className="flex justify-start message-enter">
      <div className="flex w-full max-w-full gap-3 sm:max-w-[92%]">
        <AssistantAvatar className="hidden sm:flex" />
        <div
          className={cn(
            "min-w-0 flex-1 rounded-2xl border bg-white shadow-md ring-1 ring-slate-200/60",
            tone === "error" && "border-l-4 border-l-red-500 border-red-200/60",
            tone === "warning" &&
              "border-l-4 border-l-amber-500 border-amber-200/60",
            tone === "info" && "border-l-4 border-l-sky-500 border-sky-200/60",
            tone === "success" && "border-slate-200/80",
          )}
        >
          <div className="flex items-center justify-between gap-3 border-b border-slate-100 px-4 py-3">
            <div className="flex items-center gap-2">
              <AssistantAvatar className="sm:hidden" />
              <p className="text-sm font-semibold text-slate-900">
                BillBay Intelligence
              </p>
            </div>
            <span className="text-[11px] text-muted-foreground">
              {message.timestamp.toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </span>
          </div>

          {(message.report || filterEntries.length > 0) && (
            <div className="flex flex-wrap items-center gap-2 border-b border-slate-100 px-4 py-3">
              {message.report ? (
                <Badge className="gap-1 border-teal-200 bg-teal-50 text-teal-800 hover:bg-teal-50">
                  <FileBarChart2 className="h-3 w-3" />
                  {message.report}
                </Badge>
              ) : null}
              {filterEntries.map(([key, value]) => (
                <Badge
                  key={key}
                  variant="outline"
                  className="border-slate-200 bg-slate-50 font-normal text-slate-700"
                >
                  {key}: {String(value)}
                </Badge>
              ))}
            </div>
          )}

          <div className="space-y-4 px-4 py-4">
            {summary ? (
              <MarkdownContent
                content={summary}
                className="text-[15px] leading-7 text-slate-700"
              />
            ) : null}

            {tableMarkdown ? (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <p className="text-xs font-semibold uppercase tracking-widest text-slate-500">
                    Source data
                  </p>
                  {rowCount !== null ? (
                    <Badge
                      variant="outline"
                      className="h-5 px-1.5 text-[10px] font-normal"
                    >
                      {rowCount} {rowCount === 1 ? "row" : "rows"}
                    </Badge>
                  ) : null}
                </div>
                {hasParsedTable ? (
                  <DataTable markdown={tableMarkdown} />
                ) : (
                  <div className="overflow-x-auto rounded-xl border border-slate-200 bg-slate-50/50 p-3">
                    <MarkdownContent content={tableMarkdown} />
                  </div>
                )}
              </div>
            ) : null}
          </div>

          <div className="flex flex-wrap items-center gap-2 border-t border-slate-100 px-4 py-3">
            <Button
              variant="ghost"
              size="sm"
              className="h-7 gap-1 px-2 text-xs text-muted-foreground"
              onClick={handleCopySummary}
            >
              {copiedSummary ? (
                <>
                  <Check className="h-3 w-3" />
                  Copied
                </>
              ) : (
                <>
                  <Copy className="h-3 w-3" />
                  Copy summary
                </>
              )}
            </Button>
            {tableMarkdown ? (
              <Button
                variant="ghost"
                size="sm"
                className="h-7 gap-1 px-2 text-xs text-muted-foreground"
                onClick={handleCopyTable}
              >
                {copiedTable ? (
                  <>
                    <Check className="h-3 w-3" />
                    Copied
                  </>
                ) : (
                  <>
                    <Copy className="h-3 w-3" />
                    Copy table
                  </>
                )}
              </Button>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}
