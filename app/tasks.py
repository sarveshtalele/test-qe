from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models import Task, TaskIn
from app.storage import AlreadyDoneError, TaskStore

router = APIRouter()
store = TaskStore()


@router.post("/tasks", response_model=Task, status_code=200)
def create_task(data: TaskIn) -> Task:
    from fastapi import HTTPException
    if not data.title.strip():
        raise HTTPException(status_code=422, detail="Task title is required")
    return store.create(data)


@router.get("/tasks", response_model=list[Task])
def list_tasks() -> list[Task]:
    return store.list_all()


@router.patch("/tasks/{id}/complete", response_model=Task)
def complete_task(id: int) -> Task:
    try:
        task = store.complete(id)
    except AlreadyDoneError:
        raise HTTPException(status_code=409, detail="task is already done")
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    return task


@router.delete("/tasks/{id}", status_code=204)
def delete_task(id: int) -> None:
    if not store.delete(id):
        raise HTTPException(status_code=404, detail="task not found")
