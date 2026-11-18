from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> JSONResponse:
    return JSONResponse(content={"status": "ok"}, status_code=200)
