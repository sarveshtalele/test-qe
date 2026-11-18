from datetime import datetime
import re

from fastapi import APIRouter, HTTPException, Request

from app.models import TaskStatus

router = APIRouter()

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _repo(request: Request):
    return request.app.state.task_repo


def _validate_title(title: str) -> None:
    trimmed = title.strip()
    if len(trimmed) < 1 or len(trimmed) > 120:
        raise HTTPException(status_code=422, detail="title must be 1 to 120 characters")


def _validate_due_date(due_date: str | None) -> str | None:
    if due_date is None:
        return None
    trimmed = due_date.strip()
    if not DATE_PATTERN.match(trimmed):
        raise HTTPException(status_code=422, detail="due_date must be YYYY-MM-DD")
    # also check if it is a real date
    try:
        datetime.strptime(trimmed, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=422, detail="due_date must be YYYY-MM-DD")
    return trimmed


@router.post("/tasks", status_code=201)
def create_task(request: Request, body: dict):
    title = body.get("title", "")
    _validate_title(title)
    due_date = body.get("due_date")
    if due_date is not None:
        due_date = _validate_due_date(due_date)
    repo = _repo(request)
    task = repo.create(title=title.strip(), due_date=due_date)
    return task.to_dict()


@router.get("/tasks")
def list_tasks(request: Request, status: str | None = None):
    if status is not None:
        if status not in ("open", "done"):
            raise HTTPException(status_code=422, detail="status must be open or done")
    filter_status = TaskStatus(status) if status else None
    repo = _repo(request)
    tasks = repo.list_all(status=filter_status)
    return {"tasks": [t.to_dict() for t in tasks]}


@router.patch("/tasks/{task_id}/done")
def complete_task(request: Request, task_id: int):
    repo = _repo(request)
    task = repo.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    if task.status == TaskStatus.DONE:
        raise HTTPException(status_code=409, detail="task is already done")
    task = repo.update_status(task_id, TaskStatus.DONE)
    return {
        "id": task.id,
        "title": task.title,
        "status": task.status.value,
    }


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(request: Request, task_id: int):
    repo = _repo(request)
    if not repo.delete(task_id):
        raise HTTPException(status_code=404, detail="task not found")
    return None
