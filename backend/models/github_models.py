"""
GitHub-specific API Models for Pull Request Integration
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from dataclasses import dataclass


class GitHubPROptions(BaseModel):
    """Options for GitHub pull request creation."""
    target_branch: str = Field(default="main", description="Target branch for the pull request")
    reviewers: Optional[List[str]] = Field(None, description="List of reviewers to add")
    labels: Optional[List[str]] = Field(None, description="List of labels to add")
    draft: bool = Field(default=False, description="Create as draft pull request")
    auto_merge: bool = Field(default=False, description="Enable auto-merge if possible")


class GitHubPRResult(BaseModel):
    """Result of GitHub pull request creation."""
    success: bool = Field(..., description="Whether PR creation was successful")
    pr_url: Optional[str] = Field(None, description="URL of the created pull request")
    pr_number: Optional[int] = Field(None, description="Pull request number")
    pr_id: Optional[int] = Field(None, description="Pull request ID")
    branch_name: Optional[str] = Field(None, description="Name of the created branch")
    files_changed: List[str] = Field(default_factory=list, description="List of files that were modified")
    vulnerabilities_fixed: int = Field(default=0, description="Number of vulnerabilities fixed")
    error_message: Optional[str] = Field(None, description="Error message if creation failed")


class RepositoryAccessInfo(BaseModel):
    """Information about repository access permissions."""
    has_write_access: bool = Field(..., description="Whether user has write access to repository")
    can_create_prs: bool = Field(..., description="Whether user can create pull requests")
    is_fork_required: bool = Field(..., description="Whether forking is required for PR creation")
    fork_url: Optional[str] = Field(None, description="URL of fork if available")
    repository_type: str = Field(default="public", description="Repository type (public/private)")


class VulnerabilityFix(BaseModel):
    """Information about a vulnerability fix in a dependency update."""
    module_path: str = Field(..., description="Go module path")
    current_version: str = Field(..., description="Current vulnerable version")
    updated_version: str = Field(..., description="Fixed version")
    vulnerability_ids: List[str] = Field(default_factory=list, description="CVE/vulnerability IDs")
    severity: str = Field(..., description="Vulnerability severity")
    description: str = Field(default="", description="Description of the vulnerability")


class SecurityPRRequest(BaseModel):
    """Request to create a security pull request."""
    repository_url: str = Field(..., description="GitHub repository URL")
    vulnerability_fixes: List[VulnerabilityFix] = Field(..., description="List of vulnerability fixes to apply")
    pr_options: Optional[GitHubPROptions] = Field(None, description="Pull request creation options")
    dry_run: bool = Field(default=False, description="Perform dry run without creating actual PR")


class SecurityPRResponse(BaseModel):
    """Response from security pull request creation."""
    task_id: str = Field(..., description="Task ID for tracking the PR creation")
    status: str = Field(..., description="Initial status of the task")
    message: str = Field(..., description="Status message")
    estimated_time: str = Field(default="2-5 minutes", description="Estimated completion time")
    pr_result: Optional[GitHubPRResult] = Field(None, description="PR creation result if completed")


class GitHubAuthInfo(BaseModel):
    """GitHub authentication information."""
    auth_type: str = Field(..., description="Authentication type (token/app)")
    has_valid_auth: bool = Field(..., description="Whether authentication is valid")
    authenticated_user: Optional[str] = Field(None, description="Authenticated GitHub username")
    permissions: List[str] = Field(default_factory=list, description="Available permissions")


class GitHubServiceStatus(BaseModel):
    """Status of GitHub service availability."""
    available: bool = Field(..., description="Whether GitHub service is available")
    auth_configured: bool = Field(..., description="Whether authentication is configured")
    auth_info: Optional[GitHubAuthInfo] = Field(None, description="Authentication information")
    rate_limit_remaining: Optional[int] = Field(None, description="GitHub API rate limit remaining")
    rate_limit_reset: Optional[str] = Field(None, description="Rate limit reset time")


# Enhanced Analysis Request/Response models for GitHub integration

class EnhancedAnalysisRequest(BaseModel):
    """Enhanced analysis request with GitHub PR creation options."""
    repository_url: str = Field(..., description="GitHub repository URL")
    task_type: str = Field(default="dependency-audit", description="Type of analysis to perform")
    github_token: Optional[str] = Field(None, description="GitHub token (if not in environment)")
    pr_options: Optional[GitHubPROptions] = Field(None, description="PR creation options (only used with dependency-audit task type)")
    
    class Config:
        schema_extra = {
            "example": {
                "repository_url": "https://github.com/example/go-project",
                "task_type": "dependency-audit",
                "pr_options": {
                    "target_branch": "main",
                    "reviewers": ["@security-team"],
                    "labels": ["security", "dependencies"],
                    "draft": False
                }
            }
        }


class EnhancedAnalysisResponse(BaseModel):
    """Enhanced analysis response with GitHub PR information."""
    task_id: str = Field(..., description="Analysis task ID")
    status: str = Field(..., description="Task status")
    message: str = Field(..., description="Status message")
    websocket_url: str = Field(..., description="WebSocket URL for progress updates")
    analysis_results: Optional[Dict[str, Any]] = Field(None, description="Analysis results")
    github_pr: Optional[GitHubPRResult] = Field(None, description="GitHub PR creation result")
    
    class Config:
        schema_extra = {
            "example": {
                "task_id": "task_123456",
                "status": "completed",
                "message": "Analysis completed successfully",
                "websocket_url": "ws://localhost:8000/ws/tasks/task_123456",
                "analysis_results": {
                    "vulnerabilities_found": 3,
                    "severity_breakdown": {
                        "high": 1,
                        "medium": 2
                    }
                },
                "github_pr": {
                    "success": True,
                    "pr_url": "https://github.com/example/go-project/pull/42",
                    "pr_number": 42,
                    "branch_name": "security/fix-dependencies-20241201",
                    "files_changed": ["go.mod", "go.sum"],
                    "vulnerabilities_fixed": 3
                }
            }
        }


# WebSocket message models for GitHub PR progress

class GitHubPRProgressMessage(BaseModel):
    """WebSocket message for GitHub PR creation progress."""
    type: str = Field(default="github_pr.progress", description="Message type")
    task_id: str = Field(..., description="Task ID")
    step: str = Field(..., description="Current step in PR creation")
    progress: float = Field(..., ge=0, le=100, description="Progress percentage")
    details: Optional[str] = Field(None, description="Additional details")


class GitHubPRCompletedMessage(BaseModel):
    """WebSocket message for completed GitHub PR creation."""
    type: str = Field(default="github_pr.completed", description="Message type") 
    task_id: str = Field(..., description="Task ID")
    pr_result: GitHubPRResult = Field(..., description="PR creation result")


class GitHubPRErrorMessage(BaseModel):
    """WebSocket message for GitHub PR creation errors."""
    type: str = Field(default="github_pr.error", description="Message type")
    task_id: str = Field(..., description="Task ID")
    error: str = Field(..., description="Error message")
    step: Optional[str] = Field(None, description="Step where error occurred")
    retry_possible: bool = Field(default=False, description="Whether retry is possible") 