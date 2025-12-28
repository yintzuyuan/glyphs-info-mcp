"""
GlyphsSDK Search Module
Integrates SDK content indexing, search, and formatting functionality
"""

import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

# Add shared core module path
shared_path = str(Path(__file__).parent.parent.parent / "src" / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

# Dynamically import other SDK modules (avoid relative import issues)
import importlib.util

from glyphs_info_mcp.shared.core.base_module import BaseMCPModule
from glyphs_info_mcp.shared.core.sdk_native_accessor import SDKNativeAccessor


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
            "sdk_list_xcode_templates": self._list_xcode_templates_tool,
            "sdk_get_xcode_template": self._get_xcode_template_tool,
            "sdk_list_xcode_samples": self._list_xcode_samples_tool,
            "sdk_get_xcode_sample": self._get_xcode_sample_tool,
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

    def _list_xcode_templates_tool(self) -> str:
        """
        [SDK] List all Xcode plugin templates

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

    def _get_xcode_template_tool(self, template_name: str) -> str:
        """
        [SDK] Get complete content of a specific Xcode template

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
