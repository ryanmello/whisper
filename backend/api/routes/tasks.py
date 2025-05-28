"""
Task management endpoints.
"""

import os
from fastapi import APIRouter, HTTPException

from models.api_models import AnalysisRequest, AnalysisResponse, TaskStatus, ActiveConnectionsInfo
from core.app import get_analysis_service
from config.settings import settings

router = APIRouter()

@router.post("/tasks/", response_model=AnalysisResponse)
async def create_analysis_task(request: AnalysisRequest):
    """Create a new repository analysis task."""
    analysis_service = get_analysis_service()
    if analysis_service is None:
        raise HTTPException(status_code=503, detail="Analysis service not available")
    
    task_id = await analysis_service.create_task(
        repository_url=request.repository_url,
        task_type=request.task_type
    )
    
    # Construct WebSocket URL
    websocket_url = f"ws://{settings.HOST}:{settings.PORT}/ws/tasks/{task_id}"
    
    return AnalysisResponse(
        task_id=task_id,
        status="created",
        message=f"Analysis task created for {request.repository_url}",
        websocket_url=websocket_url
    )

@router.get("/tasks/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Get the status of a specific task."""
    analysis_service = get_analysis_service()
    if analysis_service is None:
        raise HTTPException(status_code=503, detail="Analysis service not available")
    
    status_info = analysis_service.get_task_status(task_id)
    return TaskStatus(**status_info)

@router.get("/active-connections", response_model=ActiveConnectionsInfo)
async def get_active_connections():
    """Get information about active WebSocket connections."""
    analysis_service = get_analysis_service()
    if analysis_service is None:
        raise HTTPException(status_code=503, detail="Analysis service not available")
    
    connections_info = analysis_service.get_active_connections_info()
    return ActiveConnectionsInfo(**connections_info) 