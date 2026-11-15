from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI()


# In-memory storage
_tasks: dict[str, "Task"] = {}


class Task(BaseModel):
    id: str
    title: str
    dueDate: Optional[str] = None
    status: str = "open"


class TaskCreate(BaseModel):
    title: str
    dueDate: Optional[str] = None


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/")
def page() -> FileResponse:
    return FileResponse(Path(__file__).parent.parent / "static" / "index.html")


@app.post("/tasks", status_code=201)
def create_task(body: TaskCreate) -> Task:
    task = Task(
        id=str(uuid4()),
        title=body.title,
        dueDate=body.dueDate,
        status="open",
    )
    _tasks[task.id] = task
    return task


@app.get("/tasks")
def list_tasks() -> list[Task]:
    return sorted(_tasks.values(), key=lambda t: t.id, reverse=True)


@app.patch("/tasks/{task_id}/complete")
def complete_task(task_id: str) -> Task:
    task = _tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    if task.status == "done":
        raise HTTPException(status_code=409, detail="task is already done")
    task.status = "done"
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: str) -> None:
    task = _tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    del _tasks[task_id]
