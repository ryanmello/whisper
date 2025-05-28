# Whisper Backend Architecture with LangGraph

## 1. Project Structure
```
whisper-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── config.py              # Configuration
│   ├── database.py            # Database setup
│   ├── models/                # SQLAlchemy models
│   ├── api/                   # API routes
│   │   ├── __init__.py
│   │   ├── tasks.py           # Task management endpoints
│   │   └── repositories.py    # Repository endpoints
│   ├── agents/                # LangGraph agents
│   │   ├── __init__.py
│   │   ├── base.py            # Base agent class
│   │   ├── explorer.py        # Whisper analysis
│   │   ├── bug_hunter.py      # Bug detection
│   │   ├── security.py        # Security audit
│   │   └── workflows.py       # LangGraph workflows
│   ├── services/              # Business logic
│   │   ├── __init__.py
│   │   ├── github.py          # GitHub integration
│   │   ├── task_manager.py    # Task orchestration
│   │   └── websocket.py       # Real-time updates
│   └── utils/                 # Utilities
│       ├── __init__.py
│       └── helpers.py
├── requirements.txt
├── docker-compose.yml
└── README.md
```

## 2. Core Dependencies
```txt
fastapi==0.104.1
uvicorn==0.24.0
websockets==12.0
sqlalchemy==2.0.23
alembic==1.12.1
redis==5.0.1
celery==5.3.4
langgraph==0.0.62
langchain==0.0.350
langchain-openai==0.0.2
langchain-community==0.0.10
python-multipart==0.0.6
pydantic==2.5.0
httpx==0.25.2
gitpython==3.1.40
python-dotenv==1.0.0
psycopg2-binary==2.9.9
```

## 3. LangGraph Workflow Example

### Task Processing Flow:
```
[Start] → [Repository Clone] → [Agent Selection] → [Parallel Processing] → [Result Aggregation] → [End]
    ↓           ↓                    ↓                     ↓                      ↓
[Update UI] [Update UI]        [Update UI]          [Update UI]           [Final Result]
```

### Agent Coordination:
- **Supervisor Agent**: Coordinates the workflow
- **Specialized Agents**: Handle specific analysis tasks
- **Aggregator Agent**: Combines results and generates insights

## 4. Real-time Communication

### WebSocket Events:
- `task.started` - Task initiation
- `task.progress` - Progress updates (step completion)
- `task.agent_result` - Individual agent completion
- `task.completed` - Final results
- `task.error` - Error handling

## 5. Database Schema

### Tables:
- `tasks` - Task metadata and status
- `repositories` - Repository information
- `analysis_results` - Detailed analysis outputs
- `agent_logs` - Agent execution logs

## 6. API Endpoints

### Core Routes:
- `POST /api/tasks/` - Create new analysis task
- `GET /api/tasks/{task_id}` - Get task status
- `GET /api/tasks/{task_id}/results` - Get analysis results
- `WebSocket /ws/tasks/{task_id}` - Real-time updates

## 7. Environment Variables
```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/whisper

# Redis
REDIS_URL=redis://localhost:6379/0

# GitHub
GITHUB_TOKEN=your_github_token

# AI Models
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Security
SECRET_KEY=your-secret-key
```

## 8. Docker Setup
```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/whisper
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: whisper
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
``` 