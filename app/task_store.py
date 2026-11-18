from __future__ import annotations

import re
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator


_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class TaskIn(BaseModel):
    title: str
    due_date: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if not v or len(v) > 120:
            raise ValueError("title must be 1 to 120 characters")
        return v

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not _DATE_RE.match(v):
                raise ValueError("due_date must be YYYY-MM-DD")
            # also validate it is a real date
            try:
                date.fromisoformat(v)
            except ValueError:
                raise ValueError("due_date must be YYYY-MM-DD")
        return v


class Task(BaseModel):
    id: int
    title: str
    due_date: Optional[str] = None
    status: str = "open"


class TaskStore:
    def __init__(self) -> None:
        self._tasks: list[Task] = []
        self._next_id = 1

    def create(self, data: TaskIn) -> Task:
        task = Task(
            id=self._next_id,
            title=data.title.strip(),
            due_date=data.due_date,
            status="open",
        )
        self._tasks.append(task)
        self._next_id += 1
        return task

    def list_tasks(self, status: Optional[str] = None) -> list[Task]:
        if status is not None:
            return [t for t in reversed(self._tasks) if t.status == status]
        return list(reversed(self._tasks))

    def complete(self, task_id: int) -> Task:
        task = self._find(task_id)
        if task is None:
            return None  # caller checks
        if task.status == "done":
            raise ValueError("task is already done")
        task.status = "done"
        return task

    def delete(self, task_id: int) -> bool:
        task = self._find(task_id)
        if task is None:
            return False
        self._tasks.remove(task)
        return True

    def _find(self, task_id: int) -> Optional[Task]:
        for t in self._tasks:
            if t.id == task_id:
                return t
        return None
