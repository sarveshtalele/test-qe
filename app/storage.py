from __future__ import annotations

from app.models import Task

_tasks: dict[str, Task] = {}


def all_tasks() -> list[Task]:
    return sorted(_tasks.values(), key=lambda t: t.created_at, reverse=True)


def get_task(task_id: str) -> Task | None:
    return _tasks.get(task_id)


def add_task(task: Task) -> None:
    _tasks[task.id] = task


def update_task(task: Task) -> None:
    _tasks[task.id] = task


def delete_task(task_id: str) -> None:
    _tasks.pop(task_id, None)
