"use client";

import { useEffect, useRef } from "react";

import { AssistantCard } from "@/components/chat/assistant-card";
import { LoadingIndicator } from "@/components/chat/loading-indicator";
import { UserBubble } from "@/components/chat/user-bubble";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useChat } from "@/providers/chat-provider";

export function MessageList() {
  const { messages, isLoading } = useChat();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <ScrollArea className="h-full flex-1 px-4 py-6 sm:px-6 sm:py-8">
      <div className="mx-auto flex max-w-3xl flex-col gap-8">
        {messages.map((message) =>
          message.role === "user" ? (
            <UserBubble
              key={message.id}
              content={message.content}
              timestamp={message.timestamp}
            />
          ) : (
            <AssistantCard key={message.id} message={message} />
          ),
        )}
        {isLoading ? <LoadingIndicator /> : null}
        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  );
}
