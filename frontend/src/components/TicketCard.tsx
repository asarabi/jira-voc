interface TicketCardProps {
  ticketKey: string;
  ticketUrl: string;
}

export default function TicketCard({ ticketKey, ticketUrl }: TicketCardProps) {
  return (
    <div className="ticket-card">
      <div className="ticket-card-header">
        <span className="ticket-icon">&#9989;</span>
        <span className="ticket-title">Jira 티켓 생성 완료</span>
      </div>
      <div className="ticket-card-body">
        <span className="ticket-key">{ticketKey}</span>
        <a
          href={ticketUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="ticket-link"
        >
          Jira에서 보기 &rarr;
        </a>
      </div>
    </div>
  );
}
