import { useEffect, useRef } from "react";
import { useChat } from "../hooks/useChat";
import ChatInput from "./ChatInput";
import MessageBubble from "./MessageBubble";
import LoadingIndicator from "./LoadingIndicator";

export default function ChatWindow() {
  const {
    messages,
    isLoading,
    pendingTemplate,
    sendMessage,
    confirmTemplate,
    setPendingTemplate,
  } = useChat();

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const lastTemplatePreviewIndex = messages
    .map((m, i) => (m.type === "template_preview" ? i : -1))
    .filter((i) => i >= 0)
    .pop();

  return (
    <div className="chat-window">
      <div className="chat-header">
        <h1>VOC to Jira</h1>
        <p>고객의 소리를 입력하면 AI가 적절한 Jira 티켓을 생성합니다</p>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="welcome-message">
            <p>안녕하세요! VOC 내용을 입력해 주세요.</p>
            <p className="welcome-hint">
              예: "로그인 페이지에서 500 에러가 발생합니다"
            </p>
          </div>
        )}

        {messages.map((msg, index) => (
          <MessageBubble
            key={msg.id}
            message={msg}
            onConfirm={
              index === lastTemplatePreviewIndex && pendingTemplate
                ? confirmTemplate
                : undefined
            }
            onCancel={
              index === lastTemplatePreviewIndex && pendingTemplate
                ? () => setPendingTemplate(null)
                : undefined
            }
          />
        ))}

        {isLoading && <LoadingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      <ChatInput onSend={sendMessage} disabled={isLoading} />
    </div>
  );
}
