from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.models import TaskIn, TaskStatus
from app.store import store

router = APIRouter()


@router.post("/tasks", status_code=201)
def create_task(body: TaskIn) -> dict:
    trimmed = body.title.strip()
    if len(trimmed) < 1 or len(trimmed) > 120:
        raise HTTPException(
            status_code=422,
            detail="title must be 1 to 120 characters",
        )
    if body.due_date is not None:
        import datetime

        try:
            datetime.datetime.strptime(body.due_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="due_date must be YYYY-MM-DD",
            )
    task = store.create(title=trimmed, due_date=body.due_date)
    return task.model_dump()


@router.get("/tasks", status_code=200)
def list_tasks(status: Optional[str] = Query(None)) -> list[dict]:
    if status is not None:
        try:
            status_filter = TaskStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="status must be open or done",
            )
    else:
        status_filter = None
    tasks = store.list_all(status=status_filter)
    return [t.model_dump() for t in tasks]


@router.patch("/tasks/{task_id}/complete", status_code=200)
def complete_task(task_id: int) -> dict:
    try:
        task = store.complete(task_id)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    return task.model_dump()


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    if not store.delete(task_id):
        raise HTTPException(status_code=404, detail="task not found")
    return None
