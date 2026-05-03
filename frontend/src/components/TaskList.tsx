import type { TasksGroupedByDate } from "../types";

interface TaskListProps {
  groups: TasksGroupedByDate[];
  loading: boolean;
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("ru-RU", {
    weekday: "short",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

export function TaskList({ groups, loading }: TaskListProps) {
  if (loading) {
    return <div className="task-list loading">Загрузка задач...</div>;
  }

  if (groups.length === 0) {
    return (
      <div className="task-list empty">
        <p>Нет задач. Добавьте проект и синхронизируйте данные.</p>
      </div>
    );
  }

  return (
    <div className="task-list">
      {groups.map((group) => (
        <div key={group.date} className="task-group">
          <h3 className="task-group-date">{formatDate(group.date)}</h3>
          <div className="task-items">
            {group.tasks.map((task) => (
              <div
                key={task.id}
                className={`task-item ${task.done ? "done" : "active"}`}
              >
                <span className="task-number">{task.number}.</span>
                <span className="task-status-icon">
                  {task.done ? "+" : ""}
                </span>
                <span className="task-title">{task.title}</span>
                <span className="task-project-badge">{task.project}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
