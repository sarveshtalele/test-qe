from pydantic import BaseModel, field_validator
from typing import Optional


class TaskCreate(BaseModel):
    title: str
    due_date: Optional[str] = None

    @field_validator("title")
    @classmethod
    def trim_title(cls, v: str) -> str:
        return v.strip()


class Task(BaseModel):
    id: int
    title: str
    due_date: Optional[str] = None
    status: str = "open"
