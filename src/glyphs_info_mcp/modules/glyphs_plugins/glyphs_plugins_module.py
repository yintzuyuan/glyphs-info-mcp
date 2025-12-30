"""
GlyphsPlugins Management Module
Integrates local plugin accessor and official registry for complete plugin management
"""

import sys
from pathlib import Path
from typing import Any

# Add shared core module path
shared_path = str(Path(__file__).parent.parent.parent / "src" / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from glyphs_info_mcp.shared.core.base_module import BaseMCPModule  # noqa: E402
from glyphs_info_mcp.shared.core.repository_scanner import RepositoryScanner  # noqa: E402

# Import accessors
from glyphs_info_mcp.modules.glyphs_plugins.accessors.official_registry import (  # noqa: E402
    OfficialRegistry,
)
from glyphs_info_mcp.modules.glyphs_plugins.accessors.plugins_accessor import (  # noqa: E402
    PluginsAccessor,
)
from glyphs_info_mcp.modules.glyphs_plugins.accessors.local_matcher import (  # noqa: E402
    LocalPluginMatcher,
)


class GlyphsPluginsModule(BaseMCPModule):
    """Glyphs Plugin Management Module"""

    def __init__(self) -> None:
        super().__init__(name="glyphs-plugins")
        self.description = "Glyphs.app plugins, scripts, and libraries management"

        # Core components
        self.scanner: RepositoryScanner | None = None
        self.plugins_accessor: PluginsAccessor | None = None
        self.official_registry: OfficialRegistry | None = None
        self.local_matcher: LocalPluginMatcher | None = None

        # Data path
        self.data_dir = Path(__file__).parent / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def initialize(self) -> bool:
        """
        Initialize module and create core components

        Returns:
            Whether initialization was successful
        """
        try:
            print(f"[{self.name}] Initializing Glyphs Plugins module...", file=sys.stderr)

            # Default Repositories path
            default_repos_path = (
                Path.home()
                / "Library"
                / "Application Support"
                / "Glyphs 3"
                / "Repositories"
            )

            # Initialize RepositoryScanner
            self.scanner = RepositoryScanner(repositories_path=default_repos_path)

            # Initialize PluginsAccessor
            self.plugins_accessor = PluginsAccessor(self.scanner)

            # Initialize OfficialRegistry
            self.official_registry = OfficialRegistry(cache_dir=self.data_dir)

            # Initialize LocalPluginMatcher (Phase 3)
            self.local_matcher = LocalPluginMatcher()

            # Scan local plugins (if path available)
            if self.scanner.is_available():
                print(f"[{self.name}] Scanning local plugins...", file=sys.stderr)
                self.plugins_accessor.scan_all_tools()
                plugin_count = len(self.plugins_accessor.list_all_plugins())
                scripts_count = len(self.plugins_accessor.list_all_scripts())
                print(
                    f"[{self.name}] Found {plugin_count} plugins and {scripts_count} script collections",
                    file=sys.stderr,
                )
            else:
                print(f"[{self.name}] Repositories path unavailable, only official registry search available", file=sys.stderr)

            print(f"[{self.name}] Initialization complete", file=sys.stderr)
            self.is_initialized = True
            return True

        except Exception as e:
            print(f"[{self.name}] Initialization failed: {e}", file=sys.stderr)
            return False

    def get_tools(self) -> dict[str, Any]:
        """
        Get MCP tool functions

        Returns:
            Dictionary of tool functions
        """
        return {
            "plugins_search_local": self._search_local_tool,
            "plugins_search_official": self._search_official_tool,
            "plugins_get_info": self._get_info_tool,
            "plugins_scan_repository": self._scan_repository_tool,
            "plugins_list_categories": self._list_categories_tool,
        }

    def _search_local_tool(
        self,
        query: str,
        category: str = "all"
    ) -> str:
        """
        [LOCAL] Search locally installed Glyphs plugins and scripts

        Search scope: ~/Library/Application Support/Glyphs 3/Repositories
        Supported types: Plugin Bundle, Scripts Collection, Python Library

        Output format: Compact summary (use `plugins_get_info` for full details)

        Args:
            query: Search keyword (matches name, ID, description)
            category: Type filter (all/plugin/scripts/library, default: all)

        Returns:
            Compact list of matching plugins with key info only
        """
        if not self.plugins_accessor or not self.scanner:
            return "❌ Plugin accessor not initialized"

        if not self.scanner.is_available():
            return "❌ Repositories path unavailable. Please ensure Glyphs 3 is installed."

        try:
            query_lower = query.lower()
            results: list[dict] = []

            # Search Plugin Bundles
            if category in ("all", "plugin"):
                for plugin in self.plugins_accessor.list_all_plugins():
                    if self._match_plugin(plugin, query_lower):
                        results.append({
                            "icon": "🔌",
                            "name": plugin.name,
                            "type": plugin.type,
                            "version": plugin.version,
                        })

            # Search Scripts Collections
            if category in ("all", "scripts"):
                for scripts in self.plugins_accessor.list_all_scripts():
                    if query_lower in scripts.name.lower() or (scripts.readme and query_lower in scripts.readme.lower()):
                        results.append({
                            "icon": "📜",
                            "name": scripts.name,
                            "type": "Scripts",
                            "version": f"{scripts.script_count} scripts",
                        })

            # Search Libraries
            if category in ("all", "library"):
                for lib_name in self.plugins_accessor.list_all_libraries():
                    if query_lower in lib_name.lower():
                        results.append({
                            "icon": "📚",
                            "name": lib_name,
                            "type": "Library",
                            "version": "-",
                        })

            if not results:
                return f"🔍 No local plugins found matching '{query}'"

            # Format compact output
            output = [f"🔍 **Local Search: '{query}'** - Found {len(results)} results\n"]
            output.append("| # | Type | Name | Version |")
            output.append("|---|------|------|---------|")

            for i, r in enumerate(results, 1):
                output.append(f"| {i} | {r['icon']} {r['type']} | {r['name']} | {r['version']} |")

            output.append("")
            output.append("💡 Use `plugins_get_info(name)` for full details (README, path, source code)")

            return "\n".join(output)

        except Exception as e:
            return f"❌ Search failed: {e}"

    def _match_plugin(self, plugin: Any, query: str) -> bool:
        """Check if plugin matches search criteria"""
        return (
            query in plugin.name.lower()
            or query in plugin.bundle_id.lower()
            or (plugin.readme and query in plugin.readme.lower())
        )

    def _search_official_tool(
        self,
        query: str,
        filter_by_author: str | None = None
    ) -> str:
        """
        [OFFICIAL] Search Glyphs official plugin registry

        Data source: https://github.com/schriftgestalt/glyphs-packages
        Cache mechanism: 24-hour auto-refresh
        Features: Relevance scoring, author filtering, local installation status

        Output format: Compact summary (use `plugins_get_info` for full details)

        Args:
            query: Search keyword (matches name, description)
            filter_by_author: Filter by author (optional)

        Returns:
            Compact list of official plugins with key info only
        """
        if not self.official_registry:
            return "❌ Official registry accessor not initialized"

        if not self.local_matcher:
            return "❌ Local plugin matcher not initialized"

        try:
            # Use OfficialRegistry's core_search (no limit - show all results)
            results = self.official_registry.core_search(
                query=query,
                filter_by_author=filter_by_author
            )

            if not results:
                return f"🔍 No official plugins found matching '{query}'"

            # Phase 3: Mark local installation status
            local_plugins = self.local_matcher.scan_local_plugins()
            results = self.local_matcher.mark_installed_status(results, local_plugins)

            # Format compact output
            output = []
            output.append(f"🔍 **Official Registry: '{query}'** - Found {len(results)} results\n")
            output.append("| # | Status | Name | Author | Description |")
            output.append("|---|--------|------|--------|-------------|")

            for i, plugin in enumerate(results, 1):
                status = "✅" if plugin.get("installed") else "⬜️"
                name = plugin['title'][:25] + "..." if len(plugin['title']) > 25 else plugin['title']
                author = plugin['owner'][:15] + "..." if len(plugin['owner']) > 15 else plugin['owner']
                desc = plugin['description'][:40] + "..." if plugin['description'] and len(plugin['description']) > 40 else (plugin['description'] or "-")
                output.append(f"| {i} | {status} | {name} | {author} | {desc} |")

            # Statistics
            installed_count = sum(1 for p in results if p.get("installed"))
            output.append("")
            output.append(f"📊 {installed_count}/{len(results)} installed locally")
            output.append("💡 Use `plugins_get_info(name, source='official')` for full details")

            return "\n".join(output)

        except Exception as e:
            return f"❌ Search failed: {e}"

    def _list_plugin_files(self, plugin_path: Path) -> str:
        """
        List file structure of plugin directory

        Args:
            plugin_path: Plugin directory path

        Returns:
            Markdown-formatted file list
        """
        files = []
        try:
            for item in plugin_path.rglob("*"):
                # Exclude hidden directories and files
                if any(part.startswith(".") for part in item.parts):
                    continue
                # Exclude __pycache__
                if "__pycache__" in item.parts:
                    continue

                if item.is_file():
                    relative = item.relative_to(plugin_path)
                    files.append(f"- {relative}")

            if not files:
                return "(No files)"

            return "\n".join(sorted(files))
        except Exception as e:
            return f"(Failed to read file list: {e})"

    def _get_plugin_source(
        self,
        plugin_path: Path,
        include_all_sources: bool = True,
        include_headers: bool = True,
        include_ui_files: bool = False,
        max_file_size: int = 100_000,
        max_total_size: int = 500_000,
    ) -> str:
        """
        Read plugin source code (supports Python and Objective-C)

        Args:
            plugin_path: Plugin directory path
            include_all_sources: Include all source files (default: True)
            include_headers: Include .h files (default: True)
            include_ui_files: Include .xib files (default: False, verbose)
            max_file_size: Single file size limit (100KB)
            max_total_size: Total file size limit (500KB)

        Returns:
            Markdown-formatted source code content
        """
        try:
            from glyphs_info_mcp.modules.glyphs_plugins.accessors.file_classifier import (
                FileClassifier,
            )
            from glyphs_info_mcp.modules.glyphs_plugins.accessors.source_collector import (
                SourceCollector,
            )

            # Initialize collector
            classifier = FileClassifier()
            collector = SourceCollector(
                classifier,
                max_file_size=max_file_size,
                max_total_size=max_total_size,
                include_ui_files=include_ui_files,
            )

            # Collect source files
            sources = collector.collect_source_files(plugin_path)

            if not sources:
                return "(No source files found)"

            # Format output
            output = []

            # 1. Python source code
            if "python_source" in sources and sources["python_source"]:
                output.append("### Python Source Code\n")
                for file_path in sources["python_source"]:
                    try:
                        content = file_path.read_text(encoding="utf-8")
                        relative_path = file_path.relative_to(plugin_path)
                        output.append(f"**{relative_path}**:\n")
                        output.append(f"```python\n{content}\n```\n")
                    except Exception as e:
                        output.append(
                            f"**{file_path.name}**: (Read failed: {e})\n"
                        )

            # 2. Objective-C Headers (if enabled)
            if (
                include_headers
                and "objc_header" in sources
                and sources["objc_header"]
            ):
                output.append("### Objective-C Headers\n")
                for file_path in sources["objc_header"]:
                    try:
                        content = file_path.read_text(encoding="utf-8")
                        relative_path = file_path.relative_to(plugin_path)
                        output.append(f"**{relative_path}**:\n")
                        output.append(f"```objc\n{content}\n```\n")
                    except Exception as e:
                        output.append(
                            f"**{file_path.name}**: (Read failed: {e})\n"
                        )

            # 3. Objective-C Implementation
            if "objc_impl" in sources and sources["objc_impl"]:
                output.append("### Objective-C Implementation\n")
                for file_path in sources["objc_impl"]:
                    try:
                        content = file_path.read_text(encoding="utf-8")
                        relative_path = file_path.relative_to(plugin_path)
                        output.append(f"**{relative_path}**:\n")
                        output.append(f"```objc\n{content}\n```\n")
                    except Exception as e:
                        output.append(
                            f"**{file_path.name}**: (Read failed: {e})\n"
                        )

            # 4. UI files (if enabled)
            if include_ui_files and "ui_xib" in sources and sources["ui_xib"]:
                output.append("### UI Definition Files\n")
                for file_path in sources["ui_xib"]:
                    try:
                        content = file_path.read_text(encoding="utf-8")
                        relative_path = file_path.relative_to(plugin_path)
                        output.append(f"**{relative_path}**:\n")
                        output.append(f"```xml\n{content}\n```\n")
                    except Exception as e:
                        output.append(
                            f"**{file_path.name}**: (Read failed: {e})\n"
                        )

            # 5. Binary/compiled file list
            binary_files = []
            if "binary_stub" in sources:
                binary_files.extend(sources["binary_stub"])
            if "compiled" in sources:
                binary_files.extend(sources["compiled"])

            if binary_files:
                output.append("### Binary/Compiled Files\n")
                for file_path in binary_files:
                    try:
                        file_size = file_path.stat().st_size
                        relative_path = file_path.relative_to(plugin_path)
                        file_type = classifier.get_file_category(file_path)
                        output.append(
                            f"- **{relative_path}** ({file_size:,} bytes, {file_type})\n"
                        )
                    except Exception as e:
                        output.append(f"- **{file_path.name}**: (Error: {e})\n")

            # 6. Statistics
            total_files = sum(len(files) for files in sources.values())
            output.append(f"\n---\n**Statistics**: {total_files} files total\n")

            return "".join(output)

        except Exception as e:
            return f"(Failed to read source code: {e})"

    def _get_info_tool(
        self,
        name: str,
        source: str = "local",
        include_files: bool = False,
        include_source: bool = False,
    ) -> str:
        """
        [INFO] Get plugin detailed information

        Args:
            name: Plugin name
            source: Data source (local/official, default: local)
            include_files: Include file list (default: False)
            include_source: Include plugin.py source code (default: False)

        Returns:
            Complete plugin information including metadata, README, and Git info
        """
        if source == "local":
            if not self.plugins_accessor:
                return "❌ Plugin accessor not initialized"

            plugin = self.plugins_accessor.get_plugin_info(name)
            if plugin:
                info = f"# 🔌 {plugin.name}\n\n"
                info += f"**Type**: {plugin.type}\n"
                info += f"**Version**: {plugin.version}\n"
                info += f"**Bundle ID**: {plugin.bundle_id}\n"
                info += f"**Path**: {plugin.path}\n"
                if plugin.git_url:
                    info += f"**Git Repository**: {plugin.git_url}\n"
                if plugin.readme:
                    info += f"\n## 📄 README\n\n{plugin.readme}\n"

                # Add: File list
                if include_files:
                    info += "\n## 📁 File Structure\n\n"
                    info += self._list_plugin_files(plugin.path) + "\n"

                # Add: Source code
                if include_source:
                    info += "\n## 💻 Plugin Source Code\n\n"
                    info += self._get_plugin_source(plugin.path) + "\n"

                return info

            # Try Scripts Collection
            scripts = self.plugins_accessor.get_scripts_collection(name)
            if scripts:
                info = f"# 📜 {scripts.name}\n\n"
                info += "**Type**: Scripts Collection\n"
                info += f"**Script Count**: {scripts.script_count}\n"
                info += f"**Path**: {scripts.path}\n"
                info += "\n## 📝 Script List\n\n"
                for script in scripts.scripts[:10]:  # Show max 10
                    info += f"- {script}\n"
                if len(scripts.scripts) > 10:
                    info += f"\n... and {len(scripts.scripts) - 10} more scripts\n"
                if scripts.readme:
                    info += f"\n## 📄 README\n\n{scripts.readme}\n"
                return info

            return f"❌ Local plugin not found: {name}"

        elif source == "official":
            if not self.official_registry:
                return "❌ Official registry accessor not initialized"

            results = self.official_registry.core_search(query=name)
            # Exact match (title or repo_name)
            for pkg in results:
                title = pkg.get("title", "")
                pkg_name = pkg.get("repo_name", "") or pkg.get("name", "")
                if title.lower() == name.lower() or pkg_name.lower() == name.lower():
                    display_name = title or pkg_name
                    info = f"# 📦 {display_name}\n\n"
                    if pkg.get("repo_name"):
                        info += f"**Repository Name**: {pkg['repo_name']}\n"
                    info += f"**Description**: {pkg.get('description', 'No description')}\n"
                    info += f"**Repository**: {pkg.get('url', 'N/A')}\n"
                    if pkg.get("screenshot"):
                        info += f"**Screenshot**: {pkg['screenshot']}\n"
                    return info

            return f"❌ Official plugin not found: {name}"

        else:
            return f"❌ Invalid data source: {source} (please use local or official)"

    def _scan_repository_tool(self) -> str:
        """
        [SCAN] Scan Repositories directory and update index

        Re-scan ~/Library/Application Support/Glyphs 3/Repositories
        Update local plugins, scripts, and libraries index

        Returns:
            Scan results summary
        """
        if not self.plugins_accessor or not self.scanner:
            return "❌ Plugin accessor not initialized"

        if not self.scanner.is_available():
            return "❌ Repositories path unavailable"

        try:
            self.plugins_accessor.scan_all_tools()

            plugin_count = len(self.plugins_accessor.list_all_plugins())
            scripts_count = len(self.plugins_accessor.list_all_scripts())
            library_count = len(self.plugins_accessor.list_all_libraries())

            result = "# 📂 Repositories Scan Complete\n\n"
            result += f"**Path**: {self.scanner.repositories_path}\n\n"
            result += "## Statistics\n\n"
            result += f"- 🔌 Plugin Bundles: {plugin_count}\n"
            result += f"- 📜 Scripts Collections: {scripts_count}\n"
            result += f"- 📚 Python Libraries: {library_count}\n"

            return result

        except Exception as e:
            return f"❌ Scan failed: {e}"

    def _list_categories_tool(self) -> str:
        """
        [LIST] List all plugin types and statistics

        Display local plugin category statistics:
        - Plugin type distribution (Reporter, Filter, Palette, etc.)
        - Scripts Collections list
        - Libraries list

        Returns:
            Category statistics report
        """
        if not self.plugins_accessor:
            return "❌ Plugin accessor not initialized"

        try:
            # Count Plugin types
            plugins = self.plugins_accessor.list_all_plugins()
            type_counts: dict[str, int] = {}
            for plugin in plugins:
                type_counts[plugin.type] = type_counts.get(plugin.type, 0) + 1

            # List Scripts Collections
            scripts = self.plugins_accessor.list_all_scripts()

            # List Libraries
            libraries = self.plugins_accessor.list_all_libraries()

            result = "# 📊 Plugin Category Statistics\n\n"

            # Plugin types
            if type_counts:
                result += "## 🔌 Plugin Bundles\n\n"
                for ptype, count in sorted(
                    type_counts.items(), key=lambda x: x[1], reverse=True
                ):
                    result += f"- **{ptype}**: {count}\n"
                result += "\n"

            # Scripts Collections
            if scripts:
                result += f"## 📜 Scripts Collections ({len(scripts)})\n\n"
                for sc in scripts[:10]:  # Show max 10
                    result += f"- {sc.name} ({sc.script_count} scripts)\n"
                if len(scripts) > 10:
                    result += f"\n... and {len(scripts) - 10} more collections\n"
                result += "\n"

            # Libraries
            if libraries:
                result += f"## 📚 Python Libraries ({len(libraries)})\n\n"
                for lib_name in libraries[:10]:  # Show max 10
                    result += f"- {lib_name}\n"
                if len(libraries) > 10:
                    result += f"\n... and {len(libraries) - 10} more libraries\n"

            return result

        except Exception as e:
            return f"❌ Failed to list categories: {e}"

    def get_module_info(self) -> dict[str, Any]:
        """
        Get module information

        Returns:
            Module information dictionary
        """
        return {
            "name": self.name,
            "description": self.description,
            "version": "1.0.0",
            "tools": list(self.get_tools().keys()),
            "data_sources": {
                "local": (
                    str(self.scanner.repositories_path)
                    if self.scanner and self.scanner.is_available()
                    else "N/A"
                ),
                "official": "https://github.com/schriftgestalt/glyphs-packages",
            },
        }
