from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.router import router

app = FastAPI()
app.include_router(router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/")
def page() -> FileResponse:
    return FileResponse(Path(__file__).parent.parent / "static" / "index.html")
