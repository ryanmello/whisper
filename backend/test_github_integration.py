#!/usr/bin/env python3
"""
Comprehensive Test Suite for GitHub PR Integration
"""

import os
import sys
import requests
import json
import time
from typing import Dict, Any, Optional

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_step(step: str, status: str = "INFO"):
    """Print formatted test step"""
    color = Colors.CYAN if status == "INFO" else Colors.GREEN if status == "PASS" else Colors.RED
    print(f"{color}[{status}]{Colors.END} {step}")

def print_result(test_name: str, passed: bool, details: str = ""):
    """Print test result"""
    status = "PASS" if passed else "FAIL"
    color = Colors.GREEN if passed else Colors.RED
    print(f"{color}✓ {test_name}{Colors.END}" if passed else f"{color}✗ {test_name}{Colors.END}")
    if details:
        print(f"    {details}")

class GitHubIntegrationTester:
    """Test suite for GitHub PR integration"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "tests": []
        }
    
    def run_test(self, test_name: str, test_func) -> bool:
        """Run a single test and record results"""
        self.results["total"] += 1
        try:
            result = test_func()
            if result:
                self.results["passed"] += 1
                print_result(test_name, True)
            else:
                self.results["failed"] += 1
                print_result(test_name, False)
            self.results["tests"].append({"name": test_name, "passed": result})
            return result
        except Exception as e:
            self.results["failed"] += 1
            print_result(test_name, False, f"Exception: {str(e)}")
            self.results["tests"].append({"name": test_name, "passed": False, "error": str(e)})
            return False
    
    def test_server_health(self) -> bool:
        """Test if the server is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            try:
                # Try the docs endpoint if health doesn't exist
                response = requests.get(f"{self.base_url}/docs", timeout=5)
                return response.status_code == 200
            except:
                return False
    
    def test_github_status_endpoint(self) -> bool:
        """Test GitHub status API endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/github/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"    GitHub Available: {data.get('available', False)}")
                print(f"    Authenticated: {data.get('authenticated', False)}")
                if 'rate_limit_remaining' in data:
                    print(f"    Rate Limit: {data['rate_limit_remaining']}")
                return True
            return False
        except Exception as e:
            print(f"    Error: {e}")
            return False
    
    def test_github_config_loading(self) -> bool:
        """Test GitHub configuration loading"""
        try:
            # Check if environment variables are set
            github_token = os.getenv("GITHUB_TOKEN")
            if github_token:
                print(f"    GitHub Token: ✓ (starts with {github_token[:10]}...)")
                return True
            else:
                print("    GitHub Token: ✗ (not set in environment)")
                return False
        except Exception:
            return False
    
    def test_import_dependencies(self) -> bool:
        """Test if GitHub integration dependencies can be imported"""
        try:
            # Test PyGithub import
            import github
            print("    PyGithub: ✓")
            
            # Test GitPython import
            import git
            print("    GitPython: ✓")
            
            # Test our GitHub service
            sys.path.append('backend')
            from services.github_service import github_service, GITHUB_AVAILABLE, GIT_AVAILABLE
            print(f"    GitHub Service Available: {GITHUB_AVAILABLE}")
            print(f"    Git Service Available: {GIT_AVAILABLE}")
            print(f"    Service Initialized: {github_service.is_available()}")
            
            return GITHUB_AVAILABLE and GIT_AVAILABLE
        except Exception as e:
            print(f"    Import Error: {e}")
            return False
    
    def test_create_task_with_pr(self) -> bool:
        """Test creating an analysis task with PR creation enabled"""
        try:
            payload = {
                "repository_url": "https://github.com/gin-gonic/gin",  # Public Go repo
                "task_type": "security-audit",
                "create_security_pr": True,
                "pr_options": {
                    "target_branch": "main",
                    "labels": ["test", "security"],
                    "draft": True
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/tasks/",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"    Task ID: {data.get('task_id')}")
                print(f"    GitHub PR Enabled: {data.get('github_pr_enabled', False)}")
                print(f"    WebSocket URL: {data.get('websocket_url', 'N/A')}")
                return data.get('github_pr_enabled', False)
            else:
                print(f"    HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            print(f"    Error: {e}")
            return False
    
    def test_go_mod_parser(self) -> bool:
        """Test Go.mod parsing functionality"""
        try:
            sys.path.append('backend')
            from utils.go_mod_parser import GoModParser
            
            # Create a test go.mod content
            test_content = """module github.com/test/project

go 1.21

