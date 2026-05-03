import { useCallback, useEffect, useState } from "react";
import { api } from "./api/client";
import { AddProjectModal } from "./components/AddProjectModal";
import { MetricsBar } from "./components/MetricsBar";
import { SourceList } from "./components/SourceList";
import { TaskList } from "./components/TaskList";
import type {
  DashboardMetrics,
  Source,
  SourceCreate,
  TasksGroupedByDate,
} from "./types";
import "./App.css";

function App() {
  const [sources, setSources] = useState<Source[]>([]);
  const [tasks, setTasks] = useState<TasksGroupedByDate[]>([]);
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [projects, setProjects] = useState<string[]>([]);
  const [selectedProject, setSelectedProject] = useState<string>("");
  const [modalOpen, setModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [syncingAll, setSyncingAll] = useState(false);
  const [syncingSource, setSyncingSource] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"tasks" | "sources">("tasks");

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [sourcesData, tasksData, metricsData, projectsData] =
        await Promise.all([
          api.getSources(),
          api.getTasks(selectedProject || undefined),
          api.getMetrics(selectedProject || undefined),
          api.getProjects(),
        ]);
      setSources(sourcesData);
      setTasks(tasksData);
      setMetrics(metricsData);
      setProjects(projectsData);
    } catch (err) {
      console.error("Failed to load data:", err);
    } finally {
      setLoading(false);
    }
  }, [selectedProject]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleAddProject = async (data: SourceCreate) => {
    await api.createSource(data);
    await loadData();
  };

  const handleToggleSource = async (id: string, enabled: boolean) => {
    await api.toggleSource(id, enabled);
    await loadData();
  };

  const handleDeleteSource = async (id: string) => {
    await api.deleteSource(id);
    await loadData();
  };

  const handleSyncAll = async () => {
    setSyncingAll(true);
    try {
      await api.syncAll();
      await loadData();
    } finally {
      setSyncingAll(false);
    }
  };

  const handleSyncSource = async (id: string) => {
    setSyncingSource(id);
    try {
      await api.syncSource(id);
      await loadData();
    } finally {
      setSyncingSource(null);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>CPO Dashboard</h1>
        <div className="header-actions">
          <select
            className="project-filter"
            value={selectedProject}
            onChange={(e) => setSelectedProject(e.target.value)}
          >
            <option value="">Все проекты</option>
            {projects.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
          <button
            className="btn-sync"
            onClick={handleSyncAll}
            disabled={syncingAll}
          >
            {syncingAll ? "Синхронизация..." : "Sync All"}
          </button>
          <button className="btn-add" onClick={() => setModalOpen(true)}>
            +
          </button>
        </div>
      </header>

      <MetricsBar metrics={metrics} loading={loading} />

      <nav className="tab-nav">
        <button
          className={`tab-btn ${activeTab === "tasks" ? "active" : ""}`}
          onClick={() => setActiveTab("tasks")}
        >
          Задачи
        </button>
        <button
          className={`tab-btn ${activeTab === "sources" ? "active" : ""}`}
          onClick={() => setActiveTab("sources")}
        >
          Источники ({sources.length})
        </button>
      </nav>

      <main className="app-main">
        {activeTab === "tasks" ? (
          <TaskList groups={tasks} loading={loading} />
        ) : (
          <SourceList
            sources={sources}
            onToggle={handleToggleSource}
            onDelete={handleDeleteSource}
            onSync={handleSyncSource}
            syncing={syncingSource}
          />
        )}
      </main>

      <AddProjectModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onAdd={handleAddProject}
      />
    </div>
  );
}

export default App;
