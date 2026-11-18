from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.models import TaskCreate, TaskResponse
from app.storage import store

router = APIRouter()


@router.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(body: TaskCreate) -> TaskResponse:
    task = store.create(title=body.title, due_date=str(body.due_date) if body.due_date else None)
    return TaskResponse.model_validate(task)


@router.get("/tasks", response_model=list[TaskResponse])
def list_tasks(status: Optional[str] = Query(None)) -> list[TaskResponse]:
    if status is not None and status not in ("open", "done"):
        raise HTTPException(status_code=422, detail="status must be open or done")
    tasks = store.list_all(status=status)
    return [TaskResponse.model_validate(t) for t in tasks]


@router.patch("/tasks/{id}/complete", response_model=TaskResponse)
def complete_task(id: int) -> TaskResponse:
    try:
        task = store.complete(id)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    return TaskResponse.model_validate(task)


@router.delete("/tasks/{id}", status_code=204)
def delete_task(id: int) -> None:
    if not store.delete(id):
        raise HTTPException(status_code=404, detail="task not found")
