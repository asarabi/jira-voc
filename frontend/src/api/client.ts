import type { ChatResponse, ConfirmResponse } from "../types";

const API_BASE = import.meta.env.VITE_API_URL || "";

export async function sendChatMessage(
  sessionId: string,
  message: string
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message }),
  });
  if (!response.ok) {
    throw new Error(`Chat API error: ${response.status}`);
  }
  return response.json();
}

export async function confirmTicket(
  sessionId: string,
  templateId: string,
  fields: Record<string, string>
): Promise<ConfirmResponse> {
  const response = await fetch(`${API_BASE}/api/chat/${sessionId}/confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ template_id: templateId, fields }),
  });
  if (!response.ok) {
    throw new Error(`Confirm API error: ${response.status}`);
  }
  return response.json();
}
