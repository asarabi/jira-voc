import { useState } from "react";

interface TemplatePreviewProps {
  templateName: string;
  fields: Record<string, string>;
  onConfirm: (fields: Record<string, string>) => void;
  onCancel: () => void;
}

export default function TemplatePreview({
  templateName,
  fields,
  onConfirm,
  onCancel,
}: TemplatePreviewProps) {
  const [editableFields, setEditableFields] = useState<Record<string, string>>(
    { ...fields }
  );
  const [isEditing, setIsEditing] = useState(false);

  const handleFieldChange = (key: string, value: string) => {
    setEditableFields((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <div className="template-preview">
      <div className="template-preview-header">
        <span className="template-icon">&#128203;</span>
        <span className="template-title">{templateName}</span>
      </div>

      <div className="template-fields">
        {Object.entries(editableFields).map(([key, value]) => (
          <div key={key} className="template-field">
            <label className="field-label">{key}</label>
            {isEditing ? (
              key === "description" ? (
                <textarea
                  className="field-input field-textarea"
                  value={value}
                  onChange={(e) => handleFieldChange(key, e.target.value)}
                />
              ) : (
                <input
                  className="field-input"
                  value={value}
                  onChange={(e) => handleFieldChange(key, e.target.value)}
                />
              )
            ) : (
              <div className="field-value">{value}</div>
            )}
          </div>
        ))}
      </div>

      <div className="template-actions">
        {isEditing ? (
          <>
            <button
              className="btn btn-primary"
              onClick={() => setIsEditing(false)}
            >
              수정 완료
            </button>
            <button className="btn btn-secondary" onClick={onCancel}>
              취소
            </button>
          </>
        ) : (
          <>
            <button
              className="btn btn-primary"
              onClick={() => onConfirm(editableFields)}
            >
              티켓 생성
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => setIsEditing(true)}
            >
              수정
            </button>
            <button className="btn btn-ghost" onClick={onCancel}>
              취소
            </button>
          </>
        )}
      </div>
    </div>
  );
}
