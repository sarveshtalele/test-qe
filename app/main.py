from datetime import date
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, field_validator

app = FastAPI()
# The endpoint /health returns HTTP 200 with {"status": "ok"}.

# in-memory task store
_tasks: list[dict] = []
_next_id = 1


def _get_task(task_id: int) -> dict:
    for t in _tasks:
        if t["id"] == task_id:
            return t
    raise HTTPException(status_code=404, detail="task not found")


# --- request models ---

class TaskCreateRequest(BaseModel):
    title: str
    due_date: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if not v or len(v) > 120:
            raise ValueError("title must be 1 to 120 characters")
        return v

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            try:
                date.fromisoformat(v)
            except (ValueError, TypeError):
                raise ValueError("due_date must be YYYY-MM-DD")
        return v


# --- endpoints ---

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/")
def page() -> FileResponse:
    return FileResponse(Path(__file__).parent.parent / "static" / "index.html")


@app.post("/tasks", status_code=201)
def create_task(body: TaskCreateRequest) -> dict:
    global _next_id
    task = {
        "id": _next_id,
        "title": body.title.strip(),
        "due_date": body.due_date,
        "status": "open",
    }
    _next_id += 1
    _tasks.insert(0, task)  # newest first by insert at front
    task["due_date"] = body.due_date
    return task


@app.get("/tasks")
def list_tasks(status: Optional[str] = Query(None)) -> list[dict]:
    if status is not None and status not in ("open", "done"):
        raise HTTPException(status_code=422, detail="status must be open or done")
    if status is None:
        # return all tasks, newest first (insert order already newest first)
        return list(_tasks)
    return [t for t in _tasks if t["status"] == status]


@app.put("/tasks/{task_id}/complete")
def complete_task(task_id: int) -> dict:
    task = _get_task(task_id)
    if task["status"] == "done":
        raise HTTPException(status_code=409, detail="task is already done")
    task["status"] = "done"
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int) -> None:
    task = _get_task(task_id)
    _tasks.remove(task)
    return None
