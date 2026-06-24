import { ChatSettings, DEFAULT_SETTINGS } from "@/lib/types";

const STORAGE_KEY = "billbay-chat-settings";

export function loadSettings(): ChatSettings {
  if (typeof window === "undefined") {
    return DEFAULT_SETTINGS;
  }

  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return DEFAULT_SETTINGS;
    }
    const parsed = JSON.parse(raw) as Partial<ChatSettings>;
    return {
      userId: parsed.userId ?? DEFAULT_SETTINGS.userId,
      accessLevel: parsed.accessLevel ?? DEFAULT_SETTINGS.accessLevel,
      apiUrl: parsed.apiUrl ?? DEFAULT_SETTINGS.apiUrl,
      wsUrl: parsed.wsUrl ?? DEFAULT_SETTINGS.wsUrl,
    };
  } catch {
    return DEFAULT_SETTINGS;
  }
}

export function saveSettings(settings: ChatSettings): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
}
