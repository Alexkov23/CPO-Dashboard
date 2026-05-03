import { useMemo, useState } from "react";
import type { TasksGroupedByDate } from "../types";

interface TaskListProps {
  groups: TasksGroupedByDate[];
  loading: boolean;
  statusFilter: "all" | "done" | "active";
}

const DATES_PER_PAGE = 5;

function formatDate(dateStr: string): string {
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("ru-RU", {
    weekday: "short",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

export function TaskList({ groups, loading, statusFilter }: TaskListProps) {
  const [expandedTasks, setExpandedTasks] = useState<Set<number>>(new Set());
  const [page, setPage] = useState(0);

  const filtered = useMemo(() => {
    if (statusFilter === "all") return groups;

    return groups
      .map((g) => ({
        ...g,
        tasks: g.tasks.filter((t) =>
          statusFilter === "done" ? t.done : !t.done
        ),
      }))
      .filter((g) => g.tasks.length > 0);
  }, [groups, statusFilter]);

  const totalPages = Math.ceil(filtered.length / DATES_PER_PAGE);
  const pagedGroups = filtered.slice(
    page * DATES_PER_PAGE,
    (page + 1) * DATES_PER_PAGE
  );

  const toggleExpand = (taskId: number) => {
    setExpandedTasks((prev) => {
      const next = new Set(prev);
      if (next.has(taskId)) {
        next.delete(taskId);
      } else {
        next.add(taskId);
      }
      return next;
    });
  };

  if (loading) {
    return <div className="task-list loading">Загрузка задач...</div>;
  }

  if (filtered.length === 0) {
    return (
      <div className="task-list empty">
        <p>
          {groups.length === 0
            ? "Нет задач. Добавьте проект и синхронизируйте данные."
            : "Нет задач с выбранным фильтром."}
        </p>
      </div>
    );
  }

  const totalTasks = filtered.reduce((s, g) => s + g.tasks.length, 0);

  return (
    <div className="task-list">
      {pagedGroups.map((group) => (
        <div key={group.date} className="task-group">
          <h3 className="task-group-date">
            {formatDate(group.date)}
            <span className="task-group-count">{group.tasks.length}</span>
          </h3>
          <div className="task-items">
            {group.tasks.map((task) => {
              const isExpanded = expandedTasks.has(task.id);
              const isLong = task.title.length > 80;
              return (
                <div
                  key={task.id}
                  className={`task-card ${task.done ? "done" : "active"} ${isExpanded ? "expanded" : ""}`}
                  onClick={() => isLong && toggleExpand(task.id)}
                >
                  <div className="task-card-header">
                    <span className="task-number">{task.number}.</span>
                    <span className="task-status-dot" />
                    <span className="task-project-badge">{task.project}</span>
                  </div>
                  <div className="task-title-preview">{task.title}</div>
                  {isLong && !isExpanded && (
                    <div className="task-expand-hint">
                      Нажмите чтобы развернуть
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      ))}

      {totalPages > 1 && (
        <div className="pagination">
          <button
            className="pagination-btn"
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
          >
            Назад
          </button>
          <span className="pagination-info">
            {page + 1} / {totalPages} ({totalTasks} задач)
          </span>
          <button
            className="pagination-btn"
            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
            disabled={page >= totalPages - 1}
          >
            Вперёд
          </button>
        </div>
      )}
    </div>
  );
}
