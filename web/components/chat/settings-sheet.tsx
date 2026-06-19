"use client";

import { useState } from "react";
import { Settings2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { Separator } from "@/components/ui/separator";
import { useChat } from "@/providers/chat-provider";
import type { ChatSettings } from "@/lib/types";

export function SettingsSheet() {
  const { settings, updateSettings, sessionId, reconnect, clearMessages } =
    useChat();
  const [draft, setDraft] = useState<ChatSettings>(settings);
  const [open, setOpen] = useState(false);

  const handleOpenChange = (next: boolean) => {
    if (next) {
      setDraft(settings);
    }
    setOpen(next);
  };

  const handleSave = () => {
    updateSettings({
      ...draft,
      userId: Number(draft.userId) || 42,
      accessLevel: Number(draft.accessLevel) || 50,
    });
    setOpen(false);
  };

  return (
    <Sheet open={open} onOpenChange={handleOpenChange}>
      <SheetTrigger
        render={
          <Button variant="outline" size="sm" className="gap-2">
            <Settings2 className="h-4 w-4" />
            <span className="hidden sm:inline">Settings</span>
          </Button>
        }
      />
      <SheetContent className="w-full sm:max-w-md">
        <SheetHeader>
          <SheetTitle>Connection settings</SheetTitle>
          <SheetDescription>
            Demo mode — set user identity for WebSocket access. Changes reconnect
            the session and clear chat history.
          </SheetDescription>
        </SheetHeader>

        <div className="space-y-6 px-4">
          <section className="space-y-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
                Identity
              </p>
              <Separator className="mt-2" />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium" htmlFor="userId">
                User ID
              </label>
              <Input
                id="userId"
                type="number"
                value={draft.userId}
                onChange={(event) =>
                  setDraft({ ...draft, userId: Number(event.target.value) })
                }
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium" htmlFor="accessLevel">
                Access level
              </label>
              <Input
                id="accessLevel"
                type="number"
                value={draft.accessLevel}
                onChange={(event) =>
                  setDraft({
                    ...draft,
                    accessLevel: Number(event.target.value),
                  })
                }
              />
            </div>
          </section>

          <section className="space-y-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
                Connection
              </p>
              <Separator className="mt-2" />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium" htmlFor="apiUrl">
                API URL
              </label>
              <Input
                id="apiUrl"
                value={draft.apiUrl}
                onChange={(event) =>
                  setDraft({ ...draft, apiUrl: event.target.value })
                }
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium" htmlFor="wsUrl">
                WebSocket URL
              </label>
              <Input
                id="wsUrl"
                value={draft.wsUrl}
                onChange={(event) =>
                  setDraft({ ...draft, wsUrl: event.target.value })
                }
              />
            </div>
          </section>

          {sessionId ? (
            <div className="rounded-lg border bg-slate-50 p-3 text-xs text-muted-foreground">
              <p className="font-medium text-slate-700">Session ID</p>
              <p className="mt-1 break-all font-mono">{sessionId}</p>
            </div>
          ) : null}
        </div>

        <SheetFooter className="gap-2 sm:flex-col sm:items-stretch">
          <Button onClick={handleSave} className="bg-teal-600 hover:bg-teal-700">
            Save & reconnect
          </Button>
          <Button variant="outline" onClick={reconnect}>
            Reconnect
          </Button>
          <Button variant="ghost" onClick={clearMessages}>
            Clear chat
          </Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  );
}
