from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

router = APIRouter()

# In‑memory storage
_tasks_db: list = []
_next_id: int = 1


class TaskCreate(BaseModel):
    title: str
    due_date: Optional[date] = None


class Task(BaseModel):
    id: int
    title: str
    due_date: Optional[date] = None
    status: str = "open"


@router.get("/tasks")
def list_tasks(status: Optional[str] = Query(None)):
    if status is not None and status not in ("open", "done"):
        raise HTTPException(
            status_code=422,
            detail="status must be open or done",
        )
    tasks = sorted(_tasks_db, key=lambda t: t["id"], reverse=True)
    if status is not None:
        tasks = [t for t in tasks if t["status"] == status]
    return tasks


@router.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(body: TaskCreate):
    global _next_id
    task = {
        "id": _next_id,
        "title": body.title,
        "due_date": body.due_date,
        "status": "open",
    }
    _tasks_db.append(task)
    _next_id += 1
    return task


@router.patch("/tasks/{task_id}/complete")
def complete_task(task_id: int):
    for task in _tasks_db:
        if task["id"] == task_id:
            if task["status"] == "done":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="task is already done",
                )
            task["status"] = "done"
            return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="task not found",
    )


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    for i, task in enumerate(_tasks_db):
        if task["id"] == task_id:
            _tasks_db.pop(i)
            return
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="task not found",
    )
