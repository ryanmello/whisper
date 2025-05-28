# Backend Architecture & Structure

This document outlines the organized structure of the Whisper backend application.

## Directory Structure

```
backend/
├── app.py                      # Main FastAPI application instance
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── api/                        # API layer
│   ├── __init__.py
│   ├── middleware/             # Custom middleware
│   │   └── __init__.py
│   └── routes/                 # API route modules
│       ├── __init__.py
│       ├── health.py           # Health check endpoints
│       ├── tasks.py            # Task management endpoints
│       └── websocket.py        # WebSocket endpoints
├── agents/                     # Analysis agents
│   ├── __init__.py
│   └── whisper_analysis_agent.py  # Main repository analysis agent
├── config/                     # Configuration management
│   ├── __init__.py
│   └── settings.py             # Application settings and environment variables
├── core/                       # Core application logic
│   ├── __init__.py
│   └── app.py                  # FastAPI application factory
├── models/                     # Data models
│   ├── __init__.py
│   └── api_models.py           # Pydantic models for API
├── services/                   # Business logic services
│   ├── __init__.py
│   └── analysis_service.py     # Repository analysis service
└── utils/                      # Utility functions
    ├── __init__.py
    ├── file_utils.py           # File handling utilities
    └── logging_config.py       # Logging configuration
```

## Module Responsibilities

### `api/`
Contains all API-related code including routes, middleware, and request/response handling.

- **`routes/`**: Individual route modules organized by functionality
  - `health.py`: Application health and status endpoints
  - `tasks.py`: Repository analysis task management
  - `websocket.py`: Real-time WebSocket connections
- **`middleware/`**: Custom middleware components

### `agents/`
Houses the AI analysis agents responsible for repository exploration and code analysis.

- **`whisper_analysis_agent.py`**: Main agent using LangGraph for repository analysis workflow

### `config/`
Centralized configuration management.

- **`settings.py`**: Environment variable handling and application settings

### `core/`
Core application initialization and factory patterns.

- **`app.py`**: FastAPI application factory with dependency injection

### `models/`
Pydantic data models for request/response validation and type safety.

- **`api_models.py`**: API request/response models

### `services/`
Business logic layer containing service classes.

- **`analysis_service.py`**: Manages analysis tasks and WebSocket connections

### `utils/`
Shared utility functions and helpers.

- **`file_utils.py`**: File system operations and utilities
- **`logging_config.py`**: Centralized logging setup

## Key Design Patterns

### 1. Application Factory Pattern
The application uses a factory pattern in `core/app.py` to create and configure the FastAPI instance, allowing for better testing and multiple environment configurations.

### 2. Dependency Injection
Services are injected as dependencies through the `get_analysis_service()` function, making the code more testable and maintainable.

### 3. Modular Route Organization
Routes are organized by functionality in separate modules, making the codebase easier to navigate and maintain.

### 4. Centralized Configuration
All configuration is managed through the `settings.py` module, providing a single source of truth for environment variables and application settings.

### 5. Separation of Concerns
Clear separation between:
- API layer (routing, validation)
- Business logic (services)
- Core application logic (initialization)
- Utilities (shared functions)

## Starting the Application

The application can be started using:

```bash
python main.py
```

Or for development with auto-reload:

```bash
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

## Environment Configuration

Configuration is handled through environment variables or `.env` file:

```env
HOST=127.0.0.1
PORT=8000
RELOAD=true
LOG_LEVEL=info
OPENAI_API_KEY=your-api-key
FRONTEND_URL=http://localhost:3000
MAX_CONCURRENT_ANALYSES=5
```

## Benefits of This Structure

1. **Maintainability**: Clear separation of concerns makes the code easier to understand and modify
2. **Scalability**: Modular structure allows for easy addition of new features
3. **Testability**: Dependency injection and modular design facilitate unit testing
4. **Reusability**: Utilities and services can be easily reused across the application
5. **Configuration Management**: Centralized settings make deployment and environment management easier 