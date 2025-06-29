from fastapi import APIRouter

router = APIRouter(
    prefix="/utils",
    tags=["utils"],
)


@router.get("/health-check")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
