from typing import Optional

from app.models import Task


class TaskStore:
    def __init__(self, reset_on_startup: bool = False) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1
        if reset_on_startup:
            self.reset()

    def add(self, title: str, due_date: str = "") -> Task:
        task = Task(id=self._next_id, title=title, due_date=due_date, status="open")
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def get(self, task_id: int) -> Optional[Task]:
        return self._tasks.get(task_id)

    def list_all(self, status: Optional[str] = None) -> list[dict]:
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        tasks.sort(key=lambda t: t.id, reverse=True)
        return [t.model_dump() for t in tasks]

    def mark_done(self, task_id: int) -> Optional[Task]:
        task = self._tasks.get(task_id)
        if task is None:
            return None
        if task.status == "done":
            return task  # caller checks status
        task.status = "done"
        return task

    def delete(self, task_id: int) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def reset(self) -> None:
        self._tasks.clear()
        self._next_id = 1
