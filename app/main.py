from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.routes import tasks, health

app = FastAPI()
app.include_router(tasks.router)
app.include_router(health.router)


@app.get("/")
def page() -> FileResponse:
    return FileResponse(Path(__file__).parent.parent / "static" / "index.html")


@app.get("/")
def page() -> FileResponse:
    return FileResponse(Path(__file__).parent.parent / "static" / "index.html")
