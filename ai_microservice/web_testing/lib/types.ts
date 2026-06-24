export type ConnectionStatus =
  | "idle"
  | "connecting"
  | "connected"
  | "disconnected"
  | "error";

export type MessageRole = "user" | "assistant";

export interface WsResponse {
  answer: string;
  report: string | null;
  filters: Record<string, unknown>;
  session_id: string;
  error?: boolean;
}

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  report?: string | null;
  filters?: Record<string, unknown>;
  sessionId?: string;
  isError?: boolean;
  isInfo?: boolean;
}

export interface ChatSettings {
  userId: number;
  accessLevel: number;
  apiUrl: string;
  wsUrl: string;
}

export const DEFAULT_SETTINGS: ChatSettings = {
  userId: 42,
  accessLevel: 50,
  apiUrl: import.meta.env.VITE_API_URL ?? "http://localhost:8000",
  wsUrl: import.meta.env.VITE_WS_URL ?? "ws://localhost:8000",
};
