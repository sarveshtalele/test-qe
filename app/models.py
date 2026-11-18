from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Task(BaseModel):
    id: int
    title: str
    due_date: str = ""
    status: str = "open"


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    due_date: Optional[str] = ""

    @field_validator("title")
    @classmethod
    def trim_title(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("title must be a string")
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("title must be 1 to 120 characters")
        if len(trimmed) > 120:
            raise ValueError("title must be 1 to 120 characters")
        return trimmed

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: Optional[str]) -> str:
        if v and v.strip():
            import re
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", v.strip()):
                raise ValueError("due_date must be YYYY-MM-DD")
            return v.strip()
        return ""


class TaskUpdateStatus(BaseModel):
    pass
