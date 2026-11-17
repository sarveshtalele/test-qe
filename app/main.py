from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from .task_management.router import router as tasks_router
from .health_monitoring.router import router as health_router

app = FastAPI()

app.include_router(tasks_router)
app.include_router(health_router)


@app.get("/")
def page() -> FileResponse:
    return FileResponse(Path(__file__).parent.parent / "static" / "index.html")
