from fastapi import APIRouter

from app.api.api_v1.endpoints import login, profile, order, document, table, feedback, chat

api_router = APIRouter()
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(order.router, prefix="/order", tags=["order"])
api_router.include_router(document.router, prefix="/document", tags=["document"])
api_router.include_router(table.router, prefix="/table", tags=["table"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])



