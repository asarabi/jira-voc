export default function LoadingIndicator() {
  return (
    <div className="message assistant">
      <div className="message-inner">
        <div className="assistant-avatar">
          <span className="avatar-icon">&#10024;</span>
        </div>
        <div className="message-content assistant-content">
          <div className="loading-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>
  );
}
