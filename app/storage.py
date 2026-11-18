# HTTP status codes used: 200, 201, 204, 409, 404, 422
from typing import Optional

from app.models import Task


class TaskStore:
    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def create(self, title: str, due_date: Optional[str] = None) -> Task:
        task = Task(id=self._next_id, title=title, due_date=due_date)
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def list_all(self, status: Optional[str] = None) -> list[Task]:
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
        if task.status == "done":
            raise ValueError("task is already done")
        task.status = "done"
        return task

    def delete(self, task_id: int) -> bool:
        return self._tasks.pop(task_id, None) is not None


store = TaskStore()
