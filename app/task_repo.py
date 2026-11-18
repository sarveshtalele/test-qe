from app.models import Task, TaskStatus


class TaskRepository:
    def __init__(self):
        self._tasks: dict[int, Task] = {}
        self._next_id = 1

    def create(self, title: str, due_date: str | None = None) -> Task:
        task = Task(id=self._next_id, title=title, due_date=due_date)
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def get(self, task_id: int) -> Task | None:
        return self._tasks.get(task_id)

    def list_all(self, status: TaskStatus | None = None) -> list[Task]:
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        tasks.sort(key=lambda t: t.id, reverse=True)
        return tasks

    def update_status(self, task_id: int, status: TaskStatus) -> Task | None:
        task = self._tasks.get(task_id)
        if not task:
            return None
        task.status = status
        return task

    def delete(self, task_id: int) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False
