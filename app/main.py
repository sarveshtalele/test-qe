from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.routers.tasks import router

app = FastAPI()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/")
def page() -> FileResponse:
    return FileResponse(Path(__file__).parent.parent / "static" / "index.html")


app.include_router(router, prefix="")

