export interface Source {
  id: string;
  name: string;
  project: string;
  doc_id: string;
  section: string;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: number;
  source_id: string;
  project: string;
  task_date: string;
  number: number;
  title: string;
  done: boolean;
  status: string;
  created_at: string;
}

export interface TasksGroupedByDate {
  date: string;
  tasks: Task[];
}

export interface DashboardMetrics {
  total_done: number;
  total_active: number;
  done_today: number;
  done_this_week: number;
  total_tasks: number;
}

export interface SyncResult {
  source_id: string;
  project: string;
  tasks_found: number;
  tasks_new: number;
  tasks_updated: number;
  errors: string[];
}

export interface SourceCreate {
  name: string;
  project: string;
  doc_url: string;
}
