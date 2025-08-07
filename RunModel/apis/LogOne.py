# apis/loggen.py
from fastapi import APIRouter

loggen_router = APIRouter()

@loggen_router.get("/")
async def get_logs():
    return {"message": "Log system ready."}
