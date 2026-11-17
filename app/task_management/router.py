from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Response

from .models import Task, TaskStatus
from .store import store

router = APIRouter()


@router.post("/tasks", status_code=201)
def create_task(title: str, dueDate: Optional[str] = None) -> Task:
    trimmed = title.strip()
    if not trimmed or len(trimmed) > 120:
        raise HTTPException(
            status_code=422,
            detail="title must be 1 to 120 characters",
        )
    return store.create(trimmed, dueDate)


@router.get("/tasks")
def list_tasks() -> list[Task]:
    return store.list_all()


@router.patch("/tasks/{task_id}/complete")
def complete_task(task_id: int) -> Task:
    task = store.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    if task.status == TaskStatus.done:
        raise HTTPException(status_code=409, detail="task is already done")
    return store.complete(task_id)


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int) -> Response:
    task = store.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    store.delete(task_id)
    return Response(status_code=204)