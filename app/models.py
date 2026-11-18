from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class TaskCreate(BaseModel):
    title: str
    due_date: Optional[str] = None

    @field_validator("title")
    @classmethod
    def trim_and_validate_title(cls, v: str) -> str:
        stripped = v.strip()
        if len(stripped) < 1 or len(stripped) > 120:
            raise ValueError("title must be 1 to 120 characters")
        return stripped

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("due_date must be YYYY-MM-DD")
        return v


class Task(BaseModel):
    id: int
    title: str
    due_date: Optional[str] = None
    status: str = "open"
    created_at: datetime = Field(default_factory=datetime.now)


class TaskResponse(BaseModel):
    id: int
    title: str
    due_date: Optional[str] = None
    status: str
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def from_task_model(cls, data):
        if isinstance(data, Task):
            return {
                "id": data.id,
                "title": data.title,
                "due_date": str(data.due_date) if data.due_date else None,
                "status": data.status,
                "created_at": data.created_at,
            }
        return data
