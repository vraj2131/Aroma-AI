from fastapi import APIRouter

from app.api.api_v1.endpoints import login, profile

api_router = APIRouter()
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])

