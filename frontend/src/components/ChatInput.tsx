import { useState, useRef, useEffect } from "react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled: boolean;
}

export default function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [text, setText] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  }, [text]);

  const handleSubmit = () => {
    if (text.trim() && !disabled) {
      onSend(text.trim());
      setText("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="chat-input-container">
      <textarea
        ref={textareaRef}
        className="chat-input"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="VOC 내용을 입력하세요... (Enter로 전송, Shift+Enter로 줄바꿈)"
        disabled={disabled}
        rows={1}
      />
      <button
        className="send-button"
        onClick={handleSubmit}
        disabled={disabled || !text.trim()}
      >
        전송
      </button>
    </div>
  );
}
