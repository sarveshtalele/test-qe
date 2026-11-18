from datetime import datetime, date

from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel, Field, field_validator

from app.store import tasks, next_id

router = APIRouter()


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    due_date: str | None = None

    @field_validator("title")
    @classmethod
    def trim_title(cls, v: str) -> str:
        return v.strip()

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("due_date must be YYYY-MM-DD")
        return v


class TaskOut(BaseModel):
    id: int
    title: str
    due_date: str | None = None
    status: str = "open"


@router.post("/tasks", status_code=201)
def create_task(body: TaskCreate) -> TaskOut:
    title_stripped = body.title.strip()
    if len(title_stripped) < 1 or len(title_stripped) > 120:
        raise HTTPException(status_code=422, detail="title must be 1 to 120 characters")
    if body.due_date is not None:
        try:
            datetime.strptime(body.due_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=422, detail="due_date must be YYYY-MM-DD")
    task_id = next_id()
    task = {
        "id": task_id,
        "title": title_stripped,
        "due_date": body.due_date,
        "status": "open",
    }
    tasks[task_id] = task
    return TaskOut(**task)


@router.get("/tasks")
def list_tasks(status: str | None = Query(None)) -> list[TaskOut]:
    if status is not None and status not in ("open", "done"):
        raise HTTPException(status_code=422, detail="status must be open or done")
    result = [t for t in tasks.values() if status is None or t["status"] == status]
    result.sort(key=lambda t: t["id"], reverse=True)
    return [TaskOut(**t) for t in result]


@router.patch("/tasks/{task_id}/complete")
def complete_task(task_id: int) -> TaskOut:
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    if task["status"] == "done":
        raise HTTPException(status_code=409, detail="task is already done")
    task["status"] = "done"
    return TaskOut(**task)


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int) -> Response:
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    del tasks[task_id]
    return Response(status_code=204)
