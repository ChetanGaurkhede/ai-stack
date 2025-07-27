from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db, engine
from app.schemas import HealthCheck
from app.config import settings
import structlog

logger = structlog.get_logger()
router = APIRouter()


@router.get("/health", response_model=HealthCheck)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Check database connection
        db_status = "healthy"
        try:
            db.execute("SELECT 1")
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
            logger.error("Database health check failed", error=str(e))
        
        # Check ChromaDB
        chromadb_status = "healthy"
        try:
            from app.services.knowledge_base_service import KnowledgeBaseService
            kb_service = KnowledgeBaseService()
            # Try to access the collection
            _ = kb_service.collection
        except Exception as e:
            chromadb_status = f"unhealthy: {str(e)}"
            logger.error("ChromaDB health check failed", error=str(e))
        
        # Check Redis (if configured)
        redis_status = "healthy"
        try:
            import redis
            r = redis.from_url(settings.redis_url)
            r.ping()
        except Exception as e:
            redis_status = f"unhealthy: {str(e)}"
            logger.warning("Redis health check failed", error=str(e))
        
        return HealthCheck(
            status="healthy" if all(s == "healthy" for s in [db_status, chromadb_status]) else "degraded",
            timestamp=datetime.now(),
            version=settings.app_version,
            database=db_status,
            chromadb=chromadb_status,
            redis=redis_status
        )
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return HealthCheck(
            status="unhealthy",
            timestamp=datetime.now(),
            version=settings.app_version,
            database="unknown",
            chromadb="unknown",
            redis="unknown"
        )


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    return {"status": "ready", "timestamp": datetime.now()}


@router.get("/live")
async def liveness_check():
    """Liveness check endpoint"""
    return {"status": "alive", "timestamp": datetime.now()} 