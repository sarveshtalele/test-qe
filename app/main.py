import re
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, field_validator

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# ---------------------------------------------------------------------------
# In-memory store (REQ-015)
# ---------------------------------------------------------------------------

in_memory_tasks: dict[int, dict] = {}
_next_id: int = 1


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class CreateTask(BaseModel):
    title: str
    due_date: Optional[str] = None

    @field_validator("title")
    @classmethod
    def title_length(cls, v: str) -> str:
        stripped = v.strip()
        if len(stripped) < 1 or len(stripped) > 120:
            raise ValueError("title must be 1 to 120 characters")
        return stripped

    @field_validator("due_date")
    @classmethod
    def due_date_format(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            v = v.strip()
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
                raise ValueError("due_date must be YYYY-MM-DD")
            # Validate it is a real date
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("due_date must be YYYY-MM-DD")
            return v
        return None


# ---------------------------------------------------------------------------
# Routes: Health / API / Web UI
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/tasks", status_code=201)
def create_task(body: CreateTask):
    global _next_id
    task = {
        "id": _next_id,
        "title": body.title,
        "due_date": body.due_date,
        "status": "open",
    }
    in_memory_tasks[_next_id] = task
    _next_id += 1
    return task


@app.get("/tasks")
def list_tasks(status: Optional[str] = None):
    if status is not None and status not in ("open", "done"):
        raise HTTPException(status_code=422, detail="status must be open or done")
    tasks = list(in_memory_tasks.values())
    if status:
        tasks = [t for t in tasks if t["status"] == status]
    # Newest first (descending by id)
    tasks.sort(key=lambda t: t["id"], reverse=True)
    return {"tasks": tasks}


@app.patch("/tasks/{task_id}/complete")
def complete_task(task_id: int):
    task = in_memory_tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    if task["status"] == "done":
        raise HTTPException(status_code=409, detail="task is already done")
    task["status"] = "done"
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    task = in_memory_tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    del in_memory_tasks[task_id]


# ---------------------------------------------------------------------------
# Web UI (REQ-011, REQ-012, REQ-013)
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def index(request: Request, title_input: str = "", due_date_input: str = "", error: str = ""):
    tasks = list(in_memory_tasks.values())
    tasks.sort(key=lambda t: t["id"], reverse=True)
    return templates.TemplateResponse(
        "tasks.html",
        {
            "request": request,
            "tasks": tasks,
            "title_input": title_input,
            "due_date_input": due_date_input,
            "error": error,
        },
    )


@app.post("/", response_class=HTMLResponse)
def add_task(
    request: Request,
    title: str = Form(...),
    due_date: str = Form(default=""),
):
    # Build a CreateTask model manually to reuse validation
    data = {"title": title, "due_date": due_date if due_date.strip() else None}
    try:
        validated = CreateTask(**data)
    except Exception as exc:
        # Extract the first error message
        error_msg = "title must be 1 to 120 characters"  # fallback
        try:
            errors = exc.errors() if hasattr(exc, "errors") else []
            if errors:
                error_msg = errors[0]["msg"]
        except Exception:
            error_msg = str(exc)
        tasks = list(in_memory_tasks.values())
        tasks.sort(key=lambda t: t["id"], reverse=True)
        return templates.TemplateResponse(
            "tasks.html",
            {
                "request": request,
                "tasks": tasks,
                "title_input": title,
                "due_date_input": due_date,
                "error": error_msg,
            },
            status_code=200,
        )

    # Success: create the task
    global _next_id
    task = {
        "id": _next_id,
        "title": validated.title,
        "due_date": validated.due_date,
        "status": "open",
    }
    in_memory_tasks[_next_id] = task
    _next_id += 1

    tasks = list(in_memory_tasks.values())
    tasks.sort(key=lambda t: t["id"], reverse=True)
    return templates.TemplateResponse(
        "tasks.html",
        {
            "request": request,
            "tasks": tasks,
            "title_input": "",
            "due_date_input": "",
            "error": "",
        },
    )


@app.post("/tasks/{task_id}/done", response_class=HTMLResponse)
def done_task(request: Request, task_id: int):
    task = in_memory_tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    if task["status"] == "done":
        raise HTTPException(status_code=409, detail="task is already done")
    task["status"] = "done"
    # Redirect to the main page
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/", status_code=303)


@app.post("/tasks/{task_id}/delete", response_class=HTMLResponse)
def delete_task_web(request: Request, task_id: int):
    task = in_memory_tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    del in_memory_tasks[task_id]
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/", status_code=303)
