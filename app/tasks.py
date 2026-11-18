from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.task_store import Task, TaskIn

router = APIRouter()
store = None  # initialized in app setup


@router.post("/tasks", status_code=201)
def create_task(body: TaskIn) -> Task:
    task = store.create(body)
    return task


@router.get("/tasks")
def list_tasks(status: Optional[str] = Query(None)) -> list[Task]:
    if status is not None and status not in ("open", "done"):
        raise HTTPException(status_code=422, detail="status must be open or done")
    return store.list_tasks(status)


@router.patch("/tasks/{id}/complete")
def complete_task(id: int) -> Task:
    try:
        task = store.complete(id)
    except ValueError as e:
        msg = str(e)
        if msg == "task not found":
            raise HTTPException(status_code=404, detail="task not found")
        raise HTTPException(status_code=409, detail="task is already done")
    return task


@router.delete("/tasks/{id}", status_code=204)
def delete_task(id: int) -> None:
    ok = store.delete(id)
    if not ok:
        raise HTTPException(status_code=404, detail="task not found")
