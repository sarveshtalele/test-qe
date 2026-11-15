from fastapi import APIRouter, HTTPException, status
from app.models import Task, TaskCreate

router = APIRouter()

_tasks: list[Task] = []
_next_id = 1


from typing_extensions import Annotated
from fastapi import APIRouter, HTTPException, Query, status
from app.models import Task, TaskCreate

router = APIRouter()

_tasks: list[Task] = []
_next_id = 1


@router.get("/tasks")
def list_tasks(status: Annotated[str | None, Query()] = None) -> list[Task]:
    if status is not None and status not in ("open", "done"):
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["query", "status"], "msg": "status must be open or done", "type": "value_error"}]
        )
    tasks = [t for t in _tasks if status is None or t.status == status]
    tasks.sort(key=lambda t: t.id, reverse=True)
    return tasks


@router.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> Task:
    global _next_id
    title = payload.title.strip()
    if len(title) < 1 or len(title) > 120:
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["body", "title"], "msg": "title must be 1 to 120 characters", "type": "value_error"}]
        )
    if payload.due_date is not None:
        import re
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", payload.due_date):
            raise HTTPException(
                status_code=422,
                detail=[{"loc": ["body", "due_date"], "msg": "due_date must be YYYY-MM-DD", "type": "value_error"}]
            )
    task = Task(
        id=_next_id,
        title=title,
        due_date=payload.due_date,
        status="open",
    )
    _tasks.append(task)
    _next_id += 1
    return task
