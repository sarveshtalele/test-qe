from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.routers.health import router as health_router
from app.routers.tasks import router

app = FastAPI()


@app.get("/")
def page() -> FileResponse:
    return FileResponse(Path(__file__).parent.parent / "static" / "index.html")


app.include_router(health_router, prefix="")
app.include_router(router, prefix="")

