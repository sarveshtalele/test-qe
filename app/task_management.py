from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator

router = APIRouter()


# In-memory store for tasks (REQ-015). Keyed by integer id, monotonic.
_tasks: dict[int, dict] = {}
_next_id: int = 1


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

    @field_validator("due_date", mode="before")
    @classmethod
    def validate_due_date(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            try:
                date.fromisoformat(v)
            except ValueError as exc:
                raise ValueError("due_date must be YYYY-MM-DD") from exc
        return v


class TaskUpdateComplete(BaseModel):
    pass


@router.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(body: TaskCreate) -> dict:
    global _next_id
    task_id = _next_id
    _next_id += 1
    task = {
        "id": task_id,
        "title": body.title,
        "due_date": body.due_date,
        "status": "open",
    }
    _tasks[task_id] = task
    return task


@router.get("/tasks")
def list_tasks(status_filter: Optional[str] = Query(None, alias="status")) -> list[dict]:
    if status_filter is not None and status_filter not in ("open", "done"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="status must be open or done",
        )
    tasks = list(_tasks.values())
    if status_filter is not None:
        tasks = [t for t in tasks if t["status"] == status_filter]
    tasks.sort(key=lambda t: t["id"], reverse=True)
    return tasks


@router.patch("/tasks/{task_id}/complete")
def complete_task(task_id: int) -> dict:
    task = _tasks.get(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="task not found"
        )
    if task["status"] == "done":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="task is already done"
        )
    task["status"] = "done"
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> None:
    if task_id not in _tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="task not found"
        )
    del _tasks[task_id]
