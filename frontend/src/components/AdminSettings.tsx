import { useState, useEffect } from "react";
import type { AdminSettings as AdminSettingsType, AdminSettingsUpdate } from "../types";
import {
  verifyAdminPassword,
  getAdminSettings,
  updateAdminSettings,
} from "../api/client";

interface Props {
  onClose: () => void;
}

export default function AdminSettings({ onClose }: Props) {
  const [password, setPassword] = useState("");
  const [authenticated, setAuthenticated] = useState(false);
  const [settings, setSettings] = useState<AdminSettingsType | null>(null);
  const [form, setForm] = useState<AdminSettingsUpdate>({});
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const handleVerify = async () => {
    setError("");
    setLoading(true);
    try {
      await verifyAdminPassword(password);
      setAuthenticated(true);
      const data = await getAdminSettings(password);
      setSettings(data);
    } catch {
      setError("비밀번호가 올바르지 않습니다.");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setError("");
    setSuccess("");
    setLoading(true);
    try {
      const data = await updateAdminSettings(password, form);
      setSettings(data);
      setForm({});
      setSuccess("설정이 저장되었습니다.");
    } catch {
      setError("설정 저장에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const getDisplayValue = (key: keyof AdminSettingsType) => {
    if (key in form && form[key as keyof AdminSettingsUpdate] !== undefined) {
      return form[key as keyof AdminSettingsUpdate] ?? "";
    }
    return settings?.[key] ?? "";
  };

  const handleChange = (key: keyof AdminSettingsUpdate, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }));
    setSuccess("");
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  const hasChanges = Object.keys(form).length > 0;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Admin Settings</h2>
          <button className="modal-close" onClick={onClose}>
            &times;
          </button>
        </div>

        {!authenticated ? (
          <div className="modal-body">
            <p className="settings-description">
              관리자 비밀번호를 입력하세요.
            </p>
            <div className="settings-field">
              <label>Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleVerify()}
                placeholder="Admin password"
                autoFocus
              />
            </div>
            {error && <p className="settings-error">{error}</p>}
            <div className="modal-actions">
              <button
                className="btn btn-primary"
                onClick={handleVerify}
                disabled={loading || !password}
              >
                {loading ? "확인 중..." : "확인"}
              </button>
            </div>
          </div>
        ) : (
          <div className="modal-body">
            <div className="settings-group">
              <h3>AI Service</h3>
              <div className="settings-field">
                <label>Base URL</label>
                <input
                  type="text"
                  value={getDisplayValue("ai_base_url")}
                  onChange={(e) => handleChange("ai_base_url", e.target.value)}
                  placeholder="http://localhost:8000/v1"
                />
              </div>
              <div className="settings-field">
                <label>API Key</label>
                <input
                  type="password"
                  value={getDisplayValue("ai_api_key")}
                  onChange={(e) => handleChange("ai_api_key", e.target.value)}
                  placeholder="API key"
                />
              </div>
              <div className="settings-field">
                <label>Model Name</label>
                <input
                  type="text"
                  value={getDisplayValue("ai_model_name")}
                  onChange={(e) => handleChange("ai_model_name", e.target.value)}
                  placeholder="default-model"
                />
              </div>
            </div>

            <div className="settings-group">
              <h3>Jira</h3>
              <div className="settings-field">
                <label>Base URL</label>
                <input
                  type="text"
                  value={getDisplayValue("jira_base_url")}
                  onChange={(e) => handleChange("jira_base_url", e.target.value)}
                  placeholder="https://yourorg.atlassian.net"
                />
              </div>
              <div className="settings-field">
                <label>User Email</label>
                <input
                  type="email"
                  value={getDisplayValue("jira_user_email")}
                  onChange={(e) =>
                    handleChange("jira_user_email", e.target.value)
                  }
                  placeholder="user@example.com"
                />
              </div>
              <div className="settings-field">
                <label>API Token</label>
                <input
                  type="password"
                  value={getDisplayValue("jira_api_token")}
                  onChange={(e) =>
                    handleChange("jira_api_token", e.target.value)
                  }
                  placeholder="Jira API token"
                />
              </div>
              <div className="settings-field">
                <label>Project Key</label>
                <input
                  type="text"
                  value={getDisplayValue("jira_project_key")}
                  onChange={(e) =>
                    handleChange("jira_project_key", e.target.value)
                  }
                  placeholder="VOC"
                />
              </div>
            </div>

            {error && <p className="settings-error">{error}</p>}
            {success && <p className="settings-success">{success}</p>}

            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={onClose}>
                닫기
              </button>
              <button
                className="btn btn-primary"
                onClick={handleSave}
                disabled={loading || !hasChanges}
              >
                {loading ? "저장 중..." : "저장"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
