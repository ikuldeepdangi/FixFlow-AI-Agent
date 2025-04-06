# api/routes.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
async def health_check():
    return {"status": "FixFlow backend is alive!"}
