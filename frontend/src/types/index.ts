export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  type: "text" | "template_preview" | "ticket_created";
  metadata?: {
    template_id?: string;
    template_name?: string;
    fields?: Record<string, string>;
    ticket_key?: string;
    ticket_url?: string;
  };
  timestamp: string;
}

export interface ChatResponse {
  session_id: string;
  message: string;
  type: "text" | "template_preview" | "ticket_created";
  metadata?: {
    template_id?: string;
    template_name?: string;
    fields?: Record<string, string>;
    ticket_key?: string;
    ticket_url?: string;
  };
}

export interface ConfirmResponse {
  ticket_key: string;
  ticket_url: string;
}

export interface TemplateSummary {
  id: string;
  name: string;
  description: string;
  jira_issue_type: string;
  keywords: string[];
}

export interface AdminSettings {
  ai_base_url: string;
  ai_api_key: string;
  ai_model_name: string;
  jira_base_url: string;
  jira_user_email: string;
  jira_api_token: string;
  jira_project_key: string;
}

export interface AdminSettingsUpdate {
  ai_base_url?: string;
  ai_api_key?: string;
  ai_model_name?: string;
  jira_base_url?: string;
  jira_user_email?: string;
  jira_api_token?: string;
  jira_project_key?: string;
}
