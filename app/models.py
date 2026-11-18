from __future__ import annotations

from pydantic import BaseModel, Field, model_validator
from typing import Optional


class Task(BaseModel):
    id: int
    title: str
    due_date: str | None = None
    status: str = "open"


class TaskCreate(BaseModel):
    title: str
    due_date: str | None = None

    @model_validator(mode="after")
    def validate_title_and_due_date(self) -> "TaskCreate":
        title = self.title.strip() if self.title else ""
        if not 1 <= len(title) <= 120:
            raise ValueError("title must be 1 to 120 characters")
        if self.due_date is not None:
            from datetime import datetime
            try:
                datetime.strptime(self.due_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("due_date must be YYYY-MM-DD")
        self.title = title
        return self
