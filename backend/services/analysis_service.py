"""
Analysis Service - Manages repository analysis tasks and WebSocket connections
"""

import asyncio
import json
import uuid
from typing import Dict, Any, Optional
from fastapi import WebSocket
import logging

from agents.whisper_analysis_agent import WhisperAnalysisAgent
from agents.smart_analysis_agent import SmartAnalysisAgent
from core.tool_registry import get_tool_registry, initialize_tool_registry

logger = logging.getLogger(__name__)

class AnalysisService:
    """Service to manage repository analysis tasks and WebSocket connections."""
    
    def __init__(self, openai_api_key: str):
        # Initialize both agents for backward compatibility
        self.whisper_agent = WhisperAnalysisAgent(openai_api_key=openai_api_key)
        self.smart_agent = SmartAnalysisAgent(openai_api_key=openai_api_key)
        
        self.active_connections: Dict[str, WebSocket] = {}
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.task_metadata: Dict[str, Dict[str, Any]] = {}  # Store task configuration
        self._initialized = False
        
    async def initialize(self):
        """Initialize the analysis service and tool registry."""
        if self._initialized:
            return
        
        # Initialize tool registry
        await initialize_tool_registry()
        
        self._initialized = True
        logger.info("Analysis service initialized successfully")
        
    async def create_task(
        self, 
        repository_url: str, 
        task_type: str = "explore-codebase", 
        create_security_pr: bool = False,
        pr_options: Optional[Dict] = None
    ) -> str:
        """Create a new analysis task and return task ID."""
        task_id = str(uuid.uuid4())
        
        # Store task metadata (not overwriting active_tasks which stores asyncio.Task objects)
        self.task_metadata[task_id] = {
            "repository_url": repository_url,
            "task_type": task_type,
            "create_security_pr": create_security_pr,
            "pr_options": pr_options or {}
        }
        
        logger.info(f"Created analysis task {task_id} for repository: {repository_url} (PR: {create_security_pr})")
        return task_id
    
    async def create_smart_task(
        self, 
        repository_url: str, 
        context: str,
        intent: Optional[str] = None,
        target_languages: Optional[list] = None,
        scope: str = "full",
        depth: str = "comprehensive",
        additional_params: Optional[Dict] = None
    ) -> str:
        """Create a new smart analysis task and return task ID."""
        task_id = str(uuid.uuid4())
        logger.info(f"Created smart analysis task {task_id} for repository: {repository_url}")
        logger.info(f"Context: {context[:100]}...")
        return task_id
    
    async def connect_websocket(self, task_id: str, websocket: WebSocket):
        """Connect a WebSocket for real-time updates."""
        await websocket.accept()
        self.active_connections[task_id] = websocket
        logger.info(f"WebSocket connected for task {task_id}")
    
    async def disconnect_websocket(self, task_id: str):
        """Disconnect and cleanup WebSocket connection."""
        if task_id in self.active_connections:
            del self.active_connections[task_id]
        
        # Cancel any running task
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            if isinstance(task, asyncio.Task):
                task.cancel()
            del self.active_tasks[task_id]
        
        # Clean up task metadata
        if task_id in self.task_metadata:
            del self.task_metadata[task_id]
        
        logger.info(f"WebSocket disconnected for task {task_id}")
    
    async def send_message(self, task_id: str, message: Dict[str, Any]):
        """Send a message to the WebSocket client."""
        if task_id in self.active_connections:
            try:
                await self.active_connections[task_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to {task_id}: {e}")
                await self.disconnect_websocket(task_id)
    
    async def start_analysis(
        self, 
        task_id: str, 
        repository_url: str, 
        task_type: str = "explore-codebase",
        create_security_pr: bool = False,
        pr_options: Optional[Dict] = None
    ):
        """Start repository analysis with real-time updates (legacy method)."""
        
        # Create and track the analysis task
        analysis_task = asyncio.create_task(
            self._run_legacy_analysis(task_id, repository_url, task_type, create_security_pr, pr_options)
        )
        self.active_tasks[task_id] = analysis_task
        
        try:
            await analysis_task
        except asyncio.CancelledError:
            logger.info(f"Analysis task {task_id} was cancelled")
        except Exception as e:
            logger.error(f"Analysis task {task_id} failed: {e}")
        finally:
            # Cleanup
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
    
    async def start_smart_analysis(
        self, 
        task_id: str, 
        repository_url: str, 
        context: str,
        intent: Optional[str] = None,
        target_languages: Optional[list] = None,
        scope: str = "full",
        depth: str = "comprehensive",
        additional_params: Optional[Dict] = None
    ):
        """Start smart repository analysis with AI-powered tool selection."""
        
        # Ensure service is initialized
        await self.initialize()
        
        # Create and track the smart analysis task
        analysis_task = asyncio.create_task(
            self._run_smart_analysis(
                task_id, repository_url, context, intent, target_languages, 
                scope, depth, additional_params
            )
        )
        self.active_tasks[task_id] = analysis_task
        
        try:
            await analysis_task
        except asyncio.CancelledError:
            logger.info(f"Smart analysis task {task_id} was cancelled")
        except Exception as e:
            logger.error(f"Smart analysis task {task_id} failed: {e}")
        finally:
            # Cleanup
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
    
    async def _run_legacy_analysis(
        self, 
        task_id: str, 
        repository_url: str, 
        task_type: str,
        create_security_pr: bool = False,
        pr_options: Optional[Dict] = None
    ):
        """Internal method to run the legacy analysis using WhisperAnalysisAgent."""
        try:
            # Send initial confirmation
            await self.send_message(task_id, {
                "type": "task.started",
                "task_id": task_id,
                "status": "running",
                "repository_url": repository_url,
                "task_type": task_type
            })
            
            # Run the analysis with real-time updates based on task type
            last_progress = 0
            
            # Choose analysis method based on task type
            if task_type == "dependency-audit":
                # Use specialized dependency audit workflow that automatically creates PRs
                analysis_method = self.whisper_agent.analyze_repository_dependency_audit(
                    repository_url,
                    create_pr=True,  # Always create PR for dependency audits
                    pr_options=pr_options
                )
            elif create_security_pr:
                # Use PR-enabled analysis for other tasks
                analysis_method = self.whisper_agent.analyze_repository_with_pr(
                    repository_url, 
                    create_security_pr, 
                    pr_options
                )
            else:
                # Standard analysis workflow
                analysis_method = self.whisper_agent.analyze_repository(repository_url)
            
            async for update in analysis_method:
                if update["type"] == "progress":
                    current_progress = update["progress"]
                    current_step = update["current_step"]
                    
                    # Add intermediate progress updates for smoother experience
                    if current_progress > last_progress + 10:  # If jump is > 10%, add intermediate steps
                        intermediate_steps = int((current_progress - last_progress) / 5)  # 5% increments
                        for i in range(1, intermediate_steps):
                            intermediate_progress = last_progress + (i * 5)
                            if intermediate_progress < current_progress:
                                await self.send_message(task_id, {
                                    "type": "task.progress",
                                    "task_id": task_id,
                                    "current_step": f"{current_step} ({intermediate_progress:.0f}%)",
                                    "progress": intermediate_progress,
                                    "partial_results": update.get("partial_results", {})
                                })
                                # Small delay to make progress feel more natural
                                await asyncio.sleep(0.2)
                    
                    # Send the actual progress update
                    await self.send_message(task_id, {
                        "type": "task.progress",
                        "task_id": task_id,
                        "current_step": current_step,
                        "progress": current_progress,
                        "partial_results": update.get("partial_results", {})
                    })
                    
                    last_progress = current_progress
                
                elif update["type"] == "github_pr_completed":
                    # Send GitHub PR completion message
                    await self.send_message(task_id, {
                        "type": "github_pr.completed",
                        "task_id": task_id,
                        "pr_result": update["pr_result"]
                    })
                
                elif update["type"] == "github_pr_error":
                    # Send GitHub PR error message
                    await self.send_message(task_id, {
                        "type": "github_pr.error",
                        "task_id": task_id,
                        "error": update["error"]
                    })
                
                elif update["type"] == "analysis_completed":
                    # Send final analysis results (when using PR workflow)
                    await self.send_message(task_id, {
                        "type": "task.completed",
                        "task_id": task_id,
                        "results": {
                            "summary": self._generate_summary(update["results"]),
                            "statistics": self._generate_statistics(update["results"]),
                            "detailed_results": {
                                "whisper_analysis": {
                                    "analysis": update["results"]["architectural_insights"],
                                    "file_structure": update["results"]["file_structure"],
                                    "language_analysis": update["results"]["language_analysis"],
                                    "architecture_patterns": update["results"]["architecture_patterns"],
                                    "main_components": update["results"]["main_components"],
                                    "dependencies": update["results"]["dependencies"]
                                }
                            }
                        }
                    })
                    break
                
                elif update["type"] == "completed":
                    # Send final results (traditional workflow or dependency audit)
                    results = update["results"]
                    
                    # Handle dependency audit results differently
                    if task_type == "dependency-audit":
                        detailed_results = {
                            "dependency_audit": {
                                "summary": results.get("summary", "Audit completed"),
                                "vulnerability_scan": results.get("vulnerability_scan", {}),
                                "github_pr": results.get("github_pr", {}),
                                "dependencies": results.get("dependencies", {}),
                                "primary_language": results.get("primary_language", "Unknown")
                            }
                        }
                        
                        # Also include vulnerability scan results in the main results for the frontend
                        if results.get("vulnerability_scan"):
                            detailed_results["vulnerability_scanner"] = results["vulnerability_scan"]
                    else:
                        # Traditional analysis results
                        detailed_results = {
                            "whisper_analysis": {
                                "analysis": results.get("architectural_insights", ""),
                                "file_structure": results.get("file_structure", {}),
                                "language_analysis": results.get("language_analysis", {}),
                                "architecture_patterns": results.get("architecture_patterns", []),
                                "main_components": results.get("main_components", []),
                                "dependencies": results.get("dependencies", {})
                            }
                        }
                    
                    await self.send_message(task_id, {
                        "type": "task.completed",
                        "task_id": task_id,
                        "results": {
                            "summary": self._generate_summary(results),
                            "statistics": self._generate_statistics(results),
                            "detailed_results": detailed_results
                        }
                    })
                    break
        
        except Exception as e:
            logger.error(f"Legacy analysis failed for task {task_id}: {e}")
            await self.send_message(task_id, {
                "type": "task.error",
                "task_id": task_id,
                "error": f"Analysis failed: {str(e)}"
            })
    
    async def _run_smart_analysis(
        self,
        task_id: str,
        repository_url: str, 
        context: str,
        intent: Optional[str] = None,
        target_languages: Optional[list] = None,
        scope: str = "full",
        depth: str = "comprehensive",
        additional_params: Optional[Dict] = None
    ):
        """Internal method to run smart analysis using SmartAnalysisAgent."""
        try:
            # Send initial confirmation
            await self.send_message(task_id, {
                "type": "smart_task.started",
                "task_id": task_id,
                "status": "running",
                "repository_url": repository_url,
                "context": context,
                "intent": intent,
                "scope": scope,
                "depth": depth
            })
            
            # Build additional parameters
            if additional_params is None:
                additional_params = {}
            
            if intent:
                additional_params["intent"] = intent
            if target_languages:
                additional_params["target_languages"] = target_languages
            if scope:
                additional_params["scope"] = scope
            if depth:
                additional_params["depth"] = depth
            
            # Run smart analysis with real-time updates
            async for update in self.smart_agent.analyze_repository(
                repository_url, context, additional_params
            ):
                # Forward all updates to the client
                update["task_id"] = task_id
                await self.send_message(task_id, update)
                
                # Break on completion or error
                if update["type"] in ["completed", "error"]:
                    break
        
        except Exception as e:
            logger.error(f"Smart analysis failed for task {task_id}: {e}")
            await self.send_message(task_id, {
                "type": "task.error",
                "task_id": task_id,
                "error": f"Smart analysis failed: {str(e)}"
            })
    
    def _generate_summary(self, results: Dict[str, Any]) -> str:
        """Generate a summary from the analysis results."""
        lang_analysis = results.get("language_analysis", {})
        file_structure = results.get("file_structure", {})
        patterns = results.get("architecture_patterns", [])
        
        primary_lang = lang_analysis.get("primary_language", "Unknown")
        total_files = file_structure.get("total_files", 0)
        total_lines = file_structure.get("total_lines", 0)
        
        summary = f"Analysis complete for {primary_lang} project with {total_files} files ({total_lines:,} lines of code)"
        
        if patterns:
            summary += f". Detected architectural patterns: {', '.join(patterns[:3])}"
        
        return summary
    
    def _generate_statistics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate statistics from the analysis results."""
        lang_analysis = results.get("language_analysis", {})
        file_structure = results.get("file_structure", {})
        components = results.get("main_components", [])
        patterns = results.get("architecture_patterns", [])
        dependencies = results.get("dependencies", {})
        
        return {
            "Files Analyzed": file_structure.get("total_files", 0),
            "Lines of Code": file_structure.get("total_lines", 0),
            "Languages Detected": len(lang_analysis.get("languages", {})),
            "Main Components": len(components),
            "Architecture Patterns": len(patterns),
            "Dependency Groups": len(dependencies)
        }
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the status of a specific task."""
        if task_id in self.active_connections:
            return {"task_id": task_id, "status": "running"}
        elif task_id in self.active_tasks:
            return {"task_id": task_id, "status": "processing"}
        else:
            return {"task_id": task_id, "status": "not_found"}
    
    def get_active_connections_info(self) -> Dict[str, Any]:
        """Get information about active connections."""
        return {
            "active_connections": len(self.active_connections),
            "active_tasks": len(self.active_tasks),
            "connection_ids": list(self.active_connections.keys())
        }
    
    async def get_tool_registry_info(self) -> Dict[str, Any]:
        """Get information about the tool registry."""
        await self.initialize()
        
        try:
            registry = await get_tool_registry()
            return registry.get_registry_info()
        except Exception as e:
            logger.error(f"Failed to get tool registry info: {e}")
            return {
                "total_tools": 0,
                "healthy_tools": 0,
                "capabilities": [],
                "supported_languages": [],
                "tools": {},
                "error": str(e)
            } 