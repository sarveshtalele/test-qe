from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


# In‑memory store
_tasks: list[dict] = []
_last_id = 0


class TaskCreate(BaseModel):
    title: str
    due_date: Optional[str] = None


class TaskOut(BaseModel):
    id: int
    title: str
    due_date: Optional[str] = None
    status: str


@router.post("/tasks", response_model=TaskOut, status_code=201)
def create_task(body: TaskCreate):
    global _last_id
    _last_id += 1
    task = {
        "id": _last_id,
        "title": body.title,
        "due_date": body.due_date,
        "status": "open",
    }
    _tasks.append(task)
    return task


@router.get("/tasks", response_model=list[TaskOut])
def list_tasks():
    return sorted(_tasks, key=lambda t: t["id"], reverse=True)


@router.patch("/tasks/{task_id}/complete", response_model=TaskOut)
def complete_task(task_id: int):
    for t in _tasks:
        if t["id"] == task_id:
            if t["status"] == "done":
                raise HTTPException(status_code=409, detail="task is already done")
            t["status"] = "done"
            return t
    raise HTTPException(status_code=404, detail="task not found")


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    for i, t in enumerate(_tasks):
        if t["id"] == task_id:
            del _tasks[i]
            return None
    raise HTTPException(status_code=404, detail="task not found")
