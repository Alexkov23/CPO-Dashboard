import type { Source } from "../types";

interface SourceListProps {
  sources: Source[];
  onToggle: (id: string, enabled: boolean) => void;
  onDelete: (id: string) => void;
  onSync: (id: string) => void;
  syncing: string | null;
}

export function SourceList({ sources, onToggle, onDelete, onSync, syncing }: SourceListProps) {
  if (sources.length === 0) {
    return (
      <div className="source-list empty">
        <p>Нет источников. Нажмите "+" чтобы добавить проект.</p>
      </div>
    );
  }

  return (
    <div className="source-list">
      {sources.map((source) => (
        <div key={source.id} className={`source-card ${source.enabled ? "" : "disabled"}`}>
          <div className="source-info">
            <h4>{source.name}</h4>
            <span className="source-project">{source.project}</span>
            <span className="source-doc">doc: {source.doc_id.substring(0, 12)}...</span>
            {source.section && (
              <span className="source-section">tab: {source.section}</span>
            )}
          </div>
          <div className="source-actions">
            <button
              className="btn-icon"
              onClick={() => onSync(source.id)}
              disabled={syncing === source.id || !source.enabled}
              title="Синхронизировать"
            >
              {syncing === source.id ? "..." : "Sync"}
            </button>
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={source.enabled}
                onChange={() => onToggle(source.id, !source.enabled)}
              />
              <span className="toggle-slider"></span>
            </label>
            <button
              className="btn-icon btn-delete"
              onClick={() => {
                if (confirm("Удалить источник и все его задачи?")) {
                  onDelete(source.id);
                }
              }}
              title="Удалить"
            >
              Del
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
