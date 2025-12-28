"""
PluginsAccessor - Local plugin accessor

Extends RepositoryScanner to identify and classify Glyphs tools:
- Plugin Bundle (.glyphsPlugin, .glyphsReporter, etc.)
- Scripts Collection (directories containing .py files)
- Python Library (Lib/ or setup.py)
"""

import logging
from dataclasses import dataclass
from pathlib import Path

from glyphs_info_mcp.modules.glyphs_plugins.accessors.metadata_extractor import MetadataExtractor
from glyphs_info_mcp.shared.core.repository_scanner import RepositoryScanner

logger = logging.getLogger(__name__)


@dataclass
class PluginInfo:
    """Plugin Bundle information"""

    name: str
    bundle_id: str
    version: str
    type: str  # Reporter, Filter, Palette, Plugin, Tool
    path: Path
    git_url: str = ""
    readme: str = ""


@dataclass
class ScriptsCollection:
    """Scripts Collection information"""

    name: str
    path: Path
    script_count: int
    scripts: list[str]
    readme: str = ""


class PluginsAccessor:
    """Local plugin accessor - extends RepositoryScanner"""

    # Plugin Bundle extensions
    PLUGIN_EXTENSIONS = [
        ".glyphsPlugin",
        ".glyphsReporter",
        ".glyphsPalette",
        ".glyphsFilter",
        ".glyphsTool",
    ]

    def __init__(self, scanner: RepositoryScanner):
        """
        Initialize PluginsAccessor

        Args:
            scanner: RepositoryScanner instance
        """
        self.scanner = scanner
        self._plugins_index: dict[str, PluginInfo] = {}
        self._scripts_index: dict[str, ScriptsCollection] = {}
        self._libraries_index: dict[str, Path] = {}

    def scan_all_tools(self) -> None:
        """Scan and classify all tools"""
        if not self.scanner.is_available():
            logger.warning("Repositories path not available")
            return

        try:
            for item in self.scanner.repositories_path.iterdir():
                if not item.is_dir() or item.name.startswith("."):
                    continue

                # Classify and extract info
                if self._is_plugin_bundle(item):
                    plugin_info = self._extract_plugin_info(item)
                    if plugin_info:
                        self._plugins_index[item.name] = plugin_info
                elif self._is_scripts_collection(item):
                    scripts_info = self._extract_scripts_info(item)
                    if scripts_info:
                        self._scripts_index[item.name] = scripts_info
                elif self._is_library(item):
                    self._libraries_index[item.name] = item

            logger.info(
                f"Scanned tools: {len(self._plugins_index)} plugins, "
                f"{len(self._scripts_index)} scripts, "
                f"{len(self._libraries_index)} libraries"
            )
        except Exception as e:
            logger.error(f"Error scanning tools: {e}")

    def _is_plugin_bundle(self, path: Path) -> bool:
        """Check if path is a Plugin Bundle (smart search)"""
        for ext in self.PLUGIN_EXTENSIONS:
            # Search for any bundle with matching extension
            if list(path.glob(f"*{ext}")):
                return True
        return False

    def _is_scripts_collection(self, path: Path) -> bool:
        """
        Check if path is a Scripts Collection

        Condition: Contains .py files and is not a Python Library
        """
        if self._is_library(path):
            return False

        # Check if contains .py files
        py_files = list(path.glob("*.py"))
        if py_files:
            return True

        # Check subdirectories for .py files (like mekkablue's categorized structure)
        for subdir in path.iterdir():
            if subdir.is_dir() and not subdir.name.startswith("."):
                if list(subdir.glob("*.py")):
                    return True

        return False

    def _is_library(self, path: Path) -> bool:
        """
        Check if path is a Python Library

        Condition: Contains Lib/ directory or setup.py
        """
        return (path / "Lib").exists() or (path / "setup.py").exists()

    def _extract_plugin_info(self, path: Path) -> PluginInfo | None:
        """Extract Plugin Bundle information"""
        try:
            # Find Bundle path
            bundle_path = self._find_bundle_path(path)
            if not bundle_path:
                return None

            # Extract Info.plist
            info_plist_path = bundle_path / "Contents" / "Info.plist"
            info_plist = MetadataExtractor.extract_info_plist(info_plist_path)

            # Extract Git info
            git_config_path = path / ".git" / "config"
            git_info = MetadataExtractor.extract_git_config(git_config_path)

            # Extract README
            readme_path = path / "README.md"
            readme = MetadataExtractor.extract_readme(readme_path)

            # Infer plugin type
            plugin_type = self._infer_plugin_type(bundle_path.suffix)

            return PluginInfo(
                name=info_plist.get("CFBundleName", path.name),
                bundle_id=info_plist.get("CFBundleIdentifier", ""),
                version=info_plist.get("CFBundleShortVersionString", ""),
                type=plugin_type,
                path=path,
                git_url=git_info.get("url", ""),
                readme=readme,
            )
        except Exception as e:
            logger.error(f"Error extracting plugin info from {path}: {e}")
            return None

    def _find_bundle_path(self, path: Path) -> Path | None:
        """Find Plugin Bundle path (smart search)"""
        for ext in self.PLUGIN_EXTENSIONS:
            bundles = list(path.glob(f"*{ext}"))
            if bundles:
                return bundles[0]  # Return first found Bundle
        return None

    def _infer_plugin_type(self, suffix: str) -> str:
        """Infer plugin type from extension"""
        type_mapping = {
            ".glyphsReporter": "Reporter",
            ".glyphsFilter": "Filter",
            ".glyphsPalette": "Palette",
            ".glyphsPlugin": "Plugin",
            ".glyphsTool": "Tool",
        }
        return type_mapping.get(suffix, "Unknown")

    def _extract_scripts_info(self, path: Path) -> ScriptsCollection | None:
        """Extract Scripts Collection information"""
        try:
            # Collect all .py files
            scripts = []

            # Root directory scripts
            scripts.extend([f.name for f in path.glob("*.py")])

            # Subdirectory scripts (one level deep)
            for subdir in path.iterdir():
                if subdir.is_dir() and not subdir.name.startswith("."):
                    scripts.extend(
                        [f"{subdir.name}/{f.name}" for f in subdir.glob("*.py")]
                    )

            # Extract README
            readme_path = path / "README.md"
            readme = MetadataExtractor.extract_readme(readme_path, max_length=500)

            return ScriptsCollection(
                name=path.name,
                path=path,
                script_count=len(scripts),
                scripts=scripts,
                readme=readme,
            )
        except Exception as e:
            logger.error(f"Error extracting scripts info from {path}: {e}")
            return None

    def get_plugin_info(self, plugin_name: str) -> PluginInfo | None:
        """
        Get specific plugin information (smart query)

        Supports the following query methods:
        1. Exact match on directory name (e.g., "variable-font-preview")
        2. Exact match on Bundle name (e.g., "Variable Font Preview X")
        3. Case-insensitive fuzzy match

        Args:
            plugin_name: Plugin name (directory name or Bundle name)

        Returns:
            PluginInfo object or None
        """
        # 1. Exact match on directory name (backward compatible)
        if plugin_name in self._plugins_index:
            return self._plugins_index[plugin_name]

        # 2. Exact match on Bundle name
        for plugin_info in self._plugins_index.values():
            if plugin_info.name == plugin_name:
                return plugin_info

        # 3. Case-insensitive fuzzy match
        plugin_name_lower = plugin_name.lower()
        for plugin_info in self._plugins_index.values():
            if plugin_info.name.lower() == plugin_name_lower:
                return plugin_info

        return None

    def get_scripts_collection(self, collection_name: str) -> ScriptsCollection | None:
        """Get specific scripts collection information"""
        return self._scripts_index.get(collection_name)

    def list_all_plugins(self) -> list[PluginInfo]:
        """List all plugins"""
        return list(self._plugins_index.values())

    def list_all_scripts(self) -> list[ScriptsCollection]:
        """List all script collections"""
        return list(self._scripts_index.values())

    def list_all_libraries(self) -> list[str]:
        """List all library names"""
        return list(self._libraries_index.keys())
