// API service for communicating with the FastAPI backend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface TaskResponse {
  task_id: string;
  websocket_url: string;
  status: string;
  repository_url: string;
  task_type: string;
}

export interface AnalysisProgress {
  type: 'task.started' | 'task.progress' | 'task.completed' | 'task.error';
  task_id?: string;
  current_step?: string;
  progress?: number;
  partial_results?: {
    file_structure?: Record<string, unknown>;
    language_analysis?: Record<string, unknown>;
    architecture_patterns?: string[];
    main_components?: Record<string, unknown>[];
  };
  results?: {
    summary: string;
    statistics: Record<string, any>;
    detailed_results: {
      whisper_analysis: {
        analysis: string;
        file_structure: Record<string, unknown>;
        language_analysis: Record<string, unknown>;
        architecture_patterns: string[];
        main_components: Record<string, unknown>[];
        dependencies: Record<string, string[]>;
      };
    };
  };
  error?: string;
}

export class WhisperAPI {
  /**
   * Create a new analysis task
   */
  static async createTask(repositoryUrl: string, taskType: string = 'explore-codebase'): Promise<TaskResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/tasks/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          repository_url: repositoryUrl,
          task_type: taskType,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to create task: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating task:', error);
      throw error;
    }
  }

  /**
   * Get task status
   */
  static async getTaskStatus(taskId: string): Promise<Record<string, unknown>> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/tasks/${taskId}`);
      
      if (!response.ok) {
        throw new Error(`Failed to get task status: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting task status:', error);
      throw error;
    }
  }

  /**
   * Connect to WebSocket for real-time updates
   */
  static connectWebSocket(
    taskId: string,
    repositoryUrl: string,
    taskType: string,
    onMessage: (data: AnalysisProgress) => void,
    onError: (error: Event) => void,
    onClose: (event: CloseEvent) => void
  ): WebSocket {
    const wsUrl = `ws://localhost:8000/ws/tasks/${taskId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected');
      // Send task parameters to start analysis
      ws.send(JSON.stringify({
        repository_url: repositoryUrl,
        task_type: taskType,
      }));
    };

    ws.onmessage = (event) => {
      try {
        const data: AnalysisProgress = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      onError(error);
    };

    ws.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason);
      onClose(event);
    };

    return ws;
  }

  /**
   * Check if backend is healthy
   */
  static async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      return response.ok;
    } catch (error) {
      console.error('Backend health check failed:', error);
      return false;
    }
  }

  /**
   * Get active connections info (for debugging)
   */
  static async getActiveConnections(): Promise<Record<string, unknown>> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/active-connections`);
      
      if (!response.ok) {
        throw new Error(`Failed to get active connections: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting active connections:', error);
      throw error;
    }
  }
}

/**
 * Utility function to validate GitHub repository URL
 */
export function validateGitHubUrl(url: string): boolean {
  const githubUrlPattern = /^https:\/\/github\.com\/[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+\/?$/;
  return githubUrlPattern.test(url);
}

/**
 * Extract repository name from GitHub URL
 */
export function extractRepoName(url: string): string {
  const match = url.match(/github\.com\/([^\/]+\/[^\/]+)/);
  return match ? match[1] : url;
} 