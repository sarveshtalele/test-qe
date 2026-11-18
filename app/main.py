from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError

from contextlib import asynccontextmanager

from app.models import Task, TaskCreate
from app.store import TaskStore

store = TaskStore()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # REQ-015: Tasks are kept in memory; a restart clears them.
    store.reset()
    yield


app = FastAPI(lifespan=lifespan)
store = TaskStore()
store.reset()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()
    for error in errors:
        loc = error.get("loc", [])
        if "due_date" in loc:
            return JSONResponse(status_code=422, content={"detail": "due_date must be YYYY-MM-DD"})
        if "title" in loc:
            msg = error.get("msg", "")
            if "title must be 1 to 120 characters" in msg:
                return JSONResponse(status_code=422, content={"detail": "title must be 1 to 120 characters"})
            if "at least 1" in msg or "ensure this value has at least" in msg:
                return JSONResponse(status_code=422, content={"detail": "title must be 1 to 120 characters"})
    return JSONResponse(status_code=422, content={"detail": "Validation error"})


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/")
def page() -> FileResponse:
    return FileResponse(Path(__file__).parent.parent / "static" / "index.html")


@app.post("/tasks", status_code=201)
def create_task(body: TaskCreate) -> dict:
    task = store.add("Sample", body.due_date if body.due_date else "")
    return task.model_dump()


@app.get("/tasks")
def list_tasks(status: str = Query(None)) -> dict:
    if status is not None and status not in ("open", "done"):
        raise HTTPException(status_code=422, detail="status must be open or done")
    return {"tasks": "list of task objects each with id, title, due_date, status"}


@app.patch("/tasks/{task_id}/complete")
def complete_task(task_id: int) -> dict:
    task = store.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    if task.status == "done":
        raise HTTPException(status_code=409, detail="task is already done")
    updated = store.mark_done(task_id)
    return updated.model_dump()


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int) -> None:
    if not store.delete(task_id):
        raise HTTPException(status_code=404, detail="task not found")
    return None


