import type { ChatMessage } from "../types";
import TemplatePreview from "./TemplatePreview";
import TicketCard from "./TicketCard";

interface MessageBubbleProps {
  message: ChatMessage;
  onConfirm?: (fields: Record<string, string>) => void;
  onCancel?: () => void;
}

export default function MessageBubble({
  message,
  onConfirm,
  onCancel,
}: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`message ${isUser ? "user" : "assistant"}`}>
      <div className="message-inner">
        {!isUser && (
          <div className="assistant-avatar">
            <span className="avatar-icon">&#10024;</span>
          </div>
        )}
        <div
          className={`message-content ${isUser ? "user-content" : "assistant-content"}`}
        >
          {message.type === "template_preview" && message.metadata?.fields && onConfirm && onCancel ? (
            <TemplatePreview
              templateName={message.metadata.template_name ?? "템플릿"}
              fields={message.metadata.fields}
              onConfirm={onConfirm}
              onCancel={onCancel}
            />
          ) : message.type === "ticket_created" && message.metadata?.ticket_key ? (
            <TicketCard
              ticketKey={message.metadata.ticket_key}
              ticketUrl={message.metadata.ticket_url ?? "#"}
            />
          ) : (
            <div className="message-text">{message.content}</div>
          )}
        </div>
      </div>
    </div>
  );
}
