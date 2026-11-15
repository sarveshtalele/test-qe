import uuid
from datetime import datetime, date

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter()


class TaskIn(BaseModel):
    title: str
    due_date: date | None = None


class Task(BaseModel):
    id: str
    title: str
    due_date: date | None = None
    status: str = "open"
    created_at: datetime


_tasks: list[Task] = []


@router.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(body: TaskIn) -> Task:
    task = Task(
        id=str(uuid.uuid4()),
        title=body.title,
        due_date=body.due_date,
        created_at=datetime.utcnow(),
    )
    _tasks.append(task)
    return task


@router.get("/tasks")
def list_tasks() -> list[Task]:
    return sorted(_tasks, key=lambda t: t.created_at, reverse=True)


@router.patch("/tasks/{task_id}/complete")
def complete_task(task_id: str) -> Task:
    for t in _tasks:
        if t.id == task_id:
            if t.status == "done":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="task is already done",
                )
            t.status = "done"
            return t
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="task not found"
    )


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str) -> None:
    for i, t in enumerate(_tasks):
        if t.id == task_id:
            _tasks.pop(i)
            return
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="task not found"
    )
