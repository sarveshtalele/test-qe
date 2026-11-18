from typing import Optional

from fastapi import APIRouter, HTTPException

from app.database import db
from app.models import TaskCreateRequest, TaskResponse, TaskStatus

router = APIRouter()


@router.post("/tasks", status_code=201, response_model=TaskResponse)
def create_task(body: TaskCreateRequest):
    task = db.create_task(title=body.title, due_date_str=body.due_date)
    return task


@router.get("/tasks", response_model=list[TaskResponse])
def list_tasks(status: Optional[str] = None):
    if status is not None:
        valid_statuses = {s.value for s in TaskStatus}
        if status not in valid_statuses:
            raise HTTPException(status_code=422, detail="status must be open or done")
    tasks = db.list_tasks(status_filter=status)
    return tasks


@router.patch("/tasks/{task_id}/complete", response_model=TaskResponse)
def complete_task(task_id: int):
    try:
        task = db.complete_task(task_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="task not found")
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return task


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    try:
        db.delete_task(task_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="task not found")
