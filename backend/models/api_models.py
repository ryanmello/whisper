"""
API Models - Pydantic models for request/response validation
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, field_validator
import re

class AnalysisRequest(BaseModel):
    """Request model for repository analysis."""
    repository_url: str = Field(..., description="GitHub repository URL")
    task_type: str = Field(default="explore-codebase", description="Type of analysis task")
    github_token: Optional[str] = Field(None, description="GitHub token for private repositories")
    
    @field_validator('repository_url')
    @classmethod
    def validate_repository_url(cls, v):
        """Validate that the repository URL is a valid GitHub URL."""
        # More flexible pattern to handle various GitHub URL formats
        github_pattern = r'^https://github\.com/[a-zA-Z0-9\-_\.]+/[a-zA-Z0-9\-_\.]+/?$'
        if not re.match(github_pattern, v.rstrip('/')):
            raise ValueError('Must be a valid GitHub repository URL (https://github.com/owner/repo)')
        return v.rstrip('/')
    
    @field_validator('task_type')
    @classmethod
    def validate_task_type(cls, v):
        """Validate task type."""
        valid_types = [
            'explore-codebase', 'find-bugs', 'security-audit', 
            'performance-analysis', 'code-quality', 'documentation-review',
            'dependency-analysis', 'architecture-review'
        ]
        if v not in valid_types:
            raise ValueError(f'Task type must be one of: {", ".join(valid_types)}')
        return v

class AnalysisResponse(BaseModel):
    """Response model for analysis task creation."""
    task_id: str = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Task status")
    message: str = Field(..., description="Status message")
    websocket_url: str = Field(..., description="WebSocket URL for real-time updates")

class TaskStatus(BaseModel):
    """Model for task status information."""
    task_id: str
    status: str  # created, running, completed, failed, not_found
    created_at: Optional[str] = None
    completed_at: Optional[str] = None

class ProgressUpdate(BaseModel):
    """Model for progress update messages."""
    type: str = Field(..., description="Message type")
    task_id: str = Field(..., description="Task identifier")
    current_step: str = Field(..., description="Current analysis step")
    progress: float = Field(..., ge=0, le=100, description="Progress percentage")
    partial_results: Dict[str, Any] = Field(default_factory=dict, description="Partial analysis results")

class FileStructure(BaseModel):
    """Model for file structure analysis results."""
    total_files: int
    total_lines: int
    file_types: Dict[str, int]
    directory_structure: Dict[str, List[str]]
    main_directories: List[str]

class LanguageAnalysis(BaseModel):
    """Model for language analysis results."""
    languages: Dict[str, int]
    primary_language: str
    frameworks: List[Dict[str, Any]]
    total_code_files: int

class MainComponent(BaseModel):
    """Model for main component information."""
    name: str
    type: str
    path: str
    size: Optional[int] = None
    file_count: Optional[int] = None

class WhisperAnalysisResults(BaseModel):
    """Model for whisper analysis results."""
    analysis: str = Field(..., description="AI-generated architectural insights")
    file_structure: FileStructure
    language_analysis: LanguageAnalysis
    architecture_patterns: List[str]
    main_components: List[MainComponent]
    dependencies: Dict[str, List[str]]

class AnalysisResults(BaseModel):
    """Model for complete analysis results."""
    summary: str = Field(..., description="Analysis summary")
    statistics: Dict[str, Any] = Field(..., description="Key statistics")
    detailed_results: Dict[str, Any] = Field(..., description="Detailed analysis results")

class TaskCompletedMessage(BaseModel):
    """Model for task completion message."""
    type: str = Field(default="task.completed")
    task_id: str
    results: AnalysisResults

class TaskErrorMessage(BaseModel):
    """Model for task error message."""
    type: str = Field(default="task.error")
    task_id: str
    error: str
    error_code: Optional[str] = None

class TaskStartedMessage(BaseModel):
    """Model for task started message."""
    type: str = Field(default="task.started")
    task_id: str
    status: str = Field(default="running")
    repository_url: str
    task_type: str

class HealthCheck(BaseModel):
    """Model for health check response."""
    status: str = Field(..., description="Service status")
    agent_ready: bool = Field(..., description="Whether the analysis agent is ready")
    version: str = Field(default="1.0.0", description="API version")
    uptime: Optional[float] = Field(None, description="Service uptime in seconds")

class ActiveConnectionsInfo(BaseModel):
    """Model for active connections information."""
    active_connections: int = Field(..., description="Number of active WebSocket connections")
    active_tasks: int = Field(..., description="Number of active analysis tasks")
    connection_ids: List[str] = Field(..., description="List of active connection IDs") 