from fastapi import APIRouter

from .v1.router import router as v1_router # type: ignore

router = APIRouter(prefix="/channels/meta")

router.include_router(v1_router, prefix="/v1")