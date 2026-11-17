from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models import Task, TaskCreate
from app.storage import add_task, all_tasks, delete_task, get_task, update_task

router = APIRouter()


@router.post("/tasks", status_code=201)
def create_task(body: TaskCreate) -> Task:
    task = Task(title=body.title, due_date=body.due_date)
    add_task(task)
    return task


@router.get("/tasks")
def list_tasks() -> list[Task]:
    return all_tasks()


@router.put("/tasks/{task_id}/done")
def mark_done(task_id: str) -> Task:
    task = get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    if task.status == "done":
        raise HTTPException(status_code=409, detail="task is already done")
    task.status = "done"
    update_task(task)
    return task


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task_route(task_id: str) -> None:
    task = get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    delete_task(task_id)
