from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class TaskIn(BaseModel):
    title: str
    due_date: Optional[date] = None


class Task(TaskIn):
    id: int
    status: str = "open"
    created_at: datetime = Field(default_factory=datetime.utcnow)
