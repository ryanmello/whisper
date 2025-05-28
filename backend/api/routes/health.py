"""
Health check endpoints.
"""

from fastapi import APIRouter

from models.api_models import HealthCheck
from core.app import get_analysis_service, get_uptime

router = APIRouter()

@router.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Whisper API", "status": "running"}

@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint."""
    analysis_service = get_analysis_service()
    uptime = get_uptime()
    
    return HealthCheck(
        status="healthy",
        agent_ready=analysis_service is not None,
        uptime=uptime
    ) 