# CPO Dashboard

Personal CPO Dashboard that automatically collects tasks from **Google Docs** and displays them in a clean dashboard interface.

## Architecture

- **Backend**: Python FastAPI + SQLite
- **Frontend**: React + TypeScript (Vite)

## Features

- Parse tasks from Google Docs (public/shared documents)
- Support multiple projects via Google Doc tabs
- Task grouping by date, color-coded status (done/active)
- Dashboard metrics (total, done today, done this week)
- Add projects via UI (auto-parse Google Doc URL)
- Sync tasks on demand

## Task Format in Google Docs

```
27.01.2026
1. + completed task
2. active task
3. multi-line task
   continuation
```

- Date line (DD.MM.YYYY) sets `task_date`
- Number prefix (e.g. "1.") sets task `number`
- "+" after number means done
- Remaining text is the `title`

## Setup

### Backend

```bash
cd backend
pip install -e .
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`, backend on `http://localhost:8000`.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/sources | List all sources |
| POST | /api/sources | Add a source (name, project, doc_url) |
| PATCH | /api/sources/:id | Toggle source enabled/disabled |
| DELETE | /api/sources/:id | Delete a source |
| POST | /api/sync | Sync all enabled sources |
| POST | /api/sync/:id | Sync a specific source |
| GET | /api/tasks | List tasks (optional ?project=) |
| GET | /api/projects | List distinct projects |
| GET | /api/metrics | Get dashboard metrics |
| GET | /api/health | Health check |
