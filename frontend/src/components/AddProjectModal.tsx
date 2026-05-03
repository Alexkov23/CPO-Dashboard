import { useState } from "react";
import type { SourceCreate } from "../types";

interface AddProjectModalProps {
  open: boolean;
  onClose: () => void;
  onAdd: (data: SourceCreate) => Promise<void>;
}

export function AddProjectModal({ open, onClose, onAdd }: AddProjectModalProps) {
  const [name, setName] = useState("");
  const [project, setProject] = useState("");
  const [docUrl, setDocUrl] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (!open) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!name.trim() || !project.trim() || !docUrl.trim()) {
      setError("Все поля обязательны");
      return;
    }

    if (!docUrl.includes("docs.google.com/document")) {
      setError("Введите корректную ссылку на Google Doc");
      return;
    }

    setSubmitting(true);
    try {
      await onAdd({ name: name.trim(), project: project.trim(), doc_url: docUrl.trim() });
      setName("");
      setProject("");
      setDocUrl("");
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка при добавлении");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Добавить проект</h2>
          <button className="modal-close" onClick={onClose}>
            &times;
          </button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Название источника</label>
            <input
              id="name"
              type="text"
              placeholder="Например: Еженедельные задачи"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label htmlFor="project">Проект</label>
            <input
              id="project"
              type="text"
              placeholder="Например: Marketing"
              value={project}
              onChange={(e) => setProject(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label htmlFor="docUrl">Ссылка на Google Doc</label>
            <input
              id="docUrl"
              type="url"
              placeholder="https://docs.google.com/document/d/...#tab=t.xxx"
              value={docUrl}
              onChange={(e) => setDocUrl(e.target.value)}
            />
            <small className="form-hint">
              Система автоматически извлечёт doc_id и tab из URL
            </small>
          </div>
          {error && <div className="form-error">{error}</div>}
          <div className="form-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Отмена
            </button>
            <button type="submit" className="btn-primary" disabled={submitting}>
              {submitting ? "Добавление..." : "Добавить"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
