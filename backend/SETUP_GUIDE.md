# Whisper Setup Guide

This guide will help you set up the Whisper Analysis Agent backend that integrates with your existing Whisper frontend.

## 🏗️ **Architecture Overview**

```
Frontend (Next.js) ←→ FastAPI Backend ←→ Whisper Analysis Agent ←→ OpenAI GPT-4
      ↓                      ↓                        ↓
   WebSocket            LangGraph               Git Repository
                       Workflow                  Analysis
```

## 📋 **Prerequisites**

- Python 3.9 or higher
- OpenAI API Key
- Git installed on your system
- Your existing Next.js frontend (already working)

## 🚀 **Backend Setup**

### Step 1: Create Backend Directory

```bash
# In your project root (same level as your Next.js app)
mkdir whisper-backend
cd whisper-backend
```

### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install required packages
pip install -r backend_requirements.txt
```

### Step 4: Environment Configuration

Create a `.env` file in the `whisper-backend` directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Optional: For future database integration
# DATABASE_URL=postgresql://user:password@localhost:5432/whisper
# REDIS_URL=redis://localhost:6379/0
```

### Step 5: Copy Agent Files

Copy these files to your `whisper-backend` directory:
- `repository_explorer_agent.py`
- `fastapi_backend.py`
- `backend_requirements.txt`

### Step 6: Start Backend Server

```bash
# Start the FastAPI server
python fastapi_backend.py
```

The backend will start on `http://localhost:8000`

## 🔧 **Frontend Integration**

### Step 1: Update TaskExecution Component

Replace your current `TaskExecution` component with the enhanced version that connects to the real backend:

```typescript
// In your components/TaskExecution.tsx
// Replace the existing mock implementation with the WebSocket-based real implementation
// (Use the code from frontend_integration_example.tsx)
```

### Step 2: Add WebSocket Hook

Add the `useWebSocket` hook to your project (from the frontend integration example).

### Step 3: Update TaskSelector

Ensure your `TaskSelector` includes "explore-codebase" as one of the available tasks.

## 🧪 **Testing the Integration**

### Step 1: Test Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy", "agent_ready": true}
```

### Step 2: Test with Frontend

1. Start your Next.js frontend (`npm run dev`)
2. Start the backend (`python fastapi_backend.py`)
3. Connect GitHub and select a repository
4. Choose "Explore Codebase" task
5. Watch real-time analysis progress

## 📊 **What the Agent Analyzes**

The Whisper Analysis Agent provides comprehensive analysis including:

### **File Structure Analysis**
- Total files and lines of code
- File type distribution
- Directory organization
- Code vs. configuration vs. documentation files

### **Language & Framework Detection**
- Primary programming language
- All languages used with file counts
- Framework detection (React, Django, Spring Boot, etc.)
- Confidence scores for framework identification

### **Architectural Pattern Recognition**
- MVC (Model-View-Controller)
- Microservices Architecture
- Clean Architecture
- Component-Based Architecture
- Layered Architecture
- Event-Driven Architecture
- API-First Design

### **Dependency Analysis**
- Package.json dependencies (Node.js)
- Requirements.txt (Python)
- Go.mod (Go)
- Pom.xml (Java)
- And more...

### **Component Identification**
- Entry points (main.py, app.js, etc.)
- Configuration files
- Important directories (src, components, services, etc.)
- Test suites and documentation

### **AI-Powered Insights**
- Architecture overview and assessment
- Technology stack evaluation
- Code organization analysis
- Scalability considerations
- Maintainability assessment
- Specific recommendations for improvement

## 🔍 **Sample Analysis Output**

```json
{
  "summary": "Analysis complete for TypeScript project with 247 files (15,432 lines of code). Detected architectural patterns: Component-Based Architecture, API-First Design",
  "statistics": {
    "Files Analyzed": 247,
    "Lines of Code": 15432,
    "Languages Detected": 3,
    "Main Components": 12,
    "Architecture Patterns": 2,
    "Dependency Groups": 1
  },
  "detailed_results": {
          "whisper_analysis": {
      "analysis": "## Architecture Overview\nThis is a well-structured Next.js application following modern React patterns...",
      "language_analysis": {
        "primary_language": "TypeScript",
        "languages": {"TypeScript": 89, "JavaScript": 12, "CSS": 8},
        "frameworks": [{"name": "Next.js", "confidence": 0.95}]
      },
      "architecture_patterns": ["Component-Based Architecture", "API-First Design"],
      "main_components": [...],
      "dependencies": {"Node.js": ["next", "react", "typescript", ...]}
    }
  }
}
```

## 🐛 **Troubleshooting**

### Common Issues

**1. "OPENAI_API_KEY not found"**
- Ensure you've set your OpenAI API key in the `.env` file
- Restart the backend after adding the key

**2. "Module not found" errors**
- Make sure your virtual environment is activated
- Run `pip install -r backend_requirements.txt` again

**3. WebSocket connection fails**
- Check that the backend is running on port 8000
- Ensure CORS is properly configured in FastAPI
- Verify frontend is trying to connect to the correct WebSocket URL

**4. Git clone fails**
- Ensure Git is installed and accessible
- Check that the repository URL is valid and public
- For private repositories, you'll need to implement authentication

### Backend Logs

The backend provides detailed logging. Look for:
- Repository cloning progress
- Analysis step completion
- WebSocket connection events
- Error messages with stack traces

## 🚀 **Next Steps**

### Immediate Enhancements
1. **Error Handling**: Add retry logic for failed repository clones
2. **Caching**: Cache analysis results to avoid re-analyzing the same repository
3. **Rate Limiting**: Implement rate limiting to prevent API abuse

### Future Agents
1. **Bug Hunter Agent**: Scan for potential bugs and code issues
2. **Security Auditor Agent**: Check for security vulnerabilities
3. **Performance Analyzer Agent**: Identify performance bottlenecks
4. **Documentation Generator Agent**: Generate missing documentation

### Production Considerations
1. **Database Integration**: Store analysis results and history
2. **Authentication**: Add user authentication and authorization
3. **Monitoring**: Add logging, metrics, and health checks
4. **Deployment**: Containerize with Docker and deploy to cloud platforms

## 📝 **Configuration Options**

### Agent Configuration

You can customize the agent behavior by modifying parameters in `repository_explorer_agent.py`:

```python
# Framework detection sensitivity
if score >= len(indicators) * 0.5:  # Change threshold (0.3 = more sensitive)

# Analysis depth
dependencies['Python'] = deps[:20]  # Increase limit for more dependencies

# File types to analyze
if file_ext in ['.py', '.js', '.jsx', '.ts', '.tsx', ...]:  # Add more extensions
```

### Backend Configuration

Modify settings in `fastapi_backend.py`:

```python
# CORS origins
allow_origins=["http://localhost:3000", "http://localhost:3001", "your-production-domain.com"]

# WebSocket timeout
# Add timeout configuration for long-running analyses
```

This setup gives you a production-ready Whisper Analysis Agent that can analyze any public GitHub repository and provide comprehensive architectural insights through your existing Whisper frontend! 