from __future__ import annotations

from datetime import datetime
from typing import Optional

from app.models import Task, TaskIn


class TaskStore:
    def __init__(self) -> None:
        self._counter = 0
        self._tasks: dict[int, Task] = {}

    def create(self, data: TaskIn) -> Task:
        self._counter += 1
        task = Task(
            id=self._counter,
            title=data.title,
            due_date=data.due_date,
            status="open",
            created_at=datetime.utcnow(),
        )
        self._tasks[task.id] = task
        return task

    def list_all(self) -> list[Task]:
        return sorted(self._tasks.values(), key=lambda t: t.created_at, reverse=True)

    def get(self, task_id: int) -> Optional[Task]:
        return self._tasks.get(task_id)

    def complete(self, task_id: int) -> Optional[Task]:
        task = self._tasks.get(task_id)
        if task is None:
            return None
        if task.status == "done":
            raise AlreadyDoneError()
        task.status = "done"
        return task

    def delete(self, task_id: int) -> bool:
        return self._tasks.pop(task_id, None) is not None


class AlreadyDoneError(Exception):
    pass
