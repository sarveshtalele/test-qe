import enum
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class TaskStatus(str, enum.Enum):
    open = "open"
    done = "done"


class TaskCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    due_date: Optional[str] = None

    @field_validator("title")
    @classmethod
    def trim_title(cls, v: str) -> str:
        return v.strip()

    @field_validator("title")
    @classmethod
    def title_length_after_trim(cls, v: str) -> str:
        trimmed = v.strip()
        if not (1 <= len(trimmed) <= 120):
            raise ValueError("title must be 1 to 120 characters")
        return trimmed

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            date.fromisoformat(v)
        except (ValueError, TypeError):
            raise ValueError("due_date must be YYYY-MM-DD")
        return v


class TaskResponse(BaseModel):
    id: int
    title: str
    due_date: Optional[date] = None
    status: TaskStatus
    created_at: datetime
