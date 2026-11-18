from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.routers import tasks
from app.routers.health import router as health_router

app = FastAPI()

app.include_router(tasks.router)
app.include_router(health_router)


@app.get("/")
def page() -> FileResponse:
    return FileResponse(Path(__file__).parent.parent / "static" / "index.html")
