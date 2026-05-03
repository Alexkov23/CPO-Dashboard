from datetime import date, datetime

from pydantic import BaseModel, Field


class SourceCreate(BaseModel):
    name: str
    project: str
    doc_url: str


class SourceResponse(BaseModel):
    id: str
    name: str
    project: str
    doc_id: str
    section: str
    enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SourceToggle(BaseModel):
    enabled: bool


class TaskResponse(BaseModel):
    id: int
    source_id: str
    project: str
    task_date: date
    number: int
    title: str
    done: bool
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TasksGroupedByDate(BaseModel):
    date: date
    tasks: list[TaskResponse]


class DashboardMetrics(BaseModel):
    total_done: int = Field(description="Total completed tasks")
    total_active: int = Field(description="Total active tasks")
    done_today: int = Field(description="Tasks completed today")
    done_this_week: int = Field(description="Tasks completed in the last 7 days")
    total_tasks: int = Field(description="Grand total of all tasks")


class SyncResult(BaseModel):
    source_id: str
    project: str
    tasks_found: int
    tasks_new: int
    tasks_updated: int
    errors: list[str] = []
