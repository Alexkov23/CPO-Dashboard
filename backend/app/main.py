from contextlib import asynccontextmanager
from datetime import date, timedelta

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.google_auth import (
    create_auth_flow,
    exchange_code,
    get_client_config,
    is_authenticated,
    save_client_config,
)
from app.google_docs import fetch_doc_text
from app.models import Source, Task
from app.parser import parse_doc_url, parse_tasks_text
from app.schemas import (
    DashboardMetrics,
    SourceCreate,
    SourceResponse,
    SourceToggle,
    SyncResult,
    TaskResponse,
    TasksGroupedByDate,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="CPO Dashboard API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Sources ----------


@app.get("/api/sources", response_model=list[SourceResponse])
def list_sources(db: Session = Depends(get_db)):
    return db.query(Source).order_by(Source.created_at.desc()).all()


@app.post("/api/sources", response_model=SourceResponse, status_code=201)
def create_source(payload: SourceCreate, db: Session = Depends(get_db)):
    try:
        doc_id, section = parse_doc_url(payload.doc_url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    source = Source(
        name=payload.name,
        project=payload.project,
        doc_id=doc_id,
        section=section,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@app.patch("/api/sources/{source_id}", response_model=SourceResponse)
def toggle_source(source_id: str, payload: SourceToggle, db: Session = Depends(get_db)):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    source.enabled = payload.enabled
    db.commit()
    db.refresh(source)
    return source


@app.delete("/api/sources/{source_id}", status_code=204)
def delete_source(source_id: str, db: Session = Depends(get_db)):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    db.delete(source)
    db.commit()


# ---------- Sync ----------


@app.post("/api/sync", response_model=list[SyncResult])
async def sync_all(db: Session = Depends(get_db)):
    sources = db.query(Source).filter(Source.enabled.is_(True)).all()
    results: list[SyncResult] = []

    for source in sources:
        result = await _sync_source(source, db)
        results.append(result)

    return results


@app.post("/api/sync/{source_id}", response_model=SyncResult)
async def sync_source(source_id: str, db: Session = Depends(get_db)):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return await _sync_source(source, db)


async def _sync_source(source: Source, db: Session) -> SyncResult:
    errors: list[str] = []

    try:
        text = await fetch_doc_text(source.doc_id, source.section)
    except Exception as exc:
        return SyncResult(
            source_id=source.id,
            project=source.project,
            tasks_found=0,
            tasks_new=0,
            tasks_updated=0,
            errors=[f"Failed to fetch doc: {exc}"],
        )

    parsed = parse_tasks_text(text)

    db.query(Task).filter(Task.source_id == source.id).delete()

    for pt in parsed:
        task = Task(
            source_id=source.id,
            project=source.project,
            task_date=pt.task_date,
            number=pt.number,
            title=pt.title,
            done=pt.done,
            status=pt.status,
        )
        db.add(task)

    db.commit()

    return SyncResult(
        source_id=source.id,
        project=source.project,
        tasks_found=len(parsed),
        tasks_new=len(parsed),
        tasks_updated=0,
        errors=errors,
    )


# ---------- Tasks ----------


@app.get("/api/tasks", response_model=list[TasksGroupedByDate])
def list_tasks(
    project: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Task)
    if project:
        query = query.filter(Task.project == project)

    tasks = query.order_by(Task.task_date.desc(), Task.number.asc()).all()

    grouped: dict[date, list[TaskResponse]] = {}
    for t in tasks:
        task_resp = TaskResponse.model_validate(t)
        grouped.setdefault(t.task_date, []).append(task_resp)

    return [
        TasksGroupedByDate(date=d, tasks=task_list)
        for d, task_list in sorted(grouped.items(), key=lambda x: x[0], reverse=True)
    ]


@app.get("/api/projects", response_model=list[str])
def list_projects(db: Session = Depends(get_db)):
    rows = db.query(Source.project).distinct().all()
    return [r[0] for r in rows]


# ---------- Metrics ----------


@app.get("/api/metrics", response_model=DashboardMetrics)
def get_metrics(
    project: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Task)
    if project:
        query = query.filter(Task.project == project)

    total_done = query.filter(Task.done.is_(True)).count()
    total_active = query.filter(Task.done.is_(False)).count()

    today = date.today()
    week_ago = today - timedelta(days=7)

    done_today = query.filter(Task.done.is_(True), Task.task_date == today).count()
    done_this_week = query.filter(Task.done.is_(True), Task.task_date >= week_ago).count()

    total_tasks = query.count()

    return DashboardMetrics(
        total_done=total_done,
        total_active=total_active,
        done_today=done_today,
        done_this_week=done_this_week,
        total_tasks=total_tasks,
    )


# ---------- Google Auth ----------


@app.get("/api/auth/status")
def auth_status():
    return {
        "authenticated": is_authenticated(),
        "has_client_config": get_client_config() is not None,
    }


@app.post("/api/auth/client-config")
async def upload_client_config(request: Request):
    body = await request.json()
    config = body.get("config")
    if not config:
        raise HTTPException(status_code=400, detail="Missing config")
    save_client_config(config)
    return {"status": "saved"}


def _get_redirect_uri(request: Request) -> str:
    uri = str(request.url_for("google_auth_callback"))
    if uri.startswith("http://") and "localhost" not in uri:
        uri = "https://" + uri[len("http://"):]
    return uri


@app.get("/api/auth/google")
def google_auth_redirect(request: Request):
    redirect_uri = _get_redirect_uri(request)
    result = create_auth_flow(redirect_uri)
    if not result:
        raise HTTPException(
            status_code=400,
            detail="Google client config not found. Upload it first.",
        )
    _, authorization_url = result
    return RedirectResponse(authorization_url)


@app.get("/api/auth/google/callback")
def google_auth_callback(code: str, request: Request):
    redirect_uri = _get_redirect_uri(request)
    creds = exchange_code(code, redirect_uri)
    if not creds:
        raise HTTPException(status_code=400, detail="Failed to exchange code")
    frontend_url = request.headers.get("referer", "/")
    if frontend_url == "/":
        frontend_url = "https://dist-remdpcvf.devinapps.com"
    return RedirectResponse(frontend_url)


# ---------- Health ----------


@app.get("/api/health")
def health():
    return {"status": "ok"}
