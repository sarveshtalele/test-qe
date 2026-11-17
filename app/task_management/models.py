from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class TaskStatus(str, Enum):
    open = "open"
    done = "done"


class Task(BaseModel):
    id: int
    title: str
    dueDate: Optional[str] = None
    status: TaskStatus = TaskStatus.open
    createdAt: str = ""