from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=120, examples=["Buy milk"])
    due_date: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("title must be 1 to 120 characters")
        return stripped

    @field_validator("due_date")
    @classmethod
    def due_date_format(cls, v: str | None) -> str | None:
        if v is None:
            return v
        import re
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("due_date must be YYYY-MM-DD")
        return v


class TaskOut(BaseModel):
    id: int
    title: str
    due_date: str | None = None
    status: str = "open"
    created_at: datetime


class TaskCompleteOut(BaseModel):
    id: int
    title: str
    due_date: str | None = None
    status: str = "done"
    created_at: datetime


class ErrorMessage(BaseModel):
    detail: str
