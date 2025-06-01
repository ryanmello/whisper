"""
Task management endpoints.
"""

import os
from fastapi import APIRouter, HTTPException

from models.api_models import (
    AnalysisRequest, AnalysisResponse, SmartAnalysisRequest, SmartAnalysisResponse,
    TaskStatus, ActiveConnectionsInfo, ToolRegistryInfo, IntentAnalysisRequest, AIAnalysis
)
from core.app import get_analysis_service
from services.openai_service import OpenAIService
from config.settings import settings

router = APIRouter()

@router.post("/analyze-intent", response_model=AIAnalysis)
async def analyze_intent(request: IntentAnalysisRequest):
    """Analyze user intent using OpenAI API."""
    openai_service = OpenAIService()
    
    try:
        analysis = await openai_service.analyze_intent(
            context=request.context,
            repository=request.repository,
            max_tokens=request.maxTokens or 200
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intent analysis failed: {str(e)}")

@router.post("/tasks/", response_model=AnalysisResponse)
async def create_analysis_task(request: AnalysisRequest):
    """Create a new repository analysis task (legacy endpoint)."""
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

@router.post("/smart-tasks/", response_model=SmartAnalysisResponse)
async def create_smart_analysis_task(request: SmartAnalysisRequest):
    """Create a new smart context-based analysis task."""
    analysis_service = get_analysis_service()
    if analysis_service is None:
        raise HTTPException(status_code=503, detail="Analysis service not available")
    
    task_id = await analysis_service.create_smart_task(
        repository_url=request.repository_url,
        context=request.context,
        intent=request.intent,
        target_languages=request.target_languages,
        scope=request.scope,
        depth=request.depth,
        additional_params=request.additional_params
    )
    
    # Construct WebSocket URL
    websocket_url = f"ws://{settings.HOST}:{settings.PORT}/ws/smart-tasks/{task_id}"
    
    return SmartAnalysisResponse(
        task_id=task_id,
        status="created",
        message=f"Smart analysis task created for {request.repository_url}",
        websocket_url=websocket_url,
        analysis_plan=None  # Will be populated during execution
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

@router.get("/tools", response_model=ToolRegistryInfo)
async def get_tool_registry_info():
    """Get information about available analysis tools."""
    analysis_service = get_analysis_service()
    if analysis_service is None:
        raise HTTPException(status_code=503, detail="Analysis service not available")
    
    try:
        registry_info = await analysis_service.get_tool_registry_info()
        return ToolRegistryInfo(**registry_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tool registry info: {str(e)}") 