import { useMemo } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import type { TasksGroupedByDate } from "../types";

interface TaskChartProps {
  groups: TasksGroupedByDate[];
}

interface ChartData {
  date: string;
  done: number;
  active: number;
}

function formatShortDate(dateStr: string): string {
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("ru-RU", { day: "2-digit", month: "2-digit" });
}

export function TaskChart({ groups }: TaskChartProps) {
  const data = useMemo<ChartData[]>(() => {
    const recent = groups.slice(0, 20).reverse();
    return recent.map((g) => ({
      date: formatShortDate(g.date),
      done: g.tasks.filter((t) => t.done).length,
      active: g.tasks.filter((t) => !t.done).length,
    }));
  }, [groups]);

  if (data.length === 0) return null;

  return (
    <div className="chart-container">
      <h3 className="chart-title">Задачи по датам</h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} barGap={0} barCategoryGap="20%">
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="date"
            tick={{ fill: "#6b7280", fontSize: 11 }}
            axisLine={{ stroke: "#e5e7eb" }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: "#6b7280", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            width={30}
          />
          <Tooltip
            contentStyle={{
              background: "#fff",
              border: "1px solid #e5e7eb",
              borderRadius: "8px",
              color: "#1a1a2e",
              fontSize: 13,
              boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
            }}
          />
          <Bar
            dataKey="done"
            name="Выполнено"
            fill="#10b981"
            radius={[4, 4, 0, 0]}
            stackId="tasks"
          />
          <Bar
            dataKey="active"
            name="Активных"
            fill="#d1d5db"
            radius={[4, 4, 0, 0]}
            stackId="tasks"
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
