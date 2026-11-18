from datetime import date, datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

from app.store import tasks_db, next_id

tasks_router = APIRouter()


class TaskCreate(BaseModel):
    title: str = Field(...)
    due_date: Optional[str] = None


class TaskOut(BaseModel):
    id: int
    title: str
    due_date: Optional[str] = None
    status: str
    created_at: str


@tasks_router.post("/tasks", status_code=201)
def create_task(task_in: TaskCreate) -> TaskOut:
    title = task_in.title.strip()
    if len(title) < 1 or len(title) > 120:
        raise HTTPException(status_code=422, detail="title must be 1 to 120 characters")

    due_date = task_in.due_date
    if due_date is not None:
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=422, detail="due_date must be YYYY-MM-DD")

    task_id = next_id()
    now = datetime.now(timezone.utc).isoformat()
    tasks_db[task_id] = {
        "id": task_id,
        "title": title,
        "due_date": due_date,
        "status": "open",
        "created_at": now,
    }
    return TaskOut(**tasks_db[task_id])


@tasks_router.get("/tasks")
def list_tasks(
    status: Optional[str] = Query(None)
) -> list[TaskOut]:
    if status is not None and status not in ("open", "done"):
        raise HTTPException(status_code=422, detail="status must be open or done")

    tasks = list(tasks_db.values())
    if status:
        tasks = [t for t in tasks if t["status"] == status]
    tasks.sort(key=lambda t: t["id"], reverse=True)  # newest first
    return [TaskOut(**t) for t in tasks]


@tasks_router.put("/tasks/{task_id}/done", status_code=200)
def mark_task_done(task_id: int) -> TaskOut:
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="task not found")
    task = tasks_db[task_id]
    if task["status"] == "done":
        raise HTTPException(status_code=409, detail="task is already done")
    task["status"] = "done"
    return TaskOut(**task)


@tasks_router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int) -> None:
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="task not found")
    del tasks_db[task_id]
    return None
