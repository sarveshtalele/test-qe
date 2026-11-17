from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    due_date: date | None = None
    status: str = "open"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TaskCreate(BaseModel):
    title: str
    due_date: date | None = None
