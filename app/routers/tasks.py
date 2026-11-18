from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.models import ErrorMessage, TaskIn, TaskOut
from app.store import store

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskOut, status_code=201)
def create_task(body: TaskIn) -> TaskOut:
    return store.create(body)


@router.get("", response_model=list[TaskOut])
def list_tasks(status: Optional[str] = Query(None)) -> list[TaskOut]:
    if status is not None and status not in ("open", "done"):
        raise HTTPException(status_code=422, detail="status must be open or done")
    return store.list_all(status=status)


@router.patch("/{task_id}/complete", response_model=TaskOut)
def complete_task(task_id: int) -> TaskOut:
    task = store.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    if task.status == "done":
        raise HTTPException(status_code=409, detail="task is already done")
    updated = store.mark_done(task_id)
    # mark_done returns None only when already done, which we already checked
    assert updated is not None
    return updated


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int) -> None:
    if not store.delete(task_id):
        raise HTTPException(status_code=404, detail="task not found")
