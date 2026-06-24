"use client";

import { SendHorizontal } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { useChat } from "@/providers/chat-provider";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  className?: string;
  onSend?: () => void;
}

const MAX_ROWS = 4;
const LINE_HEIGHT = 24;

export function ChatInput({ className, onSend }: ChatInputProps) {
  const { sendMessage, isLoading, connectionStatus, backendHealthy } =
    useChat();
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (
        event.key === "/" &&
        document.activeElement?.tagName !== "INPUT" &&
        document.activeElement?.tagName !== "TEXTAREA"
      ) {
        event.preventDefault();
        textareaRef.current?.focus();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) {
      return;
    }
    textarea.style.height = "auto";
    const maxHeight = LINE_HEIGHT * MAX_ROWS + 24;
    textarea.style.height = `${Math.min(textarea.scrollHeight, maxHeight)}px`;
  }, [value]);

  const canSend =
    value.trim().length > 0 &&
    !isLoading &&
    connectionStatus === "connected" &&
    backendHealthy !== false;

  const handleSubmit = () => {
    if (!canSend) {
      return;
    }
    sendMessage(value);
    setValue("");
    onSend?.();
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div
      className={cn(
        "px-4 pb-4 pt-2 sm:px-6 sm:pb-6",
        className,
      )}
    >
      <div className="mx-auto max-w-3xl">
        <div className="relative rounded-2xl border border-slate-200/80 bg-white shadow-lg ring-1 ring-slate-200/50">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(event) => setValue(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              connectionStatus !== "connected"
                ? "Connect to the server to start chatting…"
                : "Ask about sales, overdue accounts, invoices, margins…"
            }
            rows={1}
            disabled={
              connectionStatus !== "connected" || backendHealthy === false
            }
            className="block w-full resize-none bg-transparent py-3.5 pr-14 pl-4 text-sm leading-6 outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-60"
          />
          <Button
            onClick={handleSubmit}
            disabled={!canSend}
            size="icon-sm"
            className={cn(
              "absolute right-2 bottom-2 h-9 w-9 rounded-xl",
              canSend
                ? "bg-teal-600 hover:bg-teal-700"
                : "bg-slate-200 text-slate-400",
            )}
          >
            <SendHorizontal className="h-4 w-4" />
            <span className="sr-only">Send</span>
          </Button>
        </div>
        <p className="mt-2 hidden text-center text-[11px] text-muted-foreground/70 sm:block">
          Enter to send · Shift+Enter for new line · / to focus
        </p>
      </div>
    </div>
  );
}
