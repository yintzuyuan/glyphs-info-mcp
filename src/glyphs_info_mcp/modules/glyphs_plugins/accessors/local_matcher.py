# encoding: utf-8
"""
Local Plugin Matcher - Matches official plugins with locally installed ones

Features:
- Scans locally installed Glyphs plugins
- Matches official registry with local plugins
- Marks installation status
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict


logger = logging.getLogger(__name__)


class LocalPluginMatcher:
    """Local plugin matcher for matching official registry with installed plugins"""

    # Glyphs plugin extension to type mapping
    PLUGIN_EXTENSIONS = {
        ".glyphsReporter": "reporter",
        ".glyphsFilter": "filter",
        ".glyphsTool": "tool",
        ".glyphsPalette": "palette",
        ".glyphsFileFormat": "fileformat",
        ".glyphsPlugin": "plugin"
    }

    def __init__(self, plugins_dir: Optional[Path] = None):
        """Initialize the matcher

        Args:
            plugins_dir: Plugin directory path (optional, defaults to standard Glyphs 3 path)
        """
        self.plugins_dir = plugins_dir or self.get_local_plugins_directory()

    def get_local_plugins_directory(self) -> Path:
        """Get local plugin directory path

        Returns:
            Standard Glyphs 3 plugin directory path
        """
        return Path.home() / "Library" / "Application Support" / "Glyphs 3" / "Plugins"

    def scan_local_plugins(self) -> List[Dict]:
        """Scan locally installed plugins

        Returns:
            List of local plugins, each containing name, path, type
        """
        if not self.plugins_dir.exists():
            logger.warning(f"Plugin directory not found: {self.plugins_dir}")
            return []

        local_plugins = []

        for item in self.plugins_dir.iterdir():
            # Check if it's a plugin (directory with correct extension)
            if not item.is_dir():
                continue

            plugin_type = self._detect_plugin_type(item.name)
            if plugin_type is None:
                continue

            local_plugins.append({
                "name": item.name,
                "path": str(item),
                "type": plugin_type
            })

        logger.info(f"Scanned {len(local_plugins)} local plugins")
        return local_plugins

    def _detect_plugin_type(self, plugin_name: str) -> Optional[str]:
        """Detect plugin type based on extension

        Args:
            plugin_name: Plugin filename (including extension)

        Returns:
            Plugin type (reporter, filter, tool, palette, fileformat, plugin)
            Returns None if not a valid plugin
        """
        for ext, plugin_type in self.PLUGIN_EXTENSIONS.items():
            if plugin_name.endswith(ext):
                return plugin_type

        return None

    def is_match(self, official_plugin: Dict, local_plugin: Dict) -> bool:
        """Check if official plugin matches local plugin

        Matching strategies:
        1. Exact name match: official["name"] == local["name"]
        2. Repository name match: local["name"] contains official["repo_name"]

        Args:
            official_plugin: Official plugin info
            local_plugin: Local plugin info

        Returns:
            Whether they match
        """
        official_name = official_plugin.get("name", "")
        local_name = local_plugin.get("name", "")

        # Strategy 1: Exact name match
        if official_name == local_name:
            return True

        # Strategy 2: Repository name match
        # Local plugin directory name may be GitHub repo_name
        # e.g., Show-Stems directory corresponds to ShowStems.glyphsReporter
        repo_name = official_plugin.get("repo_name", "")
        if repo_name:
            # Compare without extension
            local_name_base = self._remove_plugin_extension(local_name)

            # Normalize names: remove hyphens/underscores, lowercase comparison
            normalized_repo_name = repo_name.lower().replace("-", "").replace("_", "")
            normalized_local_name = local_name_base.lower().replace("-", "").replace("_", "")

            if normalized_repo_name == normalized_local_name:
                return True

            # Or local_name contains repo_name (preserve original fuzzy matching)
            if repo_name.lower() in local_name.lower():
                return True

        return False

    def _remove_plugin_extension(self, plugin_name: str) -> str:
        """Remove plugin extension from filename

        Args:
            plugin_name: Plugin filename

        Returns:
            Name with extension removed
        """
        for ext in self.PLUGIN_EXTENSIONS.keys():
            if plugin_name.endswith(ext):
                return plugin_name[:-len(ext)]

        return plugin_name

    def mark_installed_status(
        self,
        official_plugins: List[Dict],
        local_plugins: List[Dict]
    ) -> List[Dict]:
        """Mark installation status for official plugins

        Args:
            official_plugins: List of official plugins
            local_plugins: List of local plugins

        Returns:
            Marked plugin list (with installed and local_path fields added)
        """
        marked_plugins = []

        for official_plugin in official_plugins:
            # Copy plugin info (avoid modifying original data)
            plugin = official_plugin.copy()

            # Default to not installed
            plugin["installed"] = False

            # Check if there's a matching local plugin
            for local_plugin in local_plugins:
                if self.is_match(official_plugin, local_plugin):
                    plugin["installed"] = True
                    plugin["local_path"] = local_plugin["path"]
                    break

            marked_plugins.append(plugin)

        installed_count = sum(1 for p in marked_plugins if p["installed"])
        logger.info(f"Installed {installed_count}/{len(marked_plugins)} official plugins")

        return marked_plugins
