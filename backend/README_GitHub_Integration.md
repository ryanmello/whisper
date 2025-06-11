# GitHub Pull Request Integration

## Overview

This enhancement adds GitHub Pull Request creation capability to the Whisper Analysis Agent's dependency audit feature. When vulnerabilities are found in Go dependencies, the agent can automatically create pull requests with fixes.

## Features

- **Automatic PR Creation**: Create pull requests to fix security vulnerabilities
- **Go Module Support**: Parse and update `go.mod` files with dependency fixes
- **Smart Version Management**: Analyze version compatibility and breaking changes
- **Comprehensive PR Content**: Detailed descriptions with vulnerability information
- **Dry Run Mode**: Test PR creation without making actual changes
- **Rate Limiting**: Respect GitHub API limits and permissions

## Configuration

### Environment Variables

```bash
# GitHub Authentication (required)
GITHUB_TOKEN=ghp_your_github_token_here

# PR Configuration (optional)
DEFAULT_TARGET_BRANCH=main
DEFAULT_PR_REVIEWERS=@security-team,@devops-team
DEFAULT_PR_LABELS=security,dependencies,automated

# Behavior Settings (optional)
ENABLE_DRAFT_PRS=false
GITHUB_DRY_RUN=false
```

### Required GitHub Token Scopes

Your GitHub token needs the following scopes:
- `repo` (for private repositories) OR `public_repo` (for public repositories)
- `pull_requests:write` (for creating pull requests)

## API Usage

### Enhanced Analysis Request

```json
{
  "repository_url": "https://github.com/example/go-project",
  "task_type": "security-audit",
  "create_security_pr": true,
  "pr_options": {
    "target_branch": "main",
    "reviewers": ["@security-team"],
    "labels": ["security", "dependencies"],
    "draft": false
  }
}
```

### Response with PR Information

```json
{
  "task_id": "task_123456",
  "status": "completed",
  "message": "Analysis completed successfully",
  "websocket_url": "ws://localhost:8000/ws/tasks/task_123456",
  "github_pr_enabled": true,
  "analysis_results": {
    "vulnerabilities_found": 3,
    "severity_breakdown": {
      "high": 1,
      "medium": 2
    }
  },
  "github_pr": {
    "success": true,
    "pr_url": "https://github.com/example/go-project/pull/42",
    "pr_number": 42,
    "branch_name": "security/fix-dependencies-20241201",
    "files_changed": ["go.mod", "go.sum"],
    "vulnerabilities_fixed": 3
  }
}
```

## WebSocket Events

The integration adds new WebSocket message types for real-time PR creation updates:

### GitHub PR Progress
```json
{
  "type": "github_pr.progress",
  "task_id": "task_123456",
  "step": "Creating branch and applying fixes",
  "progress": 75.0
}
```

### GitHub PR Completed
```json
{
  "type": "github_pr.completed",
  "task_id": "task_123456",
  "pr_result": {
    "success": true,
    "pr_url": "https://github.com/example/go-project/pull/42",
    "pr_number": 42,
    "vulnerabilities_fixed": 3
  }
}
```

### GitHub PR Error
```json
{
  "type": "github_pr.error",
  "task_id": "task_123456",
  "error": "No permission to create pull requests for this repository"
}
```

## GitHub Service Status

Check GitHub service availability:

```bash
GET /api/github/status
```

Response:
```json
{
  "available": true,
  "authenticated": true,
  "rate_limit_remaining": 4982
}
```

## Implementation Details

### Architecture

1. **GitHub Service** (`services/github_service.py`): Handles GitHub API interactions
2. **Go.mod Parser** (`utils/go_mod_parser.py`): Parses and updates Go module files
3. **Dependency Updater** (`services/dependency_updater.py`): Maps vulnerabilities to fixes
4. **Enhanced Agent** (`agents/whisper_analysis_agent.py`): Integrates PR creation

### Workflow

1. **Analysis**: Run normal repository analysis
2. **Vulnerability Detection**: Identify security issues in dependencies
3. **Fix Generation**: Map vulnerabilities to dependency updates
4. **Repository Cloning**: Clone repository to temporary location
5. **File Updates**: Apply dependency fixes to `go.mod` files
6. **Validation**: Verify syntax and run `go mod tidy`
7. **Branch Creation**: Create new branch with timestamp
8. **Commit & Push**: Commit changes and push to GitHub
9. **PR Creation**: Create pull request with detailed description
10. **Cleanup**: Remove temporary files

### Security Considerations

- **Token Security**: GitHub tokens are never logged or exposed
- **Repository Safety**: Validate repository ownership and access
- **Change Validation**: Verify syntax before applying updates
- **Minimal Permissions**: Use least-privilege access patterns

## Error Handling

Common error scenarios and resolutions:

### Authentication Errors
- **Problem**: `GitHub service not available - check authentication`
- **Solution**: Verify `GITHUB_TOKEN` is set and valid

### Permission Errors
- **Problem**: `No permission to create pull requests for this repository`
- **Solution**: Ensure token has appropriate scopes and repository access

### Repository Errors
- **Problem**: `No go.mod files found in repository`
- **Solution**: Ensure repository is a Go project with `go.mod` files

### Validation Errors
- **Problem**: `Invalid go.mod syntax after update`
- **Solution**: Check vulnerability data format and fix mapping logic

## Testing

### Dry Run Mode

Enable dry run mode to test without creating actual PRs:

```bash
GITHUB_DRY_RUN=true
```

### Example Test Request

```bash
curl -X POST "http://localhost:8000/api/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "repository_url": "https://github.com/your-username/test-go-project",
    "task_type": "security-audit",
    "create_security_pr": true,
    "pr_options": {
      "target_branch": "main",
      "labels": ["test", "security"],
      "draft": true
    }
  }'
```

## Future Enhancements

- **Multi-Language Support**: Extend to `package.json`, `requirements.txt`, etc.
- **Advanced Testing**: Run tests in PR branch before creation
- **Auto-merge**: Automatic merging for low-risk security patches
- **Notification Integration**: Slack/Teams notifications for created PRs
- **Batch Processing**: Handle multiple repositories in organization
- **GitHub App Support**: Enhanced authentication with GitHub Apps

## Troubleshooting

### Enable Debug Logging

Set log level to debug for detailed information:

```bash
LOG_LEVEL=DEBUG
```

### Check GitHub API Rate Limits

Monitor rate limits to avoid API restrictions:

```bash
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/rate_limit
```

### Verify Repository Access

Test repository access with your token:

```bash
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/repos/OWNER/REPO
``` 