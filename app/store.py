from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from app.models import TaskIn, TaskOut


class TaskStore:
    def __init__(self) -> None:
        self._tasks: dict[int, TaskOut] = {}
        self._next_id: int = 1

    def create(self, data: TaskIn) -> TaskOut:
        task_id = self._next_id
        self._next_id += 1
        now = datetime.now(timezone.utc)
        task = TaskOut(
            id=task_id,
            title=data.title,
            due_date=data.due_date,
            status="open",
            created_at=now,
        )
        self._tasks[task_id] = task
        return task

    def list_all(self, status: Optional[str] = None) -> list[TaskOut]:
        tasks = list(self._tasks.values())
        if status is not None:
            tasks = [t for t in tasks if t.status == status]
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        return tasks

    def get(self, task_id: int) -> TaskOut | None:
        return self._tasks.get(task_id)

    def mark_done(self, task_id: int) -> TaskOut | None:
        task = self._tasks.get(task_id)
        if task is None:
            return None
        if task.status == "done":
            return None  # caller handles conflict
        updated = task.model_copy(update={"status": "done"})
        self._tasks[task_id] = updated
        return updated

    def delete(self, task_id: int) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def is_done(self, task_id: int) -> bool:
        task = self._tasks.get(task_id)
        if task is None:
            return False
        return task.status == "done"


store = TaskStore()
