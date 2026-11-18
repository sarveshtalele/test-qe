import enum


class TaskStatus(str, enum.Enum):
    OPEN = "open"
    DONE = "done"


class Task:
    def __init__(self, id: int, title: str, due_date: str | None = None):
        self.id = id
        self.title = title
        self.due_date = due_date
        self.status = TaskStatus.OPEN

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "due_date": self.due_date,
            "status": self.status.value,
        }
