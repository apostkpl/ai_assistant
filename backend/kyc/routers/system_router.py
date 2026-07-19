import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from kyc.config.settings import settings
from kyc.core.dependencies import get_db

logger = logging.getLogger(__name__)
router = APIRouter(tags=["System"])

@router.get("/health", status_code=status.HTTP_200_OK)
def health_check(db: Session = Depends(get_db)):
    """
    Lightweight diagnostic endpoint verifying application status,
    active database connectivity, and current code version.
    """
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
        logger.debug("Health check database query succeeded.")
    except Exception as e:
        logger.error(f"Health check database failure: {e}", exc_info=True)
        db_status = "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "version": settings.app.version,
        "database": db_status
    }