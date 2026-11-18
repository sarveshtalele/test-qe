from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.tasks import router as tasks_router

app = FastAPI()
app.include_router(tasks_router)


@app.get("/health")
def health() -> dict:
    # NFR-1: Returns HTTP 200 with {"status": "ok"}
    return {"status": "ok"}


@app.get("/")
def page() -> FileResponse:
    return FileResponse(Path(__file__).parent.parent / "static" / "index.html")
