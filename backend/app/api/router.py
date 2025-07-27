from fastapi import APIRouter
from app.api.endpoints import workflows, documents, chat, health

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(health.router, tags=["health"]) 