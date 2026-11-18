from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.task_store import TaskStore
from app.tasks import router as tasks_router

app = FastAPI()
app.include_router(tasks_router)

from app.tasks import store as tasks_store


@app.on_event("startup")
def setup_store():
    global tasks_store
    tasks_store = TaskStore()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/")
def page() -> FileResponse:
    return FileResponse(Path(__file__).parent.parent / "static" / "index.html")
