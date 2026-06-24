"use client";

import { BarChart3, Menu, RefreshCw } from "lucide-react";
import { useState } from "react";

import { ChatInput } from "@/components/chat/chat-input";
import { ChatSidebar } from "@/components/chat/chat-sidebar";
import { ConnectionStatusBadge } from "@/components/chat/connection-status";
import { MessageList } from "@/components/chat/message-list";
import { SettingsSheet } from "@/components/chat/settings-sheet";
import { SuggestedPrompts } from "@/components/chat/suggested-prompts";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { useChat } from "@/providers/chat-provider";
import { cn } from "@/lib/utils";

function StatusBanner() {
  const { backendHealthy, connectionStatus, reconnect } = useChat();

  const showDisconnected =
    connectionStatus === "disconnected" || connectionStatus === "error";
  const showBackendDown = backendHealthy === false;

  if (!showDisconnected && !showBackendDown) {
    return null;
  }

  return (
    <div
      className={cn(
        "flex items-center justify-between gap-3 px-4 py-2 text-xs",
        showBackendDown
          ? "bg-red-50 text-red-800"
          : "bg-amber-50 text-amber-900",
      )}
    >
      <p>
        {showBackendDown
          ? "Backend unreachable — check that the API is running on port 8000."
          : "Connection lost — messages won't send until reconnected."}
      </p>
      <Button
        variant="outline"
        size="sm"
        className="h-7 shrink-0 bg-white/80 text-xs"
        onClick={reconnect}
      >
        Reconnect
      </Button>
    </div>
  );
}

export function ChatApp() {
  const { messages, reconnect, connectionStatus } = useChat();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const showEmptyState = messages.length === 0;
  const showReconnect =
    connectionStatus === "disconnected" || connectionStatus === "error";

  return (
    <div className="flex h-dvh flex-col bg-white">
      <header className="flex h-14 shrink-0 items-center justify-between border-b border-slate-200/80 bg-white px-4 shadow-sm">
        <div className="flex items-center gap-3">
          <Sheet open={mobileNavOpen} onOpenChange={setMobileNavOpen}>
            <SheetTrigger
              render={
                <Button variant="outline" size="icon-sm" className="lg:hidden">
                  <Menu className="h-4 w-4" />
                </Button>
              }
            />
            <SheetContent
              side="left"
              className="w-[min(100vw,20rem)] border-slate-800 bg-slate-900 p-0 text-slate-200"
            >
              <SheetHeader className="border-b border-slate-800 px-4 py-3">
                <SheetTitle className="text-slate-100">Explore reports</SheetTitle>
              </SheetHeader>
              <ChatSidebar mobile showPrompts={showEmptyState} />
            </SheetContent>
          </Sheet>

          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-slate-900 to-teal-700 text-white shadow-md shadow-teal-900/20">
              <BarChart3 className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-sm font-semibold tracking-tight text-slate-900 sm:text-base">
                BillBay Intelligence
              </h1>
              <p className="hidden text-xs text-muted-foreground sm:block">
                Conversational BI for sales &amp; finance
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <ConnectionStatusBadge />
          {showReconnect ? (
            <Button
              variant="outline"
              size="sm"
              onClick={reconnect}
              className="hidden gap-1 sm:flex"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              Reconnect
            </Button>
          ) : null}
          <SettingsSheet />
        </div>
      </header>

      <StatusBanner />

      <div className="flex min-h-0 flex-1">
        <ChatSidebar
          className="hidden lg:flex"
          showPrompts={showEmptyState}
        />

        <main className="chat-canvas-bg flex min-w-0 flex-1 flex-col">
          <div className="min-h-0 flex-1 overflow-hidden">
            {showEmptyState ? <SuggestedPrompts /> : <MessageList />}
          </div>
          <ChatInput />
        </main>
      </div>
    </div>
  );
}
