import { useState, useCallback, useRef } from "react";
import type { ChatMessage } from "../types";
import { sendChatMessage, confirmTicket } from "../api/client";

function generateId(): string {
  return crypto.randomUUID();
}

export function useChat() {
  const [sessionId] = useState(() => generateId());
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [pendingTemplate, setPendingTemplate] = useState<{
    template_id: string;
    template_name: string;
    fields: Record<string, string>;
  } | null>(null);

  // Prevent double-sends
  const sendingRef = useRef(false);

  const sendMessage = useCallback(
    async (text: string) => {
      if (sendingRef.current || !text.trim()) return;
      sendingRef.current = true;
      setIsLoading(true);

      const userMsg: ChatMessage = {
        id: generateId(),
        role: "user",
        content: text,
        type: "text",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);

      try {
        const response = await sendChatMessage(sessionId, text);

        const assistantMsg: ChatMessage = {
          id: generateId(),
          role: "assistant",
          content: response.message,
          type: response.type,
          metadata: response.metadata ?? undefined,
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, assistantMsg]);

        if (
          response.type === "template_preview" &&
          response.metadata?.template_id
        ) {
          setPendingTemplate({
            template_id: response.metadata.template_id,
            template_name: response.metadata.template_name ?? "",
            fields: (response.metadata.fields as Record<string, string>) ?? {},
          });
        } else {
          setPendingTemplate(null);
        }
      } catch (err) {
        const errorMsg: ChatMessage = {
          id: generateId(),
          role: "assistant",
          content: "오류가 발생했습니다. 다시 시도해 주세요.",
          type: "text",
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, errorMsg]);
      } finally {
        setIsLoading(false);
        sendingRef.current = false;
      }
    },
    [sessionId]
  );

  const confirmTemplate = useCallback(
    async (fields: Record<string, string>) => {
      if (!pendingTemplate) return;
      setIsLoading(true);

      try {
        const result = await confirmTicket(
          sessionId,
          pendingTemplate.template_id,
          fields
        );

        const ticketMsg: ChatMessage = {
          id: generateId(),
          role: "assistant",
          content: `Jira 티켓 **${result.ticket_key}**이(가) 생성되었습니다!`,
          type: "ticket_created",
          metadata: {
            ticket_key: result.ticket_key,
            ticket_url: result.ticket_url,
          },
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, ticketMsg]);
        setPendingTemplate(null);
      } catch (err) {
        const errorMsg: ChatMessage = {
          id: generateId(),
          role: "assistant",
          content: "Jira 티켓 생성 중 오류가 발생했습니다. 다시 시도해 주세요.",
          type: "text",
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, errorMsg]);
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId, pendingTemplate]
  );

  return {
    sessionId,
    messages,
    isLoading,
    pendingTemplate,
    sendMessage,
    confirmTemplate,
    setPendingTemplate,
  };
}
