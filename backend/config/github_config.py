"""
GitHub Configuration for Pull Request Integration
"""

import os
import logging
from typing import List, Optional
from dataclasses import dataclass

# Use basic logging if custom logging config is not available
try:
    from utils.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)


@dataclass
class GitHubConfig:
    """Configuration for GitHub integration."""
    
    # Authentication
    github_token: Optional[str] = None
    github_app_id: Optional[str] = None
    github_app_private_key_path: Optional[str] = None
    
    # PR Configuration
    default_target_branch: str = "main"
    default_pr_reviewers: List[str] = None
    default_pr_labels: List[str] = None
    pr_title_template: str = "Security: Fix {count} vulnerabilities in {language} dependencies"
    pr_branch_prefix: str = "security/fix-dependencies"
    
    # Repository Settings
    max_files_per_pr: int = 10
    enable_draft_prs: bool = False
    auto_delete_branch_on_merge: bool = True
    
    # Safety Settings
    require_repository_access_validation: bool = True
    max_prs_per_repository_per_day: int = 5
    dry_run_mode: bool = False
    
    def __post_init__(self):
        """Initialize default values and validate configuration."""
        if self.default_pr_reviewers is None:
            self.default_pr_reviewers = []
        
        if self.default_pr_labels is None:
            self.default_pr_labels = ["security", "dependencies", "automated"]


def load_github_config() -> GitHubConfig:
    """
    Load GitHub configuration from environment variables.
    
    Returns:
        GitHubConfig instance with loaded configuration
    """
    config = GitHubConfig()
    
    # Load authentication
    config.github_token = os.getenv("GITHUB_TOKEN")
    config.github_app_id = os.getenv("GITHUB_APP_ID")
    config.github_app_private_key_path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    
    # Load PR configuration
    config.default_target_branch = os.getenv("DEFAULT_TARGET_BRANCH", "main")
    
    # Parse reviewers from comma-separated string
    reviewers_str = os.getenv("DEFAULT_PR_REVIEWERS", "")
    if reviewers_str:
        config.default_pr_reviewers = [r.strip() for r in reviewers_str.split(",") if r.strip()]
    
    # Parse labels from comma-separated string
    labels_str = os.getenv("DEFAULT_PR_LABELS", "security,dependencies,automated")
    if labels_str:
        config.default_pr_labels = [l.strip() for l in labels_str.split(",") if l.strip()]
    
    # Load safety settings
    config.dry_run_mode = os.getenv("GITHUB_DRY_RUN", "false").lower() == "true"
    config.enable_draft_prs = os.getenv("ENABLE_DRAFT_PRS", "false").lower() == "true"
    
    # Validate configuration
    if not config.github_token and not (config.github_app_id and config.github_app_private_key_path):
        logger.warning("No GitHub authentication configured. PR creation will be disabled.")
    
    logger.info(f"GitHub config loaded - Token: {'✅' if config.github_token else '❌'}, "
                f"App Auth: {'✅' if config.github_app_id else '❌'}, "
                f"Dry Run: {config.dry_run_mode}")
    
    return config


# Global configuration instance
github_config = load_github_config() 