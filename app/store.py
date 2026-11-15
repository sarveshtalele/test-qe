from __future__ import annotations

from typing import Optional

from app.models import Task, TaskStatus


class TaskStore:
    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def create(self, title: str, due_date: Optional[str]) -> Task:
        import datetime

        task = Task(
            id=self._next_id,
            title=title,
            due_date=due_date,
            status=TaskStatus.open,
            created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def list_all(self, status: Optional[TaskStatus] = None) -> list[Task]:
        tasks = list(self._tasks.values())
        if status is not None:
            tasks = [t for t in tasks if t.status == status]
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        return tasks

    def get(self, task_id: int) -> Optional[Task]:
        return self._tasks.get(task_id)

    def complete(self, task_id: int) -> Optional[Task]:
        task = self._tasks.get(task_id)
        if task is None:
            return None
        if task.status == TaskStatus.done:
            raise ValueError("task is already done")
        updated = task.model_copy(update={"status": TaskStatus.done})
        self._tasks[task_id] = updated
        return updated

    def delete(self, task_id: int) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False


store = TaskStore()
