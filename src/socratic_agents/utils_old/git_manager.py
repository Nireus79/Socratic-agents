"""Git Repository Manager - Handles GitHub repository operations"""

import logging
import os
import re
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class GitRepositoryManager:
    """Manages GitHub repository operations with security and isolation"""

    GITHUB_DOMAINS = ["github.com", "www.github.com"]
    TEMP_PREFIX = "socrates_clone_"
    CLONE_TIMEOUT = 300
    PUSH_PULL_TIMEOUT = 300

    def __init__(self, temp_base_dir: Optional[str] = None, github_token: Optional[str] = None):
        self.temp_base_dir = temp_base_dir or tempfile.gettempdir()
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.logger = logging.getLogger(__name__)

    def validate_github_url(self, url: str) -> Dict[str, Any]:
        """Validate GitHub URL format and extract metadata"""
        if not url or not isinstance(url, str):
            return {
                "valid": False,
                "owner": None,
                "repo": None,
                "url": url,
                "message": "URL cannot be empty",
            }

        url = url.strip()

        https_pattern = r"https://github\.com/([a-zA-Z0-9_-]+)/([a-zA-Z0-9._-]+?)(?:\.git)?/?$"
        match = re.match(https_pattern, url)
        if match:
            owner, repo = match.groups()
            return {
                "valid": True,
                "owner": owner,
                "repo": repo,
                "url": url,
                "message": "Valid GitHub URL",
            }

        ssh_pattern = r"git@github\.com:([a-zA-Z0-9_-]+)/([a-zA-Z0-9._-]+?)(?:\.git)?/?$"
        match = re.match(ssh_pattern, url)
        if match:
            owner, repo = match.groups()
            return {
                "valid": True,
                "owner": owner,
                "repo": repo,
                "url": url,
                "message": "Valid GitHub SSH URL",
            }

        return {
            "valid": False,
            "owner": None,
            "repo": None,
            "url": url,
            "message": f"Invalid GitHub URL format: {url}",
        }

    def clone_repository(self, url: str) -> Optional[str]:
        """Clone a GitHub repository to a temporary directory"""
        validation = self.validate_github_url(url)
        if not validation["valid"]:
            self.logger.error(f"Invalid GitHub URL: {validation['message']}")
            return None

        try:
            clone_dir = os.path.join(
                self.temp_base_dir,
                f"{self.TEMP_PREFIX}{uuid.uuid4().hex[:8]}",
            )
            os.makedirs(clone_dir, exist_ok=True)

            clone_url = url
            if self.github_token and url.startswith("https://github.com"):
                clone_url = url.replace(
                    "https://github.com",
                    f"https://x-access-token:{self.github_token}@github.com",
                )

            subprocess.run(
                ["git", "clone", clone_url, clone_dir],
                timeout=self.CLONE_TIMEOUT,
                capture_output=True,
                check=True,
            )

            self.logger.info(f"Successfully cloned repository to {clone_dir}")
            return clone_dir

        except subprocess.TimeoutExpired:
            self.logger.error(f"Git clone timed out for {url}")
            return None
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git clone failed for {url}: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to clone repository: {str(e)}")
            return None

    def cleanup_clone(self, clone_path: str) -> bool:
        """Safely remove a cloned repository"""
        try:
            if os.path.exists(clone_path):
                shutil.rmtree(clone_path)
                self.logger.debug(f"Cleaned up clone directory: {clone_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to cleanup clone directory: {str(e)}")
            return False
