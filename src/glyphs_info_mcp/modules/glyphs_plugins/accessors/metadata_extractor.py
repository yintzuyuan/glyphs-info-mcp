"""
MetadataExtractor - Metadata extractor

Unified metadata extraction tool for:
- Info.plist (Plugin Bundle metadata)
- .git/config (Git repository info)
- README.md (Documentation)
"""

import configparser
import plistlib
from pathlib import Path


class MetadataExtractor:
    """Unified metadata extractor"""

    @staticmethod
    def extract_info_plist(plist_path: Path) -> dict:
        """
        Extract Info.plist file content

        Args:
            plist_path: Info.plist file path

        Returns:
            plist content dictionary, empty dict on failure
        """
        if not plist_path.exists():
            return {}

        try:
            with open(plist_path, "rb") as f:
                return plistlib.load(f)
        except Exception:
            # Return empty dict on any parsing error
            return {}

    @staticmethod
    def extract_git_config(git_config_path: Path) -> dict:
        """
        Extract Git info from .git/config file

        Args:
            git_config_path: .git/config file path

        Returns:
            Dictionary containing url and branch, empty dict on failure
        """
        if not git_config_path.exists():
            return {}

        try:
            config = configparser.ConfigParser()
            config.read(git_config_path)

            result = {}

            # Extract remote URL
            if 'remote "origin"' in config:
                result["url"] = config['remote "origin"'].get("url", "")

            # Extract branch name (prefer master, then main)
            if 'branch "master"' in config:
                result["branch"] = "master"
            elif 'branch "main"' in config:
                result["branch"] = "main"

            return result
        except Exception:
            return {}

    @staticmethod
    def extract_readme(readme_path: Path, max_length: int = 2000) -> str:
        """
        Extract README.md file content (with length limit)

        Args:
            readme_path: README.md file path
            max_length: Maximum character count (default 2000)

        Returns:
            README content, truncated with "...(truncated)" if exceeds length
        """
        if not readme_path.exists():
            return ""

        try:
            content = readme_path.read_text(encoding="utf-8")
            if len(content) > max_length:
                return content[:max_length] + "\n\n...(truncated)"
            return content
        except Exception:
            return ""
