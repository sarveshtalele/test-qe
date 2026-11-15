from __future__ import annotations

import enum
from typing import Optional

from pydantic import BaseModel, Field


class TaskStatus(str, enum.Enum):
    open = "open"
    done = "done"


class TaskIn(BaseModel):
    title: str = Field(...)
    due_date: Optional[str] = None

    class Config:
        extra = "forbid"


class Task(BaseModel):
    id: int
    title: str
    due_date: Optional[str] = None
    status: TaskStatus = TaskStatus.open
    created_at: str  # ISO format
