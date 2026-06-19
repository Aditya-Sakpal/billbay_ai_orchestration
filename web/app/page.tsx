import { ChatApp } from "@/components/chat/chat-app";
import { ChatProvider } from "@/providers/chat-provider";

export default function Home() {
  return (
    <ChatProvider>
      <ChatApp />
    </ChatProvider>
  );
}
