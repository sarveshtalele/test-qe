from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from .models import Task, TaskStatus


class InMemoryTaskStore:
    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def create(self, title: str, dueDate: Optional[str] = None) -> Task:
        now = datetime.now(timezone.utc).isoformat()
        task = Task(
            id=self._next_id,
            title=title,
            dueDate=dueDate,
            status=TaskStatus.open,
            createdAt=now,
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def list_all(self) -> list[Task]:
        tasks = list(self._tasks.values())
        tasks.sort(key=lambda t: t.createdAt, reverse=True)
        return tasks

    def get(self, task_id: int) -> Optional[Task]:
        return self._tasks.get(task_id)

    def complete(self, task_id: int) -> Task:
        task = self._tasks[task_id]
        task.status = TaskStatus.done
        return task

    def delete(self, task_id: int) -> None:
        del self._tasks[task_id]


store = InMemoryTaskStore()