require (
    github.com/gin-gonic/gin v1.9.0
    golang.org/x/crypto v0.1.0
)"""
            
            parser = GoModParser()
            go_mod_file = parser._parse_content(test_content)
            
            print(f"    Module Path: {go_mod_file.module_path}")
            print(f"    Go Version: {go_mod_file.go_version}")
            print(f"    Dependencies: {len(go_mod_file.dependencies)}")
            
            return go_mod_file.module_path == "github.com/test/project"
        except Exception as e:
            print(f"    Error: {e}")
            return False
    
    def test_dependency_updater(self) -> bool:
        """Test dependency vulnerability updating"""
        try:
            sys.path.append('backend')
            from services.dependency_updater import DependencyUpdater
            from utils.go_mod_parser import GoModParser
            
            # Create test vulnerability data
            vuln_data = {
                "vulnerabilities": [
                    {
                        "id": "GO-TEST-001",
                        "module": "github.com/gin-gonic/gin",
                        "affected": [{
                            "ranges": [{
                                "type": "SEMVER",
                                "events": [{"fixed": "v1.9.1"}]
                            }]
                        }],
                        "severity": "medium",
                        "summary": "Test vulnerability"
                    }
                ]
            }
            
            # Create test go.mod
            test_content = """module github.com/test/project
require github.com/gin-gonic/gin v1.9.0"""
            
            parser = GoModParser()
            go_mod_file = parser._parse_content(test_content)
            
            updater = DependencyUpdater()
            updates = updater.analyze_vulnerabilities(vuln_data, go_mod_file)
            
            print(f"    Vulnerabilities Found: {len(updates)}")
            if updates:
                update = updates[0]
                print(f"    Update: {update.module_path} {update.current_version} -> {update.updated_version}")
            
            return len(updates) > 0
        except Exception as e:
            print(f"    Error: {e}")
            return False
    
    def test_dry_run_mode(self) -> bool:
        """Test GitHub PR creation in dry run mode"""
        try:
            # Set dry run mode
            os.environ["GITHUB_DRY_RUN"] = "true"
            
            sys.path.append('backend')
            from services.github_service import GitHubService
            from config.github_config import load_github_config
            
            config = load_github_config()
            service = GitHubService(config)
            
            print(f"    Dry Run Mode: {config.dry_run_mode}")
            print(f"    Service Available: {service.is_available()}")
            
            # Reset environment
            os.environ.pop("GITHUB_DRY_RUN", None)
            
            return config.dry_run_mode
        except Exception as e:
            print(f"    Error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests and print summary"""
        print(f"{Colors.BOLD}{Colors.CYAN}🧪 GitHub PR Integration Test Suite{Colors.END}\n")
        
        # Basic connectivity tests
        print(f"{Colors.BOLD}📡 Connectivity Tests{Colors.END}")
        self.run_test("Server Health Check", self.test_server_health)
        self.run_test("GitHub Status Endpoint", self.test_github_status_endpoint)
        print()
        
        # Configuration tests
        print(f"{Colors.BOLD}⚙️ Configuration Tests{Colors.END}")
        self.run_test("GitHub Token Configuration", self.test_github_config_loading)
        self.run_test("Import Dependencies", self.test_import_dependencies)
        self.run_test("Dry Run Mode", self.test_dry_run_mode)
        print()
        
        # Core functionality tests
        print(f"{Colors.BOLD}🔧 Core Functionality Tests{Colors.END}")
        self.run_test("Go.mod Parser", self.test_go_mod_parser)
        self.run_test("Dependency Updater", self.test_dependency_updater)
        print()
        
        # API integration tests
        print(f"{Colors.BOLD}🌐 API Integration Tests{Colors.END}")
        self.run_test("Create Task with PR Options", self.test_create_task_with_pr)
        print()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        total = self.results["total"]
        passed = self.results["passed"]
        failed = self.results["failed"]
        
        print(f"{Colors.BOLD}📊 Test Summary{Colors.END}")
        print(f"Total Tests: {total}")
        print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
        print(f"{Colors.RED}Failed: {failed}{Colors.END}")
        
        if failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! GitHub integration is ready.{Colors.END}")
        else:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️ Some tests failed. Check the issues above.{Colors.END}")
        
        # Provide recommendations
        print(f"\n{Colors.BOLD}💡 Recommendations:{Colors.END}")
        
        if not any(test["name"] == "GitHub Token Configuration" and test["passed"] for test in self.results["tests"]):
            print("• Set GITHUB_TOKEN environment variable with your GitHub token")
        
        if not any(test["name"] == "Server Health Check" and test["passed"] for test in self.results["tests"]):
            print("• Start the backend server: python backend/main.py")
        
        if any(test["name"] == "Import Dependencies" and not test["passed"] for test in self.results["tests"]):
            print("• Install missing dependencies: pip install PyGithub==1.59.1 GitPython==3.1.40")


def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test GitHub PR integration")
    parser.add_argument("--url", default="http://localhost:8000", help="Backend server URL")
    parser.add_argument("--quick", action="store_true", help="Run only basic tests")
    
    args = parser.parse_args()
    
    tester = GitHubIntegrationTester(args.url)
    
    if args.quick:
        print("Running quick tests...")
        tester.run_test("Server Health", tester.test_server_health)
        tester.run_test("GitHub Status", tester.test_github_status_endpoint)
        tester.run_test("Dependencies", tester.test_import_dependencies)
    else:
        tester.run_all_tests()


if __name__ == "__main__":
    main() 