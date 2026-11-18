from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models import Task, TaskCreate
from app.store import TaskStore

router = APIRouter()
store = TaskStore()


@router.post("/tasks", response_model=Task, status_code=201)
def create_task(body: TaskCreate) -> Task:
    return store.create(body.title, body.due_date)


@router.get("/tasks", response_model=list[Task], status_code=200)
def list_tasks(status: str | None = None) -> list[Task]:
    if status is not None and status not in ("open", "done"):
        raise HTTPException(status_code=422, detail="status must be open or done")
    return store.list(status)


@router.put("/tasks/{task_id}/complete", response_model=Task, status_code=200)
def complete_task(task_id: int) -> Task:
    try:
        task = store.complete(task_id)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    return task


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int) -> None:
    if not store.delete(task_id):
        raise HTTPException(status_code=404, detail="task not found")
