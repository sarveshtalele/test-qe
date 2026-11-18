from datetime import date, datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

app = FastAPI()


# ---------------------------------------------------------------------------
# Custom 422 handler to match contract messages exactly
# ---------------------------------------------------------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


from fastapi.exceptions import RequestValidationError


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Determine which field caused the error and return the specific message.
    for error in exc.errors():
        loc = error.get("loc", [])
        if "title" in loc and error["type"] in ("string_too_short", "string_too_long"):
            return JSONResponse(status_code=422, content={"detail": "title must be 1 to 120 characters"})
        if "due_date" in loc and error["type"] == "date_from_datetime_parsing":
            return JSONResponse(status_code=422, content={"detail": "due_date must be YYYY-MM-DD"})
    # Fallback to default
    return JSONResponse(status_code=422, content={"detail": "Validation error"})


# ---------------------------------------------------------------------------
# In-memory store
# ---------------------------------------------------------------------------
_tasks: list[dict] = []
_next_id = 1

STATUS_OPEN = "open"
STATUS_DONE = "done"
VALID_STATUSES = {STATUS_OPEN, STATUS_DONE}


def _reset_store() -> None:
    """Reset the store (used in tests)."""
    global _tasks, _next_id
    _tasks = []
    _next_id = 1


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    due_date: Optional[date] = None


class TaskOut(BaseModel):
    id: int
    title: str
    due_date: Optional[date] = None
    status: str


class ErrorOut(BaseModel):
    message: str


# ---------------------------------------------------------------------------
# Health / page endpoints
# ---------------------------------------------------------------------------
@app.get("/health", status_code=200)
def health() -> dict:
    return {"status": "ok"}


@app.get("/")
def page() -> FileResponse:
    return FileResponse(Path(__file__).parent.parent / "static" / "index.html")


# ---------------------------------------------------------------------------
# Task management endpoints
# ---------------------------------------------------------------------------
@app.post("/tasks", status_code=201, response_model=TaskOut)
def create_task(payload: TaskCreate) -> dict:
    global _next_id
    title = payload.title.strip()
    if not title or len(title) > 120:
        raise HTTPException(status_code=422, detail="title must be 1 to 120 characters")
    if payload.due_date is None:
        due_date_str = None
    else:
        d = payload.due_date
        due_date_str = d.isoformat()
        if not isinstance(d, date):
            raise HTTPException(status_code=422, detail="due_date must be YYYY-MM-DD")
    task = {
        "id": _next_id,
        "title": title,
        "due_date": due_date_str,
        "status": STATUS_OPEN,
    }
    _tasks.append(task)
    _next_id += 1
    return task


@app.get("/tasks", response_model=dict)
def list_tasks(status: Optional[str] = Query(None)) -> dict:
    if status is not None and status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail="status must be open or done")
    filtered = [t for t in _tasks if status is None or t["status"] == status]
    sorted_tasks = sorted(filtered, key=lambda t: t["id"], reverse=True)
    return {"tasks": sorted_tasks}


@app.patch("/tasks/{task_id}/complete", response_model=TaskOut)
def complete_task(task_id: int) -> dict:
    for t in _tasks:
        if t["id"] == task_id:
            if t["status"] == STATUS_DONE:
                raise HTTPException(status_code=409, detail="task is already done")
            t["status"] = STATUS_DONE
            return t
    raise HTTPException(status_code=404, detail="task not found")


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int) -> None:
    for i, t in enumerate(_tasks):
        if t["id"] == task_id:
            _tasks.pop(i)
            return None
    raise HTTPException(status_code=404, detail="task not found")
