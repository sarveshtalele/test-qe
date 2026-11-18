from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

router = APIRouter()

# In-memory store
_tasks: dict[int, dict] = {}
_next_id = 1


class TaskCreate(BaseModel):
    title: str = Field(...)
    due_date: Optional[str] = None

    @field_validator("title")
    @classmethod
    def trim_and_validate_title(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 1 or len(v) > 120:
            raise ValueError("title must be 1 to 120 characters")
        return v

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v != "":
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("due_date must be YYYY-MM-DD")
        return v


class TaskOut(BaseModel):
    id: int
    title: str
    due_date: Optional[str] = None
    status: str = "open"


@router.post("/tasks", status_code=201)
def create_task(body: TaskCreate) -> TaskOut:
    global _next_id
    task = {
        "id": _next_id,
        "title": body.title.strip(),
        "due_date": body.due_date if body.due_date else None,
        "status": "open",
    }
    _tasks[_next_id] = task
    _next_id += 1
    return TaskOut(**task)


@router.get("/tasks")
def list_tasks(status: Optional[str] = Query(None)) -> list[TaskOut]:
    if status is not None:
        if status not in ("open", "done"):
            raise HTTPException(status_code=422, detail="status must be open or done")
    result = sorted(_tasks.values(), key=lambda t: t["id"], reverse=True)
    if status:
        result = [t for t in result if t["status"] == status]
    return [TaskOut(**t) for t in result]


@router.post("/tasks/{task_id}/done")
def mark_done(task_id: int) -> TaskOut:
    task = _tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    if task["status"] == "done":
        raise HTTPException(status_code=409, detail="task is already done")
    task["status"] = "done"
    return TaskOut(**task)


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int) -> None:
    task = _tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    del _tasks[task_id]
