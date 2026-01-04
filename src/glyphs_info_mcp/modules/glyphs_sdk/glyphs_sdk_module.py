"""
GlyphsSDK Search Module
Integrates SDK content indexing, search, and formatting functionality
"""

import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

# Add shared core module path
shared_path = str(Path(__file__).parent.parent.parent / "src" / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

# Dynamically import other SDK modules (avoid relative import issues)
import importlib.util

from glyphs_info_mcp.shared.core.base_module import BaseMCPModule
from glyphs_info_mcp.shared.core.sdk_native_accessor import SDKNativeAccessor
from glyphs_info_mcp.shared.core.plugin_templates_resources import (
    PluginTemplatesResourceManager,
)
from glyphs_info_mcp.shared.core.xcode_templates_resources import (
    XcodeTemplatesResourceManager,
)
from glyphs_info_mcp.shared.core.python_samples_resources import (
    PythonSamplesResourceManager,
)
from glyphs_info_mcp.shared.core.xcode_samples_resources import (
    XcodeSamplesResourceManager,
)


def _import_sdk_module(module_name: str) -> ModuleType:
    """Dynamically import SDK submodule"""
    module_file = Path(__file__).parent / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, module_file)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module {module_name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Import SDK submodules
_indexer_module = _import_sdk_module("sdk_indexer")
_searcher_module = _import_sdk_module("sdk_searcher")
_formatter_module = _import_sdk_module("sdk_formatter")

SDKIndexer: type[Any] = _indexer_module.SDKIndexer
SDKSearcher: type[Any] = _searcher_module.SDKSearcher
SDKResultFormatter: type[Any] = _formatter_module.SDKResultFormatter


class GlyphsSDKModule(BaseMCPModule):
    """Glyphs SDK search module"""

    def __init__(self) -> None:
        super().__init__(name="glyphs-sdk")
        self.description = "Glyphs SDK code and development guide search"

        # SDK path settings
        self.sdk_path = (
            Path(__file__).parent.parent.parent / "data" / "official" / "GlyphsSDK"
        )
        self.index_file = Path(__file__).parent / "data" / "sdk_index.json"

        # Core components
        self.indexer: Any = None
        self.searcher: Any = None
        self.formatter = SDKResultFormatter()
        self.index: dict[str, list[dict[str, Any]]] = {}

        # Native Accessor (for Xcode resource access)
        self.native_accessor: SDKNativeAccessor | None = None

        # Plugin Templates Manager (Issue #33)
        self.templates_manager: PluginTemplatesResourceManager | None = None

        # Xcode Templates Manager (Issue #34)
        self.xcode_templates_manager: XcodeTemplatesResourceManager | None = None

        # Python Samples Manager (Issue #37)
        self.python_samples_manager: PythonSamplesResourceManager | None = None

        # Xcode Samples Manager (Issue #37)
        self.xcode_samples_manager: XcodeSamplesResourceManager | None = None

    def initialize(self) -> bool:
        """
        Initialize module, build or load index

        Returns:
            Whether initialization was successful
        """
        try:
            self.indexer = SDKIndexer(self.sdk_path)

            # Check if index needs to be rebuilt
            if self._needs_rebuild_index():
                print(f"[{self.name}] Building SDK content index...", file=sys.stderr)
                self._build_and_save_index()
            else:
                print(f"[{self.name}] Loading existing SDK index...", file=sys.stderr)
                self._load_index()

            # Initialize searcher
            self.searcher = SDKSearcher(self.index)

            # Load actual file contents into index
            self._load_file_contents()

            # Initialize Native Accessor (for Xcode resources)
            self.native_accessor = SDKNativeAccessor(self.sdk_path)

            # Initialize Plugin Templates Manager (Issue #33)
            try:
                self.templates_manager = PluginTemplatesResourceManager(self.sdk_path)
                template_count = len(self.templates_manager.get_templates())
                print(
                    f"[{self.name}] Loaded {template_count} Python templates as resources",
                    file=sys.stderr,
                )
            except Exception as e:
                print(
                    f"[{self.name}] Warning: Failed to initialize Python templates manager: {e}",
                    file=sys.stderr,
                )
                self.templates_manager = None

            # Initialize Xcode Templates Manager (Issue #34)
            try:
                self.xcode_templates_manager = XcodeTemplatesResourceManager(
                    self.sdk_path
                )
                xcode_template_count = len(self.xcode_templates_manager.get_templates())
                print(
                    f"[{self.name}] Loaded {xcode_template_count} Xcode templates as resources",
                    file=sys.stderr,
                )
            except Exception as e:
                print(
                    f"[{self.name}] Warning: Failed to initialize Xcode templates manager: {e}",
                    file=sys.stderr,
                )
                self.xcode_templates_manager = None

            # Initialize Python Samples Manager (Issue #37)
            try:
                self.python_samples_manager = PythonSamplesResourceManager(
                    self.sdk_path
                )
                python_sample_count = len(self.python_samples_manager.get_samples())
                print(
                    f"[{self.name}] Loaded {python_sample_count} Python samples as resources",
                    file=sys.stderr,
                )
            except Exception as e:
                print(
                    f"[{self.name}] Warning: Failed to initialize Python samples manager: {e}",
                    file=sys.stderr,
                )
                self.python_samples_manager = None

            # Initialize Xcode Samples Manager (Issue #37)
            try:
                self.xcode_samples_manager = XcodeSamplesResourceManager(self.sdk_path)
                xcode_sample_count = len(self.xcode_samples_manager.get_samples())
                print(
                    f"[{self.name}] Loaded {xcode_sample_count} Xcode samples as resources",
                    file=sys.stderr,
                )
            except Exception as e:
                print(
                    f"[{self.name}] Warning: Failed to initialize Xcode samples manager: {e}",
                    file=sys.stderr,
                )
                self.xcode_samples_manager = None

            print(
                f"[{self.name}] Initialization complete - indexed {self._count_total_items()} SDK items",
                file=sys.stderr,
            )
            return True

        except Exception as e:
            print(f"[{self.name}] Initialization failed: {e}", file=sys.stderr)
            return False

    def core_search(
        self, query: str, max_results: int = 5, **kwargs: Any
    ) -> list[dict[str, Any]]:
        """
        Core search functionality

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of search results
        """
        if not self.searcher:
            return []

        return self.searcher.search(query, max_results)

    def get_tools(self) -> dict[str, Any]:
        """
        Get MCP tool functions

        Returns:
            Dictionary of tool functions
        """
        return {
            "sdk_search_content": self._sdk_search_tool,
            "sdk_get_content": self._fetch_sdk_content_tool,
            "sdk_list_xcode_templates": self._list_xcode_templates_by_native_tool,
            "sdk_get_xcode_template": self._get_xcode_template_by_name_tool,
            "sdk_list_xcode_samples": self._list_xcode_samples_tool,
            "sdk_get_xcode_sample": self._get_xcode_sample_tool,
            # Python Templates Tools (Issue #33)
            "sdk_list_python_templates": self._list_python_templates_tool,
            "sdk_get_python_template": self._get_python_template_tool,
        }

    def _sdk_search_tool(self, query: str, max_results: int = 5) -> str:
        """
        [SDK] Search official development guides, documentation, and tutorials

        Purpose: Find development guides, README files, and tutorials (excludes code templates)
        Content types: Development guides, README files, usage instructions, implementation tutorials
        Complementary tools:
          - Use `python_api_search` to view API specifications and correct usage
          - Code templates are now provided as MCP resources (avoiding content overlap)

        When to use:
        - Need to understand basic concepts and workflow of plugin development
        - View official development guides and documentation
        - Learn development methods for different plugin types
        - Understand SDK overall architecture and usage

        Important changes:
        - Python Templates code samples have been moved to MCP resource system
        - This tool focuses on documentation content, avoiding duplication with code templates

        Args:
            query: Search keyword or feature description
            max_results: Maximum number of results (default: 5)

        Returns:
            Formatted development guide search results with related tool recommendations
        """
        if not query:
            return "Please provide a search keyword"

        # Execute search
        results = self.core_search(query, max_results)

        # Format results
        formatted_result = self.formatter.format_results(results, query)

        # Add related tool recommendations
        formatted_result += self._add_cross_references(query)

        return formatted_result

    def _add_cross_references(self, query: str) -> str:
        """Add related tool recommendations"""
        cross_ref = "\n\n## 🔗 Related Resources\n"
        cross_ref += f'📚 **View API specs**: Use `python_api_search "{query}"` to confirm correct API usage and parameters\n'
        cross_ref += "💡 **More learning resources**:\n"
        cross_ref += f'  - Use `handbook_search "{query}"` to view official handbook documentation\n'
        cross_ref += f'  - Use `web_search_forum "{query}"` to view community discussions and Q&A\n'
        return cross_ref

    def _fetch_sdk_content_tool(self, file_path: str) -> str:
        """
        Get complete content of a specific SDK file

        Args:
            file_path: Relative file path (relative to GlyphsSDK root directory)

        Returns:
            File content
        """
        if not file_path:
            return "Please provide a file path"

        try:
            full_path = self.sdk_path / file_path

            if not full_path.exists():
                return f"File not found: {file_path}"

            # Read file content
            content = full_path.read_text(encoding="utf-8")

            # Format display
            return f"📄 **{file_path}**\n\n```{'python' if file_path.endswith('.py') else 'markdown' if file_path.endswith('.md') else 'text'}\n{content}\n```"

        except Exception as e:
            return f"Error reading file: {e}"

    async def handle_tool_call(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """
        Handle tool call

        Args:
            tool_name: Tool name
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        if tool_name == "sdk_search_content":
            return self._handle_sdk_search(arguments)
        elif tool_name == "sdk_get_content":
            return self._handle_fetch_content(arguments)
        else:
            return f"Unknown tool: {tool_name}"

    def _handle_sdk_search(self, arguments: dict[str, Any]) -> str:
        """Handle SDK search"""
        query = arguments.get("query", "")
        max_results = arguments.get("max_results", 10)

        if not query:
            return "Please provide a search keyword"

        # Execute search
        results = self.core_search(query, max_results)

        # Format results
        return self.formatter.format_results(results, query)

    def _handle_fetch_content(self, arguments: dict[str, Any]) -> str:
        """Handle file content fetch"""
        file_path = arguments.get("file_path", "")

        if not file_path:
            return "Please provide a file path"

        try:
            full_path = self.sdk_path / file_path

            if not full_path.exists():
                return f"File not found: {file_path}"

            # Read file content
            content = full_path.read_text(encoding="utf-8")

            # Format display
            return f"📄 **{file_path}**\n\n```{'python' if file_path.endswith('.py') else 'markdown' if file_path.endswith('.md') else 'text'}\n{content}\n```"

        except Exception as e:
            return f"Error reading file: {e}"

    def _needs_rebuild_index(self) -> bool:
        """Check if index needs to be rebuilt"""
        if not self.index_file.exists():
            return True

        # Can add more complex logic, such as checking SDK directory modification time
        return False

    def _build_and_save_index(self) -> None:
        """Build and save index"""
        if self.indexer is None:
            return
        self.index = self.indexer.build_index()

        # Ensure data directory exists
        self.index_file.parent.mkdir(parents=True, exist_ok=True)

        # Save index
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)

    def _load_index(self) -> None:
        """Load existing index"""
        with open(self.index_file, encoding="utf-8") as f:
            self.index = json.load(f)

    def _load_file_contents(self) -> None:
        """Load file contents into index

        Paths in index are relative, need to combine with sdk_path to get absolute path
        """
        total_loaded = 0
        total_failed = 0

        for category_name, category_items in self.index.items():
            for item in category_items:
                try:
                    # Index stores relative paths, need to convert to absolute paths
                    relative_path = item["path"]
                    file_path = self.sdk_path / relative_path

                    if file_path.exists():
                        content = file_path.read_text(encoding="utf-8")
                        # Only save first 1000 characters for search
                        item["content"] = content[:1000]
                        total_loaded += 1
                    else:
                        print(f"[{self.name}] File not found: {file_path}", file=sys.stderr)
                        item["content"] = ""
                        total_failed += 1
                except Exception as e:
                    print(f"[{self.name}] Failed to read file {item['path']}: {e}", file=sys.stderr)
                    item["content"] = ""
                    total_failed += 1

        print(f"[{self.name}] Content loading complete: {total_loaded} succeeded, {total_failed} failed", file=sys.stderr)

    def _count_total_items(self) -> int:
        """Count total items in index"""
        return sum(len(items) for items in self.index.values())

    def get_available_sources(self) -> list[str]:
        """Get available search sources"""
        return list(self.index.keys())

    def get_source_stats(self) -> dict[str, int]:
        """Get statistics for each source"""
        return {source: len(items) for source, items in self.index.items()}

    def get_module_info(self) -> dict[str, Any]:
        """Get module information"""
        capabilities = [
            "SDK code search",
            "Development guide query",
            "Example code search",
            "Plugin template search",
            "File content retrieval",
            "Xcode template query",
            "Xcode sample project access",
        ]

        return {
            "name": self.name,
            "description": self.description,
            "version": "1.0.0",
            "type": "search",
            "sources": self.get_available_sources(),
            "total_items": self._count_total_items(),
            "search_types": ["code", "guide", "example", "template", "xcode"],
            "capabilities": capabilities,
        }

    # ============================================================================
    # Xcode resource tool methods
    # ============================================================================

    def _list_xcode_templates_by_native_tool(self) -> str:
        """
        [SDK] List all Xcode plugin templates (legacy native API)

        DEPRECATED: Use _list_xcode_templates_tool for the new resource-based API.
        This method is kept for backward compatibility with the old API.

        Display available Objective-C plugin development templates for advanced developers using Xcode.
        These templates use Objective-C language and require Xcode development environment.

        Template types:
        - Reporter Plugin: Visualization helper tools
        - Filter Plugin: Font effect processors
        - Tool Plugin: Custom editing tools
        - Palette Plugin: Sidebar panels
        - File Format Plugin: Custom file format support

        Related resources:
        - Use api_search_objc_headers to view Objective-C protocol definitions
        - Use sdk_list_xcode_samples to view complete sample projects

        Returns:
            Xcode template list with template name, type, and description
        """
        if not self.native_accessor:
            return "❌ Native Accessor not initialized"

        try:
            templates = self.native_accessor.list_xcode_templates()

            if not templates:
                return "No Xcode templates found"

            result = "## 📱 Xcode Plugin Template List\n\n"
            result += f"Found {len(templates)} Objective-C plugin templates\n\n"

            for template in templates:
                result += f"### {template['name']}\n"
                result += f"- **Type**: {template['type']}\n"
                result += f"- **File count**: {template['file_count']}\n"
                if template.get("description"):
                    result += f"- **Description**: {template['description']}\n"
                result += f"- **Path**: `{template['path']}`\n\n"

            result += "\n💡 **Usage tips**:\n"
            result += "- Use `sdk_get_xcode_template` to view specific template's complete code\n"
            result += (
                "- Use `api_search_objc_headers` to view related Objective-C protocol definitions\n"
            )

            return result

        except Exception as e:
            return f"❌ Error listing Xcode templates: {e}"

    def _get_xcode_template_by_name_tool(self, template_name: str) -> str:
        """
        [SDK] Get complete content of a specific Xcode template (legacy API)

        DEPRECATED: Use _get_xcode_template_tool with template_id instead.
        This method is kept for backward compatibility with the old API.

        Retrieve Xcode template file structure and source code, including:
        - .h header files
        - .m implementation files
        - .plist configuration files
        - .xib interface files (if available)

        Args:
            template_name: Template name (e.g., "Glyphs Reporter" or "Glyphs Filter Plugin")

        Returns:
            Template file structure and main source code
        """
        if not self.native_accessor:
            return "❌ Native Accessor not initialized"

        if not template_name:
            return "Please provide a template name"

        try:
            template = self.native_accessor.get_xcode_template(template_name)

            if not template:
                available = self.native_accessor.list_xcode_templates()
                names = [t["name"] for t in available]
                return f"❌ Template not found: {template_name}\n\nAvailable templates:\n" + "\n".join(
                    f"- {n}" for n in names
                )

            result = f"## 📱 {template['name']}\n\n"
            result += f"**Type**: {template['type']}\n"
            if template.get("description"):
                result += f"**Description**: {template['description']}\n"
            result += f"\n### 📁 File Structure ({template['file_count']} files)\n\n"

            # List all files
            for file_info in template["files"]:
                result += f"- `{file_info['path']}`\n"

            # Show main source code
            result += "\n### 💻 Main Source Code\n\n"
            source_files = template.get("source_files", {})

            for file_path, content in source_files.items():
                ext = Path(file_path).suffix
                lang = (
                    "objective-c"
                    if ext in [".h", ".m"]
                    else "xml" if ext == ".plist" else "text"
                )
                result += f"#### `{file_path}`\n\n"
                result += f"```{lang}\n{content}\n```\n\n"

            return result

        except Exception as e:
            return f"❌ Error getting Xcode template: {e}"

    def _list_xcode_samples_tool(self) -> str:
        """
        [SDK] List all Xcode sample projects

        Display available complete Xcode sample projects, each is a compilable and runnable plugin.
        These samples demonstrate implementation approaches and best practices for different plugin types.

        Sample types:
        - UI integration samples (custom parameter panels, inspector panels)
        - Window management samples (standalone window plugins)
        - Special feature samples (photo fonts, etc.)

        Related resources:
        - Use sdk_get_xcode_sample to view the complete code of a specific sample
        - Use api_search_objc_headers to view API definitions used

        Returns:
            Sample project list with name, feature description, and main files
        """
        if not self.native_accessor:
            return "❌ Native Accessor not initialized"

        try:
            samples = self.native_accessor.list_xcode_samples()

            if not samples:
                return "No Xcode sample projects found"

            result = "## 🎯 Xcode Sample Project List\n\n"
            result += f"Found {len(samples)} complete sample projects\n\n"

            for sample in samples:
                result += f"### {sample['name']}\n"
                result += f"- **Xcode Project**: {'✅ Yes' if sample['has_xcode_project'] else '❌ No'}\n"
                result += f"- **Source files**: {sample['source_file_count']}\n"

                if sample.get("readme"):
                    # Only show first 200 characters of README
                    readme_preview = sample["readme"][:200].strip()
                    result += f"- **Description**: {readme_preview}{'...' if len(sample['readme']) > 200 else ''}\n"

                result += f"- **Path**: `{sample['path']}`\n\n"

            result += "\n💡 **Usage tips**:\n"
            result += "- Use `sdk_get_xcode_sample` to view specific sample's complete code\n"
            result += "- These samples can be opened and compiled directly in Xcode\n"

            return result

        except Exception as e:
            return f"❌ Error listing Xcode samples: {e}"

    def _get_xcode_sample_tool(self, sample_name: str) -> str:
        """
        [SDK] Get complete information of a specific Xcode sample

        Retrieves complete content of Xcode sample project, including:
        - README documentation
        - Complete source code files (.h, .m)
        - Project structure information

        Args:
            sample_name: Sample name (e.g., "InspectorDemo" or "Plugin With Window")

        Returns:
            Sample documentation, file structure, and main source code
        """
        if not self.native_accessor:
            return "❌ Native Accessor not initialized"

        if not sample_name:
            return "Please provide a sample name"

        try:
            sample = self.native_accessor.get_xcode_sample(sample_name)

            if not sample:
                available = self.native_accessor.list_xcode_samples()
                names = [s["name"] for s in available]
                return f"❌ Sample not found: {sample_name}\n\nAvailable samples:\n" + "\n".join(
                    f"- {n}" for n in names
                )

            result = f"## 🎯 {sample['name']}\n\n"
            result += f"**Xcode Project**: {'✅ Yes' if sample['has_xcode_project'] else '❌ No'}\n"
            result += f"**Source files**: {sample['source_file_count']}\n\n"

            # Show README
            if sample.get("readme"):
                result += "### 📖 README\n\n"
                result += f"{sample['readme']}\n\n"

            # List source files
            result += f"### 📁 Source Files ({sample['source_file_count']})\n\n"
            for file_info in sample["source_files"]:
                result += f"- `{file_info['path']}`\n"

            # Show source code content
            result += "\n### 💻 Source Code\n\n"
            source_code = sample.get("source_code", {})

            for file_path, content in source_code.items():
                ext = Path(file_path).suffix
                lang = "objective-c" if ext in [".h", ".m"] else "text"
                result += f"#### `{file_path}`\n\n"
                result += f"```{lang}\n{content}\n```\n\n"

            return result

        except Exception as e:
            return f"❌ Error getting Xcode sample: {e}"

    # ============================================================================
    # Python Samples Tools (Issue #38)
    # ============================================================================

    def _list_python_samples_tool(self) -> str:
        """
        [SDK] List all Python sample plugins

        Display available Python sample plugins demonstrating various plugin types
        and implementation patterns. Samples include complete working code.

        Sample types:
        - Script samples (standalone Python scripts)
        - Plugin samples (.glyphsPlugin bundles)
        - Palette samples (.glyphsPalette bundles)
        - Tool samples (.glyphsTool bundles)

        Related resources:
        - Use sdk(action="get_python_sample") to view specific sample's complete code
        - Use api(action="search_python") to view API definitions used

        Returns:
            Sample list with name, type, and file information
        """
        if not self.native_accessor:
            return "❌ Native Accessor not initialized"

        try:
            samples = self.native_accessor.list_python_samples()

            if not samples:
                return "No Python sample plugins found"

            result = "## 🐍 Python Sample Plugin List\n\n"
            result += f"Found {len(samples)} sample plugins\n\n"

            for sample in samples:
                result += f"### {sample['name']}\n"
                result += f"- **Type**: {sample['type']}\n"
                result += f"- **Bundle**: {'✅ Yes' if sample['has_bundle'] else '❌ No (standalone script)'}\n"
                result += f"- **Source files**: {sample['source_file_count']}\n"

                if sample.get("readme"):
                    # Only show first 200 characters of README
                    readme_preview = sample["readme"][:200].strip()
                    result += f"- **Description**: {readme_preview}{'...' if len(sample['readme']) > 200 else ''}\n"

                result += f"- **Path**: `{sample['path']}`\n\n"

            result += "\n💡 **Usage tips**:\n"
            result += "- Use `sdk(action=\"get_python_sample\", sample_name=\"...\")` to view specific sample's complete code\n"
            result += "- Bundle samples can be installed directly to ~/Library/Application Support/Glyphs 3/Plugins/\n"
            result += "- Standalone scripts can be run from Script menu or used as reference\n"

            return result

        except Exception as e:
            return f"❌ Error listing Python samples: {e}"

    def _get_python_sample_tool(self, sample_name: str) -> str:
        """
        [SDK] Get complete information of a specific Python sample

        Retrieves complete content of Python sample plugin, including:
        - README documentation
        - Complete Python source code files
        - Plugin structure information

        Args:
            sample_name: Sample name (e.g., "Plugin With Window" or "Callback for context menu")

        Returns:
            Sample documentation, file structure, and complete source code
        """
        if not self.native_accessor:
            return "❌ Native Accessor not initialized"

        if not sample_name:
            return "Please provide a sample name"

        try:
            sample = self.native_accessor.get_python_sample(sample_name)

            if not sample:
                available = self.native_accessor.list_python_samples()
                names = [s["name"] for s in available]
                return f"❌ Sample not found: {sample_name}\n\nAvailable samples:\n" + "\n".join(
                    f"- {n}" for n in names
                )

            result = f"## 🐍 {sample['name']}\n\n"
            result += f"**Type**: {sample['type']}\n"
            result += f"**Bundle**: {'✅ Yes' if sample['has_bundle'] else '❌ No (standalone script)'}\n"
            result += f"**Source files**: {sample['source_file_count']}\n\n"

            # Show README
            if sample.get("readme"):
                result += "### 📖 README\n\n"
                result += f"{sample['readme']}\n\n"

            # List source files
            result += f"### 📁 Source Files ({sample['source_file_count']})\n\n"
            for file_info in sample["source_files"]:
                result += f"- `{file_info['path']}`\n"

            # Show source code content
            result += "\n### 💻 Source Code\n\n"
            source_code = sample.get("source_code", {})

            for file_path, content in source_code.items():
                result += f"#### `{file_path}`\n\n"
                result += f"```python\n{content}\n```\n\n"

            # Show load errors if any
            if sample.get("partial_load"):
                load_errors = sample.get("load_errors", [])
                result += "### ⚠️ Load Warnings\n\n"
                result += "Some files could not be loaded:\n\n"
                for error in load_errors:
                    result += f"- `{error['file']}`: {error['error']}\n"
                result += "\n"

            return result

        except Exception as e:
            return f"❌ Error getting Python sample: {e}"

    # ============================================================================
    # MCP Resources Implementation (Issue #33)
    # ============================================================================

    def get_resources(self) -> dict[str, Callable]:
        """Get MCP resources provided by SDK module

        Returns dictionary of resource URIs mapped to handler functions that
        provide Python and Xcode plugin templates as MCP resources.

        Resource URI formats:
        - Python: glyphs://plugin-template/{template_id}
        - Xcode: glyphs://xcode-template/{template_id}

        Examples:
        - glyphs://plugin-template/filter_without_dialog
        - glyphs://xcode-template/reporter

        Returns:
            Dictionary of resource URI -> callable mapping

        Note:
            - Each template gets its own resource URI
            - Handlers are closures that capture template_id
            - Returns empty dict if managers not initialized
        """
        resources = {}

        # Python Templates Resources (Issue #33)
        if self.templates_manager:
            python_templates = self.templates_manager.get_templates()
            for template_id in python_templates:
                uri = f"glyphs://plugin-template/{template_id}"

                # Create closure to capture template_id (avoid late binding)
                def make_resource_handler(tid: str) -> Callable[[], str]:
                    def resource_handler() -> str:
                        return self._get_template_resource(tid)
                    resource_handler.__name__ = f"get_template_{tid}"
                    return resource_handler

                resources[uri] = make_resource_handler(template_id)

        # Xcode Templates Resources (Issue #34)
        if self.xcode_templates_manager:
            xcode_templates = self.xcode_templates_manager.get_templates()
            for template_id in xcode_templates:
                uri = f"glyphs://xcode-template/{template_id}"

                # Create closure to capture template_id (avoid late binding)
                def make_xcode_resource_handler(tid: str) -> Callable[[], str]:
                    def resource_handler() -> str:
                        return self._get_xcode_template_resource(tid)
                    resource_handler.__name__ = f"get_xcode_template_{tid}"
                    return resource_handler

                resources[uri] = make_xcode_resource_handler(template_id)

        # Python Samples Resources (Issue #37)
        if self.python_samples_manager:
            python_samples = self.python_samples_manager.get_samples()
            for sample_id in python_samples:
                uri = f"glyphs://python-sample/{sample_id}"

                # Create closure to capture sample_id (avoid late binding)
                def make_python_sample_handler(sid: str) -> Callable[[], str]:
                    def resource_handler() -> str:
                        return self._get_python_sample_resource(sid)
                    resource_handler.__name__ = f"get_python_sample_{sid}"
                    return resource_handler

                resources[uri] = make_python_sample_handler(sample_id)

        # Xcode Samples Resources (Issue #37)
        if self.xcode_samples_manager:
            xcode_samples = self.xcode_samples_manager.get_samples()
            for sample_id in xcode_samples:
                uri = f"glyphs://xcode-sample/{sample_id}"

                # Create closure to capture sample_id (avoid late binding)
                def make_xcode_sample_handler(sid: str) -> Callable[[], str]:
                    def resource_handler() -> str:
                        return self._get_xcode_sample_resource(sid)
                    resource_handler.__name__ = f"get_xcode_sample_{sid}"
                    return resource_handler

                resources[uri] = make_xcode_sample_handler(sample_id)

        print(
            f"[{self.name}] Prepared {len(resources)} resources (templates + samples)",
            file=sys.stderr,
        )
        return resources

    def _get_template_resource(self, template_id: str) -> str:
        """Internal handler to get template resource content

        Formats template as Markdown with code block for MCP resource display.

        Args:
            template_id: Template identifier (e.g., "filter_without_dialog")

        Returns:
            Formatted template content with metadata and usage instructions
        """
        if not self.templates_manager:
            return "❌ Templates manager not initialized"

        template = self.templates_manager.get_template_by_id(template_id)
        if not template:
            return f"❌ Template not found: {template_id}"

        # Format template as MCP resource (Markdown)
        result = f"# {template['name']}\n\n"
        result += f"**Type**: {template['type']}\n"
        result += f"**Subtype**: {template['subtype']}\n\n"

        if template.get('description'):
            result += f"## Description\n\n{template['description']}\n\n"

        usage = template.get('usage', {})
        if usage:
            result += f"## Usage Information\n\n"
            result += f"- **Base Class**: `{usage.get('base_class', 'Unknown')}`\n"
            result += f"- **Plugin Type**: {usage.get('plugin_type', 'Unknown')}\n\n"

        result += f"## Template Code\n\n"
        result += f"```python\n{template['content']}\n```\n\n"

        result += f"---\n\n"
        result += f"**Path**: `{template['relative_path']}`\n"
        result += f"**Size**: {template['size']} bytes\n"

        return result

    # ============================================================================
    # Python Templates Tool Methods (Issue #33)
    # ============================================================================

    def _list_python_templates_tool(self, template_type: str | None = None) -> str:
        """
        [SDK] List Python plugin templates for script conversion

        Lists available plugin templates that can be used to convert Glyphs scripts
        into proper plugins. These templates provide the standard structure and boilerplate
        code for different plugin types.

        Purpose: Help users discover available plugin templates for their conversion needs

        Template types:
        - filter: Filter plugins (with/without dialog)
        - reporter: Reporter plugins (visualization helpers)
        - palette: Palette plugins (sidebar panels)
        - general: General plugins (custom functionality)
        - file_format: File format plugins (import/export)
        - selecttool: SelectTool plugins (custom selection tools)

        Related workflow:
        1. Use this tool to browse available templates
        2. Use get_python_template to view template details
        3. Access templates as MCP resources for conversion
        4. Use PluginMaker.py utility for batch conversion (advanced)

        Args:
            template_type: Filter by plugin type (optional)

        Returns:
            List of available Python plugin templates with type and description
        """
        if not self.templates_manager:
            return "❌ Plugin Templates Manager not initialized"

        try:
            if template_type:
                templates = self.templates_manager.get_templates_by_type(template_type)
            else:
                templates = self.templates_manager.get_templates()

            if not templates:
                filter_msg = f" of type '{template_type}'" if template_type else ""
                return f"No Python templates found{filter_msg}"

            result = "## 🐍 Python Plugin Templates\n\n"
            result += f"Found {len(templates)} template(s)\n\n"

            # Group by type for better readability
            by_type: dict[str, list] = {}
            for tid, info in templates.items():
                ttype = info['type']
                if ttype not in by_type:
                    by_type[ttype] = []
                by_type[ttype].append((tid, info))

            # Display grouped results
            for ttype in sorted(by_type.keys()):
                result += f"### {ttype.title()} Templates\n\n"
                for tid, info in by_type[ttype]:
                    result += f"#### `{tid}`\n"
                    result += f"- **Name**: {info['name']}\n"
                    result += f"- **Subtype**: {info['subtype']}\n"
                    if info.get('description'):
                        result += f"- **Description**: {info['description']}\n"
                    result += f"- **MCP Resource**: `glyphs://plugin-template/{tid}`\n"
                    result += "\n"

            result += "\n💡 **Usage**:\n"
            result += "- Use `sdk(action='get_python_template', template_id='...')` for details\n"
            result += "- Access as MCP resource: `glyphs://plugin-template/{template_id}`\n"
            result += "- Templates include placeholder replacement instructions\n"

            return result

        except Exception as e:
            return f"❌ Error listing Python templates: {e}"

    def _get_python_template_tool(self, template_id: str) -> str:
        """
        [SDK] Get detailed information about a Python plugin template

        Retrieves complete template code and metadata for a specific plugin template.
        This is the primary way to view template content before using it for conversion.

        The template includes:
        - Complete plugin.py source code with placeholders
        - Base class and protocol information
        - Required imports and dependencies
        - Usage instructions and conversion notes

        Placeholder format:
        - ____PluginClassName____: Replace with your plugin class name
        - ____PluginName____: Replace with your plugin name
        - ____PluginMenuName____: Replace with menu display name

        Conversion workflow:
        1. Get template using this tool or MCP resource
        2. Replace placeholders with your plugin details
        3. Add your custom implementation code
        4. Save as .glyphsFilter/.glyphsReporter/etc.
        5. Install in ~/Library/Application Support/Glyphs 3/Plugins/
        6. Restart Glyphs and test

        Args:
            template_id: Template identifier (from list_python_templates)

        Returns:
            Complete template code with metadata and usage instructions
        """
        if not self.templates_manager:
            return "❌ Plugin Templates Manager not initialized"

        if not template_id:
            return "Please provide a template_id"

        try:
            template = self.templates_manager.get_template_by_id(template_id)

            if not template:
                available = self.templates_manager.get_templates()
                ids = list(available.keys())
                return f"❌ Template not found: {template_id}\n\nAvailable templates:\n" + "\n".join(
                    f"- {tid}" for tid in sorted(ids)
                )

            result = f"## 🐍 {template['name']}\n\n"
            result += f"**Type**: {template['type']}\n"
            result += f"**Subtype**: {template['subtype']}\n"
            result += f"**Template ID**: `{template_id}`\n\n"

            if template.get('description'):
                result += f"### Description\n\n{template['description']}\n\n"

            usage = template.get('usage', {})
            if usage:
                result += f"### Usage Information\n\n"
                result += f"- **Base Class**: `{usage.get('base_class', 'Unknown')}`\n"
                result += f"- **Plugin Type**: {usage.get('plugin_type', 'Unknown')}\n"

                requirements = usage.get('requirements', [])
                if requirements:
                    result += f"\n**Key Imports**:\n"
                    for req in requirements[:5]:
                        result += f"- `{req}`\n"
                result += "\n"

            result += f"### Template Code\n\n"
            result += f"```python\n{template['content']}\n```\n\n"

            result += f"### Placeholders to Replace\n\n"
            result += "- `____PluginClassName____`: Your plugin class name (e.g., MyAwesomeFilter)\n"
            result += "- `____PluginName____`: Your plugin name (e.g., My Awesome Filter)\n"
            result += "- `____PluginMenuName____`: Menu display name (e.g., My Filter)\n\n"

            result += f"### File Information\n\n"
            result += f"- **Path**: `{template['relative_path']}`\n"
            result += f"- **Size**: {template['size']} bytes\n"
            result += f"- **MCP Resource**: `glyphs://plugin-template/{template_id}`\n\n"

            result += "💡 **Next Steps**:\n"
            result += "1. Copy template code above\n"
            result += "2. Replace all placeholders (____*____)\n"
            result += "3. Add your custom implementation\n"
            result += "4. Save with appropriate extension (.glyphsFilter/.glyphsReporter/etc.)\n"
            result += "5. Install in ~/Library/Application Support/Glyphs 3/Plugins/\n"
            result += "6. Restart Glyphs and test your plugin!\n"

            return result

        except Exception as e:
            return f"❌ Error getting Python template: {e}"

    # ============================================================================
    # Xcode Templates Tool Methods (Issue #34)
    # ============================================================================

    def _get_xcode_template_resource(self, template_id: str) -> str:
        """Internal handler to get Xcode template resource content

        Formats template as Markdown with code blocks for MCP resource display.

        Args:
            template_id: Template identifier (e.g., "reporter", "filter")

        Returns:
            Formatted template content with metadata and usage instructions
        """
        if not self.xcode_templates_manager:
            return "❌ Xcode Templates manager not initialized"

        template = self.xcode_templates_manager.get_template_by_id(template_id)
        if not template:
            return f"❌ Template not found: {template_id}"

        # Format template as MCP resource (Markdown)
        result = f"# {template['name']}\n\n"
        result += f"**Type**: {template['type']}\n"
        result += f"**File Count**: {template['file_count']}\n\n"

        if template.get("description"):
            result += f"## Description\n\n{template['description']}\n\n"

        # Display file structure
        result += f"## File Structure\n\n"
        for file_info in template.get("files", []):
            result += f"- `{file_info['path']}` ({file_info['type']})\n"
        result += "\n"

        # Display source code
        source_files = template.get("source_files", {})
        if source_files:
            result += f"## Template Files\n\n"
            for file_path, content in source_files.items():
                ext = Path(file_path).suffix
                lang = (
                    "objective-c"
                    if ext in [".h", ".m"]
                    else "xml" if ext == ".plist" else "text"
                )
                result += f"### `{file_path}`\n\n"
                result += f"```{lang}\n{content}\n```\n\n"

        # Placeholder instructions
        result += f"## Xcode Placeholders\n\n"
        result += "Replace the following placeholders in Xcode:\n"
        result += "- `___PACKAGENAMEASIDENTIFIER___`: Your bundle identifier (e.g., com.YourName.PluginName)\n"
        result += "- `___FILENAME___`: File name without extension\n"
        result += "- `___PACKAGENAME___`: Plugin display name\n"
        result += "- `___FULLUSERNAME___`: Your full name\n"
        result += "- `___DATE___`: Current date\n"
        result += "- `___COPYRIGHT___`: Copyright notice\n\n"

        result += f"---\n\n"
        result += f"**Template ID**: `{template_id}`\n"
        result += f"**MCP Resource**: `glyphs://xcode-template/{template_id}`\n"

        return result

    def _list_xcode_templates_tool(self, template_type: str | None = None) -> str:
        """[SDK] List Xcode plugin templates for native Objective-C development

        Lists available Xcode templates for creating Glyphs plugins using Objective-C.
        These templates provide the standard Xcode project structure and boilerplate
        code for different plugin types.

        Purpose: Help developers discover available Xcode templates for plugin development

        Template types:
        - reporter: Reporter plugins (visualization helpers)
        - filter: Filter plugins (font effect processors)
        - palette: Palette plugins (sidebar panels)
        - tool: Tool plugins (custom editing tools)
        - file_format: File format plugins (import/export)
        - plugin: General plugins
        - plugin_base: Base template

        Related workflow:
        1. Use this tool to browse available templates
        2. Use get_xcode_template to view template details
        3. Access templates as MCP resources for development
        4. Create Xcode project from template

        Args:
            template_type: Filter by plugin type (optional)

        Returns:
            List of available Xcode plugin templates with type and description
        """
        if not self.xcode_templates_manager:
            return "❌ Xcode Templates Manager not initialized"

        try:
            if template_type:
                templates = self.xcode_templates_manager.get_templates_by_type(
                    template_type
                )
            else:
                templates = self.xcode_templates_manager.get_templates()

            if not templates:
                filter_msg = f" of type '{template_type}'" if template_type else ""
                return f"No Xcode templates found{filter_msg}"

            result = "## 📱 Xcode Plugin Templates\n\n"
            result += f"Found {len(templates)} template(s)\n\n"

            # Group by type for better readability
            by_type: dict[str, list] = {}
            for tid, info in templates.items():
                ttype = info["type"]
                if ttype not in by_type:
                    by_type[ttype] = []
                by_type[ttype].append((tid, info))

            # Display grouped results
            for ttype in sorted(by_type.keys()):
                result += f"### {ttype} Templates\n\n"
                for tid, info in by_type[ttype]:
                    result += f"#### `{tid}`\n"
                    result += f"- **Name**: {info['name']}\n"
                    result += f"- **Files**: {info['file_count']}\n"
                    if info.get("description"):
                        result += f"- **Description**: {info['description']}\n"
                    result += f"- **MCP Resource**: `glyphs://xcode-template/{tid}`\n"
                    result += "\n"

            result += "\n💡 **Usage**:\n"
            result += "- Use `sdk(action='get_xcode_template', template_id='...')` for details\n"
            result += "- Access as MCP resource: `glyphs://xcode-template/{template_id}`\n"
            result += "- Templates require Xcode for Objective-C development\n"

            return result

        except Exception as e:
            return f"❌ Error listing Xcode templates: {e}"

    def _get_xcode_template_tool(self, template_id: str) -> str:
        """[SDK] Get detailed information about an Xcode plugin template

        Retrieves complete template code and metadata for a specific Xcode template.
        This is the primary way to view template content before using it for development.

        The template includes:
        - Complete .h (header) and .m (implementation) files with placeholders
        - .plist configuration files
        - Project structure information
        - Placeholder replacement instructions

        Xcode Placeholder format:
        - ___PACKAGENAMEASIDENTIFIER___: Bundle identifier
        - ___FILENAME___: File name
        - ___PACKAGENAME___: Plugin name
        - ___FULLUSERNAME___: Developer name
        - ___DATE___: Date
        - ___COPYRIGHT___: Copyright

        Development workflow:
        1. Get template using this tool or MCP resource
        2. Create new Xcode project from template
        3. Replace placeholders (Xcode does this automatically)
        4. Implement your custom plugin logic
        5. Build and install to ~/Library/Application Support/Glyphs 3/Plugins/
        6. Restart Glyphs and test

        Args:
            template_id: Template identifier (from list_xcode_templates)

        Returns:
            Complete template code with metadata and usage instructions
        """
        if not self.xcode_templates_manager:
            return "❌ Xcode Templates Manager not initialized"

        if not template_id:
            return "Please provide a template_id"

        try:
            template = self.xcode_templates_manager.get_template_by_id(template_id)

            if not template:
                available = self.xcode_templates_manager.get_templates()
                ids = list(available.keys())
                return (
                    f"❌ Template not found: {template_id}\n\nAvailable templates:\n"
                    + "\n".join(f"- {tid}" for tid in sorted(ids))
                )

            result = f"## 📱 {template['name']}\n\n"
            result += f"**Type**: {template['type']}\n"
            result += f"**Template ID**: `{template_id}`\n"
            result += f"**File Count**: {template['file_count']}\n\n"

            if template.get("description"):
                result += f"### Description\n\n{template['description']}\n\n"

            # File structure
            result += f"### File Structure\n\n"
            for file_info in template.get("files", []):
                result += f"- `{file_info['path']}` ({file_info['type']})\n"
            result += "\n"

            # Source code
            source_files = template.get("source_files", {})
            if source_files:
                result += f"### Template Code\n\n"
                for file_path, content in source_files.items():
                    ext = Path(file_path).suffix
                    lang = (
                        "objective-c"
                        if ext in [".h", ".m"]
                        else "xml" if ext == ".plist" else "text"
                    )
                    result += f"#### `{file_path}`\n\n"
                    result += f"```{lang}\n{content}\n```\n\n"

            # Placeholders
            result += f"### Xcode Placeholders to Replace\n\n"
            result += "- `___PACKAGENAMEASIDENTIFIER___`: Your bundle identifier (e.g., com.YourName.PluginName)\n"
            result += "- `___FILENAME___`: File name without extension\n"
            result += "- `___PACKAGENAME___`: Plugin display name\n"
            result += "- `___FULLUSERNAME___`: Your full name (for copyright)\n"
            result += "- `___DATE___`: Current date\n"
            result += "- `___COPYRIGHT___`: Copyright notice\n\n"

            result += f"### File Information\n\n"
            result += f"- **Path**: `{template['path']}`\n"
            result += f"- **MCP Resource**: `glyphs://xcode-template/{template_id}`\n\n"

            result += "💡 **Next Steps**:\n"
            result += "1. Use this template in Xcode: File > New > Project...\n"
            result += "2. Xcode will automatically replace placeholders\n"
            result += "3. Implement your plugin logic in the template methods\n"
            result += "4. Build the plugin (Cmd+B)\n"
            result += "5. Install to ~/Library/Application Support/Glyphs 3/Plugins/\n"
            result += "6. Restart Glyphs and test your plugin!\n"

            return result

        except Exception as e:
            return f"❌ Error getting Xcode template: {e}"

    # ============================================================================
    # Samples Resource Handlers (Issue #37)
    # ============================================================================

    def _get_python_sample_resource(self, sample_id: str) -> str:
        """Internal handler to get Python sample resource content

        Formats sample as Markdown with code blocks for MCP resource display.

        Args:
            sample_id: Sample identifier (e.g., "callback_for_context_menu")

        Returns:
            Formatted sample content with metadata and source code
        """
        if not self.python_samples_manager:
            return "❌ Python Samples manager not initialized"

        sample = self.python_samples_manager.get_sample_by_id(sample_id)
        if not sample:
            return f"❌ Sample not found: {sample_id}"

        # Format sample as MCP resource (Markdown)
        result = f"# {sample['name']}\n\n"
        result += f"**Type**: {sample['type']}\n"
        result += f"**Has Bundle**: {'Yes' if sample.get('has_bundle') else 'No'}\n\n"

        # README section
        if sample.get("readme"):
            result += f"## README\n\n{sample['readme']}\n\n"

        # File structure
        result += f"## File Structure ({sample['source_file_count']} files)\n\n"
        for file_info in sample.get("source_files", []):
            result += f"- `{file_info['path']}`\n"
        result += "\n"

        # Load errors warning
        if sample.get("partial_load"):
            load_errors = sample.get("load_errors", [])
            result += f"## ⚠️ Load Warnings\n\n"
            result += f"Some files could not be loaded:\n\n"
            for error in load_errors:
                result += f"- `{error['file']}`: {error['error']}\n"
            result += "\n"

        # Source code
        source_code = sample.get("source_code", {})
        if source_code:
            result += f"## Source Code\n\n"
            for file_path, content in source_code.items():
                result += f"### `{file_path}`\n\n"
                result += f"```python\n{content}\n```\n\n"

        result += f"---\n\n"
        result += f"**Sample ID**: `{sample_id}`\n"
        result += f"**MCP Resource**: `glyphs://python-sample/{sample_id}`\n"

        return result

    def _get_xcode_sample_resource(self, sample_id: str) -> str:
        """Internal handler to get Xcode sample resource content

        Formats sample as Markdown with code blocks for MCP resource display.

        Args:
            sample_id: Sample identifier (e.g., "inspector_demo")

        Returns:
            Formatted sample content with metadata and source code
        """
        if not self.xcode_samples_manager:
            return "❌ Xcode Samples manager not initialized"

        sample = self.xcode_samples_manager.get_sample_by_id(sample_id)
        if not sample:
            return f"❌ Sample not found: {sample_id}"

        # Format sample as MCP resource (Markdown)
        result = f"# {sample['name']}\n\n"
        result += f"**Xcode Project**: {'✅ Yes' if sample.get('has_xcode_project') else '❌ No'}\n\n"

        # README section
        if sample.get("readme"):
            result += f"## README\n\n{sample['readme']}\n\n"

        # File structure
        result += f"## File Structure ({sample['source_file_count']} files)\n\n"
        for file_info in sample.get("source_files", []):
            result += f"- `{file_info['path']}`\n"
        result += "\n"

        # Load errors warning
        if sample.get("partial_load"):
            load_errors = sample.get("load_errors", [])
            result += f"## ⚠️ Load Warnings\n\n"
            result += f"Some files could not be loaded:\n\n"
            for error in load_errors:
                result += f"- `{error['file']}`: {error['error']}\n"
            result += "\n"

        # Source code
        source_code = sample.get("source_code", {})
        if source_code:
            result += f"## Source Code\n\n"
            for file_path, content in source_code.items():
                ext = Path(file_path).suffix
                lang = "objective-c" if ext in [".h", ".m"] else "text"
                result += f"### `{file_path}`\n\n"
                result += f"```{lang}\n{content}\n```\n\n"

        result += f"---\n\n"
        result += f"**Sample ID**: `{sample_id}`\n"
        result += f"**MCP Resource**: `glyphs://xcode-sample/{sample_id}`\n"

        return result
