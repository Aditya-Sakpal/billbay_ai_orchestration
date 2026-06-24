import { ChatApp } from "@/components/chat/chat-app";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ChatProvider } from "@/providers/chat-provider";

export default function App() {
  return (
    <TooltipProvider>
      <ChatProvider>
        <ChatApp />
      </ChatProvider>
    </TooltipProvider>
  );
}
