from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.models import TaskResponse, TaskStatus


class InMemoryDatabase:
    def __init__(self):
        self._tasks: Dict[int, TaskResponse] = {}
        self._next_id = 1

    def create_task(self, title: str, due_date_str: Optional[str]) -> TaskResponse:
        task_id = self._next_id
        self._next_id += 1
        parsed_date = None
        if due_date_str is not None:
            from datetime import date
            parts = due_date_str.split("-")
            parsed_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
        task = TaskResponse(
            id=task_id,
            title=title,
            due_date=parsed_date,
            status=TaskStatus.open,
            created_at=datetime.now(timezone.utc),
        )
        self._tasks[task_id] = task
        return task

    def list_tasks(self, status_filter: Optional[str] = None) -> List[TaskResponse]:
        tasks = list(self._tasks.values())
        if status_filter is not None:
            tasks = [t for t in tasks if t.status.value == status_filter]
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        return tasks

    def get_task(self, task_id: int) -> Optional[TaskResponse]:
        return self._tasks.get(task_id)

    def complete_task(self, task_id: int) -> TaskResponse:
        task = self._tasks.get(task_id)
        if task is None:
            raise KeyError("task not found")
        if task.status == TaskStatus.done:
            raise ValueError("task is already done")
        completed_task = task.model_copy(update={"status": TaskStatus.done})
        self._tasks[task_id] = completed_task
        return completed_task

    def delete_task(self, task_id: int) -> None:
        if task_id not in self._tasks:
            raise KeyError("task not found")
        del self._tasks[task_id]


db = InMemoryDatabase()
