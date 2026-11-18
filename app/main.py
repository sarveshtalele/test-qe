from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, field_validator

app = FastAPI()

# In-memory storage
tasks_db: dict[int, dict] = {}
next_id: int = 1


class TaskCreate(BaseModel):
    title: str
    due_date: str | None = None

    @field_validator("title")
    @classmethod
    def title_length(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped or len(stripped) > 120:
            raise ValueError("title must be 1 to 120 characters")
        return stripped

    @field_validator("due_date")
    @classmethod
    def due_date_format(cls, v: str | None) -> str | None:
        if v is not None:
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("due_date must be YYYY-MM-DD")
        return v


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/")
def page() -> FileResponse:
    return FileResponse(Path(__file__).parent.parent / "static" / "index.html")


@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    global next_id
    new_task = {
        "id": next_id,
        "title": task.title,
        "due_date": task.due_date,
        "status": "open",
    }
    tasks_db[next_id] = new_task
    next_id += 1
    return new_task


@app.get("/tasks", status_code=200)
def list_tasks(status: str | None = Query(None)):
    if status is not None and status not in ("open", "done"):
        raise HTTPException(status_code=422, detail="status must be open or done")
    tasks = list(tasks_db.values())
    if status is not None:
        tasks = [t for t in tasks if t["status"] == status]
    tasks.sort(key=lambda t: t["id"], reverse=True)
    return {"tasks": tasks}


@app.patch("/tasks/{task_id}/complete", status_code=200)
def complete_task(task_id: int):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="task not found")
    task = tasks_db[task_id]
    if task["status"] == "done":
        raise HTTPException(status_code=409, detail="task is already done")
    task["status"] = "done"
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="task not found")
    del tasks_db[task_id]
    return None
