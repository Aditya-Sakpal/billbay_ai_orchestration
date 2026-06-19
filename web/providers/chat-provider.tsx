"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useReducer,
  useRef,
  useState,
  type ReactNode,
} from "react";

import { loadSettings, saveSettings } from "@/lib/storage";
import {
  type ChatMessage,
  type ChatSettings,
  type ConnectionStatus,
  DEFAULT_SETTINGS,
  type WsResponse,
} from "@/lib/types";

interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  connectionStatus: ConnectionStatus;
  sessionId: string | null;
  backendHealthy: boolean | null;
}

type ChatAction =
  | { type: "ADD_USER_MESSAGE"; payload: ChatMessage }
  | { type: "ADD_ASSISTANT_MESSAGE"; payload: ChatMessage }
  | { type: "SET_LOADING"; payload: boolean }
  | { type: "SET_CONNECTION"; payload: ConnectionStatus }
  | { type: "SET_SESSION"; payload: string | null }
  | { type: "CLEAR_MESSAGES" }
  | { type: "SET_BACKEND_HEALTH"; payload: boolean | null };

function chatReducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case "ADD_USER_MESSAGE":
      return { ...state, messages: [...state.messages, action.payload] };
    case "ADD_ASSISTANT_MESSAGE":
      return {
        ...state,
        messages: [...state.messages, action.payload],
        isLoading: false,
      };
    case "SET_LOADING":
      return { ...state, isLoading: action.payload };
    case "SET_CONNECTION":
      return { ...state, connectionStatus: action.payload };
    case "SET_SESSION":
      return { ...state, sessionId: action.payload };
    case "CLEAR_MESSAGES":
      return { ...state, messages: [], sessionId: null };
    case "SET_BACKEND_HEALTH":
      return { ...state, backendHealthy: action.payload };
    default:
      return state;
  }
}

interface ChatContextValue {
  messages: ChatMessage[];
  isLoading: boolean;
  connectionStatus: ConnectionStatus;
  sessionId: string | null;
  backendHealthy: boolean | null;
  settings: ChatSettings;
  updateSettings: (next: ChatSettings) => void;
  sendMessage: (text: string) => void;
  reconnect: () => void;
  clearMessages: () => void;
}

const ChatContext = createContext<ChatContextValue | null>(null);

function createMessageId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

export function ChatProvider({ children }: { children: ReactNode }) {
  const [settings, setSettings] = useState<ChatSettings>(() =>
    typeof window !== "undefined" ? loadSettings() : DEFAULT_SETTINGS,
  );
  const [state, dispatch] = useReducer(chatReducer, {
    messages: [],
    isLoading: false,
    connectionStatus: "idle",
    sessionId: null,
    backendHealthy: null,
  });

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const settingsRef = useRef(settings);

  useEffect(() => {
    settingsRef.current = settings;
  }, [settings]);

  const checkHealth = useCallback(async () => {
    try {
      const res = await fetch(`${settingsRef.current.apiUrl}/health`);
      dispatch({
        type: "SET_BACKEND_HEALTH",
        payload: res.ok,
      });
    } catch {
      dispatch({ type: "SET_BACKEND_HEALTH", payload: false });
    }
  }, []);

  const disconnect = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.onclose = null;
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const connect = useCallback(() => {
    disconnect();
    dispatch({ type: "SET_CONNECTION", payload: "connecting" });

    const { wsUrl, userId, accessLevel } = settingsRef.current;
    const url = `${wsUrl}/ws/chat?user_id=${userId}&access_level=${accessLevel}`;

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        dispatch({ type: "SET_CONNECTION", payload: "connected" });
      };

      ws.onmessage = (event) => {
        let payload: WsResponse;
        try {
          payload = JSON.parse(event.data as string) as WsResponse;
        } catch {
          dispatch({
            type: "ADD_ASSISTANT_MESSAGE",
            payload: {
              id: createMessageId(),
              role: "assistant",
              content: "Received an invalid response from the server.",
              timestamp: new Date(),
              isError: true,
            },
          });
          return;
        }

        dispatch({ type: "SET_SESSION", payload: payload.session_id });
        dispatch({
          type: "ADD_ASSISTANT_MESSAGE",
          payload: {
            id: createMessageId(),
            role: "assistant",
            content: payload.answer,
            timestamp: new Date(),
            report: payload.report,
            filters: payload.filters,
            sessionId: payload.session_id,
            isError: payload.error === true,
          },
        });
      };

      ws.onerror = () => {
        dispatch({ type: "SET_CONNECTION", payload: "error" });
        dispatch({ type: "SET_LOADING", payload: false });
      };

      ws.onclose = () => {
        wsRef.current = null;
        dispatch({ type: "SET_CONNECTION", payload: "disconnected" });
        dispatch({ type: "SET_LOADING", payload: false });
      };
    } catch {
      dispatch({ type: "SET_CONNECTION", payload: "error" });
    }
  }, [disconnect]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    void checkHealth();
    connect();
    return () => disconnect();
  }, [settings.userId, settings.accessLevel, settings.wsUrl, connect, disconnect, checkHealth]);

  const sendMessage = useCallback(
    (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || state.isLoading) {
        return;
      }

      const ws = wsRef.current;
      if (!ws || ws.readyState !== WebSocket.OPEN) {
        dispatch({
          type: "ADD_ASSISTANT_MESSAGE",
          payload: {
            id: createMessageId(),
            role: "assistant",
            content:
              "Not connected to the server. Check your settings and try reconnecting.",
            timestamp: new Date(),
            isError: true,
          },
        });
        return;
      }

      dispatch({
        type: "ADD_USER_MESSAGE",
        payload: {
          id: createMessageId(),
          role: "user",
          content: trimmed,
          timestamp: new Date(),
        },
      });
      dispatch({ type: "SET_LOADING", payload: true });
      ws.send(trimmed);
    },
    [state.isLoading],
  );

  const updateSettings = useCallback(
    (next: ChatSettings) => {
      saveSettings(next);
      setSettings(next);
      dispatch({ type: "CLEAR_MESSAGES" });
    },
    [],
  );

  const reconnect = useCallback(() => {
    void checkHealth();
    connect();
  }, [checkHealth, connect]);

  const clearMessages = useCallback(() => {
    dispatch({ type: "CLEAR_MESSAGES" });
  }, []);

  const value = useMemo<ChatContextValue>(
    () => ({
      messages: state.messages,
      isLoading: state.isLoading,
      connectionStatus: state.connectionStatus,
      sessionId: state.sessionId,
      backendHealthy: state.backendHealthy,
      settings,
      updateSettings,
      sendMessage,
      reconnect,
      clearMessages,
    }),
    [
      state.messages,
      state.isLoading,
      state.connectionStatus,
      state.sessionId,
      state.backendHealthy,
      settings,
      updateSettings,
      sendMessage,
      reconnect,
      clearMessages,
    ],
  );

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

export function useChat(): ChatContextValue {
  const ctx = useContext(ChatContext);
  if (!ctx) {
    throw new Error("useChat must be used within ChatProvider");
  }
  return ctx;
}
