import type { AdminSettings, AdminSettingsUpdate, ChatResponse, ConfirmResponse } from "../types";

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

export async function verifyAdminPassword(
  password: string
): Promise<{ ok: boolean }> {
  const response = await fetch(`${API_BASE}/api/admin/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password }),
  });
  if (!response.ok) {
    throw new Error("Invalid password");
  }
  return response.json();
}

export async function getAdminSettings(
  password: string
): Promise<AdminSettings> {
  const response = await fetch(`${API_BASE}/api/admin/settings`, {
    headers: { "X-Admin-Password": password },
  });
  if (!response.ok) {
    throw new Error(`Settings API error: ${response.status}`);
  }
  return response.json();
}

export async function updateAdminSettings(
  password: string,
  updates: AdminSettingsUpdate
): Promise<AdminSettings> {
  const response = await fetch(`${API_BASE}/api/admin/settings`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "X-Admin-Password": password,
    },
    body: JSON.stringify(updates),
  });
  if (!response.ok) {
    throw new Error(`Settings update error: ${response.status}`);
  }
  return response.json();
}
