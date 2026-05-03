import type { DashboardMetrics } from "../types";

interface MetricsBarProps {
  metrics: DashboardMetrics | null;
  loading: boolean;
}

export function MetricsBar({ metrics, loading }: MetricsBarProps) {
  if (loading) {
    return <div className="metrics-bar loading">Загрузка метрик...</div>;
  }

  if (!metrics) return null;

  const pct =
    metrics.total_tasks > 0
      ? Math.round((metrics.total_done / metrics.total_tasks) * 100)
      : 0;

  return (
    <div className="metrics-section">
      <div className="metrics-bar">
        <div className="metric-card done">
          <span className="metric-value">{metrics.total_done}</span>
          <span className="metric-label">Выполнено</span>
        </div>
        <div className="metric-card active">
          <span className="metric-value">{metrics.total_active}</span>
          <span className="metric-label">Активных</span>
        </div>
        <div className="metric-card total">
          <span className="metric-value">{metrics.total_tasks}</span>
          <span className="metric-label">Всего</span>
        </div>
        <div className="metric-card today">
          <span className="metric-value">{metrics.done_today}</span>
          <span className="metric-label">Сегодня</span>
        </div>
        <div className="metric-card week">
          <span className="metric-value">{metrics.done_this_week}</span>
          <span className="metric-label">За неделю</span>
        </div>
      </div>

      <div className="progress-section">
        <div className="progress-header">
          <span className="progress-label">Прогресс выполнения</span>
          <span className="progress-pct">{pct}%</span>
        </div>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${pct}%` }} />
        </div>
      </div>
    </div>
  );
}
