#!/usr/bin/env python3
"""
Unified API module for Glyphs.app API documentation
Combines functionality from api, api_search, and vanilla modules
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any, Callable

# Use shared core library
project_root = Path(__file__).parent.parent.parent
shared_core_path = str(project_root / "src" / "shared")
if shared_core_path not in sys.path:
    sys.path.insert(0, shared_core_path)

from glyphs_info_mcp.shared.core.base_module import BaseMCPModule
from glyphs_info_mcp.data.class_hierarchy import (
    CLASS_NAMES,
    CLASS_REFERENCES,
    COMPOSITION,
    INHERITANCE,
    OFFICIAL_DIAGRAM_URL,
    REFERENCES,
    build_structure_dict,
    get_display_name,
    get_python_class,
)

logger = logging.getLogger(__name__)

# Dynamically import submodules - use absolute path
import importlib.util
import sys
from pathlib import Path


def import_submodule(module_path: str, class_name: str) -> type[Any]:
    """Dynamically import submodule"""
    spec = importlib.util.spec_from_file_location(class_name.lower(), module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, class_name)


# Get current file directory
current_dir = Path(__file__).parent

# Dynamically import required classes
try:
    # New architecture: use dedicated submodules
    PythonAPIModule = import_submodule(
        str(current_dir / "python_api" / "python_api_module.py"), "PythonAPIModule"
    )
    ObjectiveCAPIModule = import_submodule(
        str(current_dir / "objc_api" / "objc_api_module.py"), "ObjectiveCAPIModule"
    )

    # Legacy modules (Plugin Tools, WebSearch, etc.)
    PluginAPIManager = import_submodule(
        str(current_dir / "api" / "plugin_api.py"), "PluginAPIManager"
    )
    PluginToolsModule = import_submodule(
        str(current_dir / "plugins_tools.py"), "PluginToolsModule"
    )
    WebSearchAPIModule = import_submodule(
        str(current_dir / "websearch" / "websearch_api_module.py"), "WebSearchAPIModule"
    )
except Exception as e:
    logger.error(f"Failed to import submodules: {e}")
    raise


class UnifiedAPIModule(BaseMCPModule):
    """Unified API documentation module"""

    def __init__(self, name: str = "api", data_path: Path | None = None):
        if data_path is None:
            # Get the module root directory (3 levels up from this file)
            module_root = Path(__file__).parent
            data_path = module_root / "data"

        super().__init__(name, data_path)

        # New architecture: submodules
        self.python_api_module: Any = None  # PythonAPIModule instance
        self.objc_api_module: Any = None  # ObjectiveCAPIModule instance

        # Legacy modules
        self.plugin_tools_module: Any = None
        self.websearch_api_module: Any = None
        self.vanilla_tools: Any = None

        # Other retained variables
        self.plugin_api: Any = None
        self.sdk_accessor: Any = None

    @property
    def python_api(self) -> Any:
        """Backward-compatible property proxy, maps self.python_api to self.python_api_module.python_api"""
        if self.python_api_module and hasattr(self.python_api_module, 'python_api'):
            return self.python_api_module.python_api
        return None

    def set_search_engine(self, search_engine: Any) -> None:
        """Set unified search engine (called by server.py)"""
        self.search_engine = search_engine

        # Inject search engine to all submodules
        if self.python_api_module and hasattr(
            self.python_api_module, "set_search_engine"
        ):
            self.python_api_module.set_search_engine(search_engine)
        if self.objc_api_module and hasattr(self.objc_api_module, "set_search_engine"):
            self.objc_api_module.set_search_engine(search_engine)
        if self.websearch_api_module and hasattr(
            self.websearch_api_module, "set_search_engine"
        ):
            self.websearch_api_module.set_search_engine(search_engine)

    def initialize(self) -> bool:
        """Initialize the API module - New architecture: Coordinator pattern"""
        try:
            project_root = Path(__file__).parent.parent.parent

            # === New architecture: Initialize submodules ===

            # 1. Initialize Python API module
            self.python_api_module = PythonAPIModule("python-api", self.data_path)
            if not self.python_api_module.initialize():
                logger.warning("Failed to initialize Python API module")
            else:
                logger.info("✅ Python API module initialized")

            # 2. Initialize Objective-C API module
            self.objc_api_module = ObjectiveCAPIModule("objc-api", self.data_path)
            if not self.objc_api_module.initialize():
                logger.warning("Failed to initialize Objective-C API module")
            else:
                logger.info("✅ Objective-C API module initialized")

            # === Legacy architecture (Plugin Tools, WebSearch, Vanilla, etc.) ===

            # Initialize SDK Native Accessor (for Plugin API)
            sdk_root = project_root / "data" / "official" / "GlyphsSDK"
            from glyphs_info_mcp.shared.core.sdk_native_accessor import SDKNativeAccessor

            self.sdk_accessor = SDKNativeAccessor(sdk_root)
            logger.info("SDK Native Accessor initialized")

            # Initialize Plugin API Manager with SDK Native Accessor
            self.plugin_api = PluginAPIManager(sdk_accessor=self.sdk_accessor)
            logger.info("Plugin API Manager initialized with SDK Native Accessor")

            # Plugin Tools functionality integrated into SDK Native Accessor
            self.plugin_tools_module = None

            # Initialize websearch API module
            self.websearch_api_module = WebSearchAPIModule(
                "websearch-api", self.data_path
            )
            if not self.websearch_api_module.initialize():
                logger.warning("Failed to initialize websearch API module")
            else:
                logger.info("✅ WebSearch API module initialized")

            # Initialize Vanilla Tools with local accessor
            try:
                # Create Repository Scanner and Vanilla Local Accessor
                from glyphs_info_mcp.shared.core.repository_scanner import RepositoryScanner
                from glyphs_info_mcp.shared.core.vanilla_local_accessor import VanillaLocalAccessor

                # Dynamically import VanillaTools
                VanillaTools = import_submodule(
                    str(current_dir / "vanilla_tools.py"), "VanillaTools"
                )

                # Set Submodule fallback paths
                project_root = Path(__file__).parent.parent.parent
                fallback_paths = {
                    "vanilla": project_root / "data/official/vanilla/Lib/vanilla",
                }

                # Auto-detect Repositories path
                repo_scanner = RepositoryScanner.auto_detect()
                if repo_scanner:
                    # Set fallback paths
                    repo_scanner.fallback_paths = fallback_paths
                    repo_scanner.scan_repositories()
                    vanilla_accessor = VanillaLocalAccessor(repo_scanner)

                    if vanilla_accessor.is_available():
                        self.vanilla_tools = VanillaTools(vanilla_accessor)
                        logger.info("✅ Vanilla Tools initialized with local accessor")
                    else:
                        logger.warning("⚠️  Vanilla not found in Repositories")
                else:
                    logger.warning(
                        "⚠️  Glyphs Repositories not found - Vanilla tools will be unavailable"
                    )
            except Exception as e:
                logger.error(f"Failed to initialize Vanilla Tools: {e}")
                self.vanilla_tools = None

            self.is_initialized = True

            # Count initialized modules
            initialized_modules: list[str] = []
            if self.python_api_module and self.python_api_module.is_initialized:
                initialized_modules.append("PythonAPI")
            if self.objc_api_module and self.objc_api_module.is_initialized:
                initialized_modules.append("ObjectiveCAPI")
            if self.websearch_api_module and self.websearch_api_module.is_initialized:
                initialized_modules.append("WebSearch")
            if self.vanilla_tools:
                initialized_modules.append("Vanilla")
            if self.plugin_api:
                initialized_modules.append("PluginAPI")

            logger.info(
                f"✅ Unified API module initialized with {len(initialized_modules)} sub-modules: {', '.join(initialized_modules)}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to initialize API module: {e}")
            return False

    def core_search(
        self, query: str, max_results: int = 5, **kwargs: Any
    ) -> list[dict[str, Any]]:
        """Core search function - For unified search engine use only (New architecture: delegates to submodules)

        Returns structured search results without vocabulary processing or formatting

        Args:
            query: Search query (pre-processed)
            max_results: Maximum number of results
            scope: Search scope

        Returns:
            Structured search result list
        """
        if not self.is_initialized:
            return []

        scope = kwargs.get("scope", "auto")
        results: list[dict[str, Any]] = []

        try:
            # === New architecture: Delegate to submodules ===

            # 1. Python API module search
            if self.python_api_module and self.python_api_module.is_initialized:
                python_results = self.python_api_module.core_search(
                    query, max_results, scope=scope
                )
                results.extend(python_results)

            # 2. Objective-C API module search
            if self.objc_api_module and self.objc_api_module.is_initialized:
                objc_results = self.objc_api_module.core_search(
                    query, max_results // 2, scope=scope
                )
                results.extend(objc_results)

            # === Legacy architecture ===

            # 3. Plugin API search (may migrate to independent module in the future)
            if hasattr(self, "plugin_api") and self.plugin_api:
                plugin_results = self._search_plugin_api(query, max_results // 2)
                results.extend(plugin_results)

        except Exception as e:
            logger.error(f"API core search failed: {e}")

        return results[:max_results]

    def _search_python_api_structured(
        self, query: str, max_results: int, scope: str
    ) -> list[dict[str, Any]]:
        """Search in Python API (simplified version - returns formatted string directly)"""
        results = []

        try:
            # Use Python API Manager's indexed search (already formatted)
            search_result = self.python_api.search(
                query, search_scope=scope, max_results=max_results
            )

            # Return entire result as single item (already in optimal format)
            if search_result and "Not found" not in search_result:
                results.append(
                    {
                        "title": f"Python API search results: '{query}'",
                        "content": search_result,
                        "type": "api_index",
                        "source": "python_api",
                        "score": 0.9,
                    }
                )

        except Exception as e:
            logger.error(f"Python API search failed: {e}")

        return results

    def _search_plugin_api(self, query: str, max_results: int) -> list[dict[str, Any]]:
        """Search in Plugin API"""
        results = []

        try:
            if hasattr(self.plugin_api, "search"):
                plugin_results = self.plugin_api.search(query)
                for result in plugin_results[:max_results]:
                    results.append(
                        {
                            "title": result.get("name", "Plugin API"),
                            "content": result.get("description", ""),
                            "type": "plugin",
                            "source": "api",
                            "score": 0.6,
                        }
                    )
        except Exception as e:
            logger.debug(f"Plugin API search failed: {e}")

        return results

    def _load_api_data(self, api_path: Path) -> None:
        """Load API data files"""
        try:
            # Load Python API
            python_file = api_path / "python_api.json"
            if python_file.exists():
                with open(python_file, encoding="utf-8") as f:
                    self.python_api_data = json.load(f)

            # Load drawing tools
            drawing_file = api_path / "drawing_tools.json"
            if drawing_file.exists():
                with open(drawing_file, encoding="utf-8") as f:
                    self.drawing_tools_data = json.load(f)

            # Load plugins
            plugins_file = api_path / "plugins.json"
            if plugins_file.exists():
                with open(plugins_file, encoding="utf-8") as f:
                    self.plugins_data = json.load(f)

        except Exception as e:
            logger.error(f"Failed to load API data: {e}")

    def get_tools(self) -> dict[str, Callable[..., Any]]:
        """Get available tools as dictionary - Coordinator pattern aggregates all submodule tools"""
        tools = {}

        # === New architecture: Aggregate submodule tools ===

        # 1. Python API module tools (3)
        if self.python_api_module and self.python_api_module.is_initialized:
            python_tools = self.python_api_module.get_tools()
            tools.update(python_tools)
            logger.debug(f"Added {len(python_tools)} Python API tools")

        # 2. Objective-C API module tools (2)
        if self.objc_api_module and self.objc_api_module.is_initialized:
            objc_tools = self.objc_api_module.get_tools()
            tools.update(objc_tools)
            logger.debug(f"Added {len(objc_tools)} Objective-C API tools")

        # === Legacy architecture tools ===

        # 3. WebSearch API module tools (excluding Vanilla, now using local version)
        if self.websearch_api_module and self.websearch_api_module.is_initialized:
            websearch_tools = self.websearch_api_module.get_tools()
            # Remove Vanilla-related tools (now using local version)
            websearch_tools_filtered = {
                k: v for k, v in websearch_tools.items() if "vanilla" not in k.lower()
            }
            tools.update(websearch_tools_filtered)
            logger.debug(f"Added {len(websearch_tools_filtered)} WebSearch API tools")

        # 4. Vanilla Tools (local accessor)
        if self.vanilla_tools:
            vanilla_tools = {
                "api_search_vanilla_ui": self.search_vanilla_ui,
                "api_get_vanilla_ui": self.get_vanilla_ui,
                "api_list_vanilla_ui": self.list_vanilla_ui,
            }
            tools.update(vanilla_tools)
            logger.debug(f"Added {len(vanilla_tools)} Vanilla Tools (local accessor)")

        # 5. Plugin Tools (temporarily kept here, may migrate to independent module in the future)
        # Plugin tools functionality provided by SDK Native Accessor, not registered as MCP tools

        # 6. API Structure query tools (Issue #51)
        structure_tools = {
            "api_get_class_hierarchy": self.api_get_class_hierarchy,
            "api_get_class_relationships": self.api_get_class_relationships,
            "api_navigate_structure": self.api_navigate_structure,
        }
        tools.update(structure_tools)
        logger.debug(f"Added {len(structure_tools)} API Structure tools")

        logger.info(f"✅ Unified API module registered {len(tools)} total tools")
        return tools

    def python_api_class_info(
        self, class_name: str, detail_level: str = "overview"
    ) -> str:
        """
        [PYTHON API] Python class information tool supporting multiple detail levels

        Features: Provides Python API class information at different detail levels based on needs, solving information overload problem.

        Args:
            class_name: Class name (e.g., GSFont, GSGlyph, GSLayer)
            detail_level: Detail level
                - "overview": Summary + important members + query guide (default)
                - "detailed": Categorized member list + type info + usage tips
                - "full": Complete member information (suitable for large development tasks)

        Returns:
            Formatted Python API class information
        """
        if not self.is_initialized:
            return "API module not initialized"

        if detail_level not in ["overview", "detailed", "full"]:
            return f"Invalid detail_level: {detail_level}. Supported values: overview, detailed, full"

        return self._get_python_class_info(class_name, detail_level)

    def python_api_search(
        self, query: str, scope: str = "auto", max_results: int = 5
    ) -> str:
        """
        [PYTHON API] Query Glyphs Python API official specifications and documentation

        Purpose: Find official documentation and specifications for API classes, methods, and properties
        Content types: API reference documentation, type definitions, parameter descriptions, return values
        Complementary tools: Use `sdk_search` to get actual code examples and implementation guidance

        When to use:
        - Need to understand correct API syntax and parameters
        - Query type definitions for methods or properties
        - Confirm official API usage and specifications
        - Find class inheritance relationships and member lists

        Args:
            query: Search keyword (class name, method name, property name, etc.)
            scope: Search scope
                - "auto": Auto-detect search scope (default)
                - "classes": Search classes only
                - "methods": Search methods only
                - "properties": Search properties only
                - "all": Search all content
            max_results: Maximum number of results

        Returns:
            Formatted API documentation search results with related SDK example hints
        """
        if not self.is_initialized:
            return "API module not initialized"

        if scope not in ["auto", "classes", "methods", "properties", "all"]:
            return f"Invalid scope: {scope}. Supported values: auto, classes, methods, properties, all"

        # Use local Python search logic directly, avoiding mixing with Header search
        processed_query = query
        user_language = "zh"

        # Use term processor for preprocessing (if available)
        if self.search_engine and self.search_engine.query_processor:
            processed_query, user_language = (
                self.search_engine.query_processor.preprocess_query(query)
            )

        result = self._python_search(processed_query, scope, max_results)

        # Use term processor for postprocessing
        if self.search_engine and self.search_engine.query_processor:
            result = self.search_engine.query_processor.postprocess_output(
                result, user_language
            )

        # Add related tool recommendations
        result += self._add_cross_references(processed_query, "python_api")

        return result

    def python_core_search(
        self, query: str, max_results: int = 5
    ) -> list[dict[str, Any]]:
        """Dedicated Python API core search method for unified search engine use"""
        if not self.is_initialized:
            return []

        # Use local Python search logic
        scope = "all"
        python_results = self._python_search(query, scope, max_results)

        # Parse results and convert to unified format
        unified_results = []

        # Parse python_results string and extract results
        if (
            "Found 0 results" not in python_results
            and "No results found" not in python_results
        ):
            # Simplified handling: return entire result as one entry
            # In practice, you may want more granular parsing
            unified_results.append(
                {
                    "title": f"Python API search results: '{query}'",
                    "content": python_results[:500],  # Limit length
                    "score": 0.8,
                    "source": "python_api",
                    "metadata": {"search_type": "python_api", "query": query},
                }
            )

        return unified_results

    def python_api_member_info(
        self, class_name: str, member_name: str, member_type: str
    ) -> str:
        """
        [PYTHON API] Get detailed information and usage examples for Python API class members

        Features: Provides complete documentation, parameter descriptions, and code examples for specific Python API class members.

        Args:
            class_name: Class name (e.g., GSFont, GSGlyph, GSLayer)
            member_name: Member name (methods, properties, etc.)
            member_type: Member type, must be "property" or "method"

        Returns:
            Detailed documentation and usage examples for Python API members
        """
        if not self.is_initialized:
            return "API module not initialized"

        return self._get_python_member_info(class_name, member_name, member_type)

    # Plugin tools methods
    def search_plugins(self, query: str, plugin_type: str | None = None) -> str:
        """
        [PLUGIN DEV] Search Glyphs.app plugin types and features

        When to use: Only when user explicitly mentions "making plugins", "plugin development"

        Args:
            query: Search query string
            plugin_type: Optional plugin type filter

        Returns:
            Search results for plugins matching the query
        """
        if not self.sdk_accessor:
            return "SDK Native Accessor not available"

        # Use SDK Native Accessor to search plugin classes
        results = self.sdk_accessor.search_plugin_classes(query)
        if not results:
            return f"No plugin classes found matching '{query}'"

        # Format results
        output = [f"🔍 Found {len(results)} related plugin classes:\n"]
        for i, result in enumerate(results[:10], 1):
            output.append(f"**{i}. {result['name']}**")
            if result.get("doc"):
                first_line = result["doc"].split("\n")[0].strip()
                output.append(f"   📝 {first_line}")
            output.append("")

        return "\n".join(output)

    def get_plugin_details(self, plugin_name: str) -> str:
        """
        [PLUGIN DEV] Get detailed information for a specific plugin type

        When to use: Only when user explicitly mentions "making plugins", "plugin development"

        Args:
            plugin_name: Name of the plugin class

        Returns:
            Detailed information about the plugin including methods and usage
        """
        if not self.sdk_accessor:
            return "SDK Native Accessor not available"

        # Get plugin class info from SDK Native Accessor
        plugin_info = self.sdk_accessor.get_plugin_class(plugin_name)
        if not plugin_info:
            return f"Plugin class not found: {plugin_name}"

        # Format output
        output = [f"# {plugin_info['name']}\n"]
        if plugin_info.get("base_class"):
            output.append(f"**Base Class**: {plugin_info['base_class']}\n")
        if plugin_info.get("doc"):
            output.append(f"## Description\n{plugin_info['doc']}\n")
        if plugin_info.get("methods"):
            output.append(f"## Methods ({len(plugin_info['methods'])})\n")
            for method in plugin_info["methods"]:
                output.append(f"- `{method['name']}()`")
                if method.get("doc"):
                    output.append(f"  - {method['doc'].split(chr(10))[0]}")

        return "\n".join(output)

    def get_method_details(self, method_name: str) -> str:
        """
        [PLUGIN DEV] Get detailed information for a specific plugin method

        When to use: Only when user explicitly mentions "making plugins", "plugin development"

        Args:
            method_name: Name of the method to look up

        Returns:
            Detailed information about the method across all plugins
        """
        if not self.sdk_accessor:
            return "SDK Native Accessor not available"

        # Search for the method in all plugin classes
        all_classes = self.sdk_accessor.list_plugin_classes()
        found_methods = []

        for cls in all_classes:
            for method in cls.get("methods", []):
                if method["name"] == method_name:
                    found_methods.append({"class": cls["name"], "method": method})

        if not found_methods:
            return f"Method not found in plugin classes: {method_name}"

        # Format output
        output = [f"# Method: {method_name}\n"]
        output.append(f"Found in {len(found_methods)} plugin classes:\n")

        for item in found_methods:
            output.append(f"## {item['class']}")
            if item["method"].get("doc"):
                output.append(f"{item['method']['doc']}\n")

        return "\n".join(output)

    def generate_plugin_code(self, plugin_type: str, plugin_name: str) -> str:
        """
        [PLUGIN DEV] Generate code template for a specific plugin type

        When to use: Only when user explicitly mentions "making plugins", "plugin development"

        Args:
            plugin_type: Type of plugin to generate (e.g., FileFormatPlugin, ReporterPlugin)
            plugin_name: Custom name for the generated plugin

        Returns:
            Generated Python code template for the plugin
        """
        # This functionality has been moved to SDK module's Plugin Templates resource
        return (
            "This functionality has been migrated to SDK module's Plugin Templates resource.\n\n"
            "Please use the following tools:\n"
            "1. `sdk_list_plugin_types` - List all available plugin template types\n"
            "2. `sdk_get_plugin_template` - Get complete code for a specific plugin template\n\n"
            "Example: sdk_get_plugin_template(template_id='Filter_without_dialog')"
        )

    def list_available_plugins(self) -> str:
        """
        [PLUGIN DEV] List all available plugin types and descriptions

        When to use: Only when user explicitly mentions "making plugins", "plugin development"

        Returns:
            List of all available plugin types and their purposes
        """
        if not self.sdk_accessor:
            return "SDK Native Accessor not available"

        # List all plugin classes
        classes = self.sdk_accessor.list_plugin_classes()
        output = [f"# Available Glyphs Plugin Classes ({len(classes)})\n"]

        for cls in classes:
            output.append(f"## {cls['name']}")
            if cls.get("doc"):
                first_line = cls["doc"].split("\n")[0].strip()
                output.append(f"{first_line}\n")

        return "\n".join(output)

    def get_inheritance_info(self) -> str:
        """
        [PLUGIN DEV] Get plugin class inheritance hierarchy information

        When to use: Only when user explicitly mentions "making plugins", "plugin development"

        Returns:
            Information about plugin class inheritance relationships
        """
        if not self.sdk_accessor:
            return "SDK Native Accessor not available"

        # Collect inheritance info for all classes
        classes = self.sdk_accessor.list_plugin_classes()
        output = ["# Glyphs Plugin Class Inheritance Architecture\n"]

        for cls in classes:
            output.append(f"- **{cls['name']}**")
            if cls.get("base_class"):
                output.append(f"  - Inherits from: `{cls['base_class']}`")
            output.append("")

        return "\n".join(output)

    # Implementation methods

    def _search_python_api(self, query: str, max_results: int) -> str:
        """Implementation for Python API search with smart routing"""
        if " " in query.strip():
            # Multi-word query - use smart routing
            return self._smart_search_python_api(query, max_results)
        else:
            # Single word query - use direct search
            return self.python_api.search(query)

    def _smart_search_python_api(self, query: str, max_results: int) -> str:
        """Enhanced smart search for Python API with better relevance"""
        query_words = query.lower().split()

        # Glyphs-specific class keywords
        class_keywords = [
            "gsfont",
            "gsglyph",
            "gslayer",
            "gspath",
            "gsnode",
            "gsanchor",
            "gsguide",
            "gsmaster",
        ]

        # Check if query is about a specific class
        class_match = None
        for word in query_words:
            if word in class_keywords:
                class_match = word
                break

        if class_match:
            # Try to get class overview first
            result = self.python_api.get_class_overview(class_match.upper())
            if result and "error" not in result:
                return f"# 🐍 Python API - {class_match.upper()}\n\n{self._format_class_info(result)}"

        # Enhanced multi-word search strategy
        if len(query_words) > 1:
            return self._enhanced_multi_word_search(query, query_words, max_results)
        else:
            # Single word search - use direct search
            return self._single_word_search(query, max_results)

    def _enhanced_multi_word_search(
        self, query: str, query_words: list, max_results: int
    ) -> str:
        """Enhanced multi-word search with better relevance scoring"""
        # Define search priority: object terms > action terms
        object_terms = [
            "background",
            "anchor",
            "bounds",
            "width",
            "height",
            "layer",
            "glyph",
            "font",
            "color",
            "path",
            "node",
            "guide",
            "master",
            "component",
        ]
        action_terms = [
            "add",
            "remove",
            "get",
            "set",
            "create",
            "delete",
            "update",
            "find",
        ]

        # Separate words by priority
        primary_words = [w for w in query_words if w in object_terms]
        secondary_words = [w for w in query_words if w in action_terms]
        other_words = [
            w
            for w in query_words
            if w not in object_terms and w not in action_terms and len(w) > 2
        ]

        # Search priority: primary > other > secondary
        search_order = primary_words + other_words + secondary_words

        # Try each word in priority order
        best_result = None
        best_word = None

        for word in search_order:
            word_result = self.python_api.search(word)
            if (
                word_result
                and not word_result.startswith("Not found")
            ):
                # If this is a primary word (object term), use it immediately
                if word in object_terms:
                    return f"# 🔍 Multi-word Search: {query}\n\n## Key search results for '{word}':\n{word_result}"

                # Otherwise, store as best result if we haven't found one yet
                if best_result is None:
                    best_result = word_result
                    best_word = word

        # Return best result found
        if best_result:
            return f"# 🔍 Multi-word Search: {query}\n\n## Related search results for '{best_word}':\n{best_result}"

        # Fallback to complete phrase search
        complete_result = self.python_api.search(query)
        if complete_result and not complete_result.startswith("Not found"):
            return f"# 🔍 Complete Query: {query}\n\n{complete_result}"

        return f"No Python API found matching '{query}'"

    def _single_word_search(self, query: str, max_results: int) -> str:
        """Enhanced single word search"""
        result = self.python_api.search(query)
        if result and not result.startswith("Not found"):
            return f"# 🔍 Python API Search: {query}\n\n{result}"

        return f"No Python API found matching '{query}'"

    def _get_python_class_info(self, class_name: str, detail_level: str) -> str:
        """Implementation for python class info - Using new concise format"""
        # Try Python API first
        result = self.python_api.get_class_info(class_name, detail_level)
        if result and "error" not in result:
            formatted_info = self._format_class_info_simple(result, detail_level)
            return formatted_info

        # Try Plugin API as fallback
        result = self.plugin_api.get_class_overview(class_name)
        if result and "error" not in result:
            # Plugin API temporarily uses old format (to be unified later)
            formatted_info = self._format_class_info_enhanced(
                result, detail_level, "Plugin API"
            )
            return f"# 🔌 Plugin API - {class_name}\n\n{formatted_info}"

        return f"Class not found: '{class_name}'"

    def _format_class_info_simple(self, class_info: dict, detail_level: str) -> str:
        """Minimal formatting (using list directly, for Native Accessor)"""
        output = [f"# 🐍 {class_info['name']}\n"]

        # Description
        if class_info.get("description"):
            output.append(f"{class_info['description']}\n")

        properties = class_info.get("properties", [])
        methods = class_info.get("methods", [])

        # Statistics
        output.append("## 📊 Members")
        output.append(f"- Properties: {len(properties)}")
        output.append(f"- Methods: {len(methods)}\n")

        # Property list (concise)
        if properties:
            if detail_level == "overview":
                shown = properties[:10]
                output.append("## Main Properties")
                output.append(", ".join(shown))
                if len(properties) > 10:
                    output.append(f"... (+{len(properties)-10} more)")
            else:
                output.append("## All Properties")
                output.append("\n".join(f"- {p}" for p in properties))

        # Method list (concise)
        if methods:
            if detail_level == "overview":
                shown = methods[:10]
                output.append("\n## Main Methods")
                output.append(", ".join(f"{m}()" for m in shown))
                if len(methods) > 10:
                    output.append(f"... (+{len(methods)-10} more)")
            else:
                output.append("\n## All Methods")
                output.append("\n".join(f"- {m}()" for m in methods))

        # Query hint
        output.append("\n## 💡 Query Details")
        output.append(
            f"Use `api_get_python_member {class_info['name']} <member_name> <property|method>` for detailed info"
        )

        return "\n".join(output)

    def _python_search(self, query: str, scope: str, max_results: int) -> str:
        """Implementation for unified python search - Uses global search uniformly"""
        # Note: scope parameter retained for API compatibility, but uses global search uniformly
        # Reason: Scoped search methods (_search_methods, _search_properties, etc.) are less effective

        return self._search_python_api(query, max_results)

    def _get_python_member_info(
        self, class_name: str, member_name: str, member_type: str
    ) -> str:
        """Enhanced implementation for python member info"""
        # Try Python API first
        result = self.python_api.get_class_member(class_name, member_name, member_type)
        if result and "error" not in result:
            return self._format_member_info_enhanced(result, "Python API")

        # Try Plugin API as fallback
        result = self.plugin_api.get_class_member(class_name, member_name, member_type)
        if result and "error" not in result:
            return self._format_member_info_enhanced(result, "Plugin API")

        return f"Member '{member_name}' not found in class '{class_name}' (type: {member_type})"

    def _format_class_info(self, class_info: dict) -> str:
        """Format class information for display"""
        output = []

        if class_info.get("description"):
            output.append(f"**Description:** {class_info['description']}")

        if class_info.get("methods"):
            output.append(f"**Method count:** {len(class_info['methods'])}")

        if class_info.get("properties"):
            output.append(f"**Property count:** {len(class_info['properties'])}")

        return "\n".join(output) if output else "No information available"

    def _format_class_info_enhanced(
        self, class_info: dict, detail_level: str, source: str
    ) -> str:
        """Enhanced format class information with different detail levels"""
        output = []
        class_name = class_info.get("name", "Unknown")

        # Add source info for context
        # Note: source parameter kept for potential future use

        # Basic description
        if class_info.get("description"):
            output.append(f"**Description:** {class_info['description']}")

        # Inheritance info
        inheritance = class_info.get("inheritance", [])
        if inheritance:
            output.append(f"**Inherits from:** {' → '.join(inheritance)}")

        methods = class_info.get("methods", {})
        properties = class_info.get("properties", {})

        if detail_level == "overview":
            return self._format_overview_level(output, methods, properties, class_name)
        elif detail_level == "detailed":
            return self._format_detailed_level(output, methods, properties, class_name)
        else:  # full
            return self._format_full_level(output, methods, properties, class_name)

    def _format_overview_level(
        self, output: list, methods: dict, properties: dict, class_name: str
    ) -> str:
        """Format overview level information"""
        # Statistics
        output.append("\n### 📊 Member Statistics")
        output.append(f"- **Methods:** {len(methods)}")
        output.append(f"- **Properties:** {len(properties)}")

        # Important methods (first 5)
        if methods:
            output.append("\n### ⚙️ Main Methods")
            method_list = []
            for i, (name, info) in enumerate(methods.items()):
                if i >= 5:
                    remaining = len(methods) - 5
                    method_list.append(f"... (+{remaining} more)")
                    break
                params = info.get("parameters", [])
                param_str = ", ".join([p.get("name", "") for p in params[:3]])
                if len(params) > 3:
                    param_str += ", ..."
                method_list.append(f"`{name}({param_str})`")
            output.append(" ".join(method_list))

        # Important properties (grouped by type, first 10)
        if properties:
            output.append("\n### 📝 Main Properties")
            prop_list = []
            for i, (name, info) in enumerate(properties.items()):
                if i >= 10:
                    remaining = len(properties) - 10
                    prop_list.append(f"... (+{remaining} more)")
                    break
                prop_type = info.get("type", "Any")
                readonly_mark = "●" if info.get("read_only", False) else "○"
                prop_list.append(f"`{name}{readonly_mark}({prop_type})`")
            output.append(" ".join(prop_list))

        # Query guidance
        output.append("\n### 💡 Query Guide")
        output.append(f"- **Full list:** `python_api_class_info {class_name} detailed`")
        output.append(f"- **All details:** `python_api_class_info {class_name} full`")
        output.append(
            f"- **Specific member:** `python_api_member_info {class_name} <member_name>`"
        )
        if len(properties) > 10:
            output.append(
                f'- **Search properties:** `python_api_search "{class_name} properties"`'
            )

        return "\n".join(output)

    def _format_detailed_level(
        self, output: list, methods: dict, properties: dict, class_name: str
    ) -> str:
        """Format detailed level information"""
        # Methods by category
        if methods:
            output.append(f"\n### ⚙️ Methods ({len(methods)})")
            for name, info in methods.items():
                params = info.get("parameters", [])
                param_str = ", ".join([p.get("name", "") for p in params[:2]])
                if len(params) > 2:
                    param_str += ", ..."
                desc = info.get("description", "").split("\n")[0][:60] + (
                    "..." if len(info.get("description", "")) > 60 else ""
                )
                output.append(f"- `{name}({param_str})` - {desc}")

        # Properties by category
        if properties:
            # Categorize properties
            geometry_props = {}
            state_props = {}
            relation_props = {}
            other_props = {}

            for name, info in properties.items():
                prop_type = info.get("type", "Any").lower()
                if any(
                    keyword in name.lower()
                    for keyword in ["bound", "width", "height", "lsb", "rsb", "bsb"]
                ):
                    geometry_props[name] = info
                elif any(
                    keyword in name.lower()
                    for keyword in ["color", "visible", "locked", "selected"]
                ):
                    state_props[name] = info
                elif any(
                    keyword in name.lower()
                    for keyword in ["master", "parent", "font", "layer"]
                ):
                    relation_props[name] = info
                else:
                    other_props[name] = info

            output.append(f"\n### 📝 Properties ({len(properties)})")

            for category, props in [
                ("Geometry", geometry_props),
                ("State", state_props),
                ("Relation", relation_props),
                ("Other", other_props),
            ]:
                if props:
                    output.append(f"\n**{category} Properties:**")
                    for name, info in props.items():
                        prop_type = info.get("type", "Any")
                        readonly_mark = (
                            " [readonly]" if info.get("read_only", False) else ""
                        )
                        desc = info.get("description", "").split(".")[0][:40] + (
                            "..." if len(info.get("description", "")) > 40 else ""
                        )
                        output.append(
                            f"- `{name}` ({prop_type}){readonly_mark} - {desc}"
                        )

        # Query guidance
        output.append("\n### 💡 Deep Query")
        output.append(f"- **Full details:** `python_api_class_info {class_name} full`")
        output.append(
            f"- **Specific member:** `python_api_member_info {class_name} <member_name>`"
        )

        return "\n".join(output)

    def _format_full_level(
        self, output: list, methods: dict, properties: dict, class_name: str
    ) -> str:
        """Format full level information"""
        # All methods with full details
        if methods:
            output.append(f"\n### ⚙️ All Methods ({len(methods)})")
            for name, info in methods.items():
                params = info.get("parameters", [])
                param_details = []
                for param in params:
                    param_name = param.get("name", "")
                    param_type = param.get("type", "Any")
                    param_details.append(f"{param_name}: {param_type}")

                param_str = ", ".join(param_details)
                return_type = info.get("return_type", "None")
                desc = info.get("description", "No description")

                output.append(f"\n**`{name}({param_str}) -> {return_type}`**")
                output.append(f"- {desc}")

                # Show examples if available
                examples = info.get("examples", [])
                if examples:
                    output.append("- Example:")
                    for example in examples[:2]:  # Show first 2 examples
                        output.append(f"  ```python\n  {example}\n  ```")

        # All properties with full details
        if properties:
            output.append(f"\n### 📝 All Properties ({len(properties)})")
            for name, info in properties.items():
                prop_type = info.get("type", "Any")
                readonly_mark = " [readonly]" if info.get("read_only", False) else ""
                desc = info.get("description", "No description")

                output.append(f"\n**`{name}` ({prop_type}){readonly_mark}**")
                output.append(f"- {desc}")

                # Show examples if available
                examples = info.get("examples", [])
                if examples:
                    output.append("- Example:")
                    for example in examples[:1]:  # Show first example
                        output.append(f"  ```python\n  {example}\n  ```")

        # Query guidance
        output.append("\n### 💡 Advanced Query")
        output.append(
            f"- **Specific member details:** `python_api_member_info {class_name} <member_name>`"
        )

        return "\n".join(output)

    def _format_member_info(self, member_info: dict, source: str) -> str:
        """Format member information for display"""
        class_name = member_info.get("class", "Unknown")
        member_name = member_info.get("name", "Unknown")
        member_type = member_info.get("member_type", "unknown")

        # API icon mapping
        api_icons = {"Python API": "🐍", "Objective-C API": "🔧", "Plugin API": "🔌"}
        icon = api_icons.get(source, "📚")

        output = [f"# {icon} {source} - {class_name}.{member_name}\n"]

        # Basic info
        description = member_info.get("description", "No description")
        output.append(f"**📝 Description:** {description}\n")

        # Member type specific info
        if member_type == "property":
            prop_type = member_info.get("type", "Any")
            output.append(f"**🏷️ Type:** `{prop_type}`")

            # Python API specific attributes
            if "read_only" in member_info:
                read_only = "Yes" if member_info.get("read_only") else "No"
                output.append(f"**🔒 Read-only:** {read_only}")

            if "getter" in member_info and member_info.get("getter"):
                output.append(f"**📥 Getter:** `{member_info['getter']}`")

            if "setter" in member_info and member_info.get("setter"):
                output.append(f"**📤 Setter:** `{member_info['setter']}`")

            # Objective-C API specific attributes
            if "attributes" in member_info:
                attributes = member_info.get("attributes", [])
                if attributes:
                    output.append(f"**⚙️ Attributes:** {', '.join(attributes)}")

            if "readonly" in member_info:
                readonly = "Yes" if member_info.get("readonly") else "No"
                output.append(f"**🔒 ReadOnly:** {readonly}")

            # Plugin API specific attributes
            if "required" in member_info:
                required = "Yes" if member_info.get("required") else "No"
                output.append(f"**❗ Required:** {required}")

        elif member_type == "method":
            # Method signature
            if "signature" in member_info and member_info.get("signature"):
                output.append(f"**🔧 Method Signature:** `{member_info['signature']}`")

            # Return type
            return_type = member_info.get("return_type", "None")
            output.append(f"**↩️ Return Type:** `{return_type}`")

            # Parameter info
            parameters = member_info.get("parameters", [])
            if parameters:
                output.append("**📋 Parameters:**")
                for param in parameters[:5]:  # Limit to first 5 parameters
                    if isinstance(param, dict):
                        param_name = param.get("name", "param")
                        param_type = param.get("type", "Any")
                        param_desc = param.get("description", "")
                        if param_desc:
                            output.append(
                                f"  - `{param_name}` ({param_type}): {param_desc}"
                            )
                        else:
                            output.append(f"  - `{param_name}` ({param_type})")
                    else:
                        output.append(f"  - {param}")

                if len(parameters) > 5:
                    output.append(f"  ... {len(parameters) - 5} more parameters")

            # Plugin API specific attributes
            if "required" in member_info:
                required = "Yes" if member_info.get("required") else "No"
                output.append(f"**❗ Required to implement:** {required}")

        # Version info
        version_added = member_info.get("version_added")
        if version_added:
            output.append(f"**📅 Added in version:** {version_added}")

        # Deprecated mark
        deprecated = member_info.get("deprecated", False)
        if deprecated:
            output.append("**⚠️ Deprecated:** Yes")

        # Example code
        examples = member_info.get("examples", [])
        if examples:
            output.append("\n**💡 Usage Examples:**")
            for i, example in enumerate(examples, 1):
                if i <= 3:  # Limit to first 3 examples
                    output.append(f"```python\n{example}\n```")
                elif i == 4:
                    output.append(f"... {len(examples) - 3} more examples")
                    break

        return "\n".join(output)

    def _format_function_info(self, func_info: dict, source: str) -> str:
        """Format function information for display"""
        function_name = func_info.get("function_name", "Unknown")

        # API icon mapping
        api_icons = {"Python API": "🐍", "Objective-C API": "🔧", "Plugin API": "🔌"}
        icon = api_icons.get(source, "📚")

        output = [f"# {icon} {source} - {function_name}()\n"]

        # Basic info
        description = func_info.get("description", "No description")
        output.append(f"**📝 Description:** {description}\n")

        # Function definition
        func_def = func_info.get("function_def", "")
        if func_def:
            output.append(f"**🔧 Function Definition:** `{func_def}`")

        # Return type
        return_type = func_info.get("return_type", "Any")
        output.append(f"**↩️ Return Type:** `{return_type}`")

        # Parameter info
        parameters = func_info.get("parameters", [])
        if parameters:
            output.append("**📋 Parameters:**")
            for param in parameters[:5]:  # Limit to first 5 parameters
                if isinstance(param, dict):
                    param_name = param.get("name", "param")
                    param_type = param.get("type", "Any")
                    param_desc = param.get("description", "")
                    if param_desc:
                        output.append(
                            f"  - `{param_name}` ({param_type}): {param_desc}"
                        )
                    else:
                        output.append(f"  - `{param_name}` ({param_type})")
                else:
                    output.append(f"  - {param}")

            if len(parameters) > 5:
                output.append(f"  ... {len(parameters) - 5} more parameters")

        # Version info
        version_added = func_info.get("version_added")
        if version_added:
            output.append(f"**📅 Added in version:** {version_added}")

        # Deprecated mark
        deprecated = func_info.get("deprecated", False)
        if deprecated:
            output.append("**⚠️ Deprecated:** Yes")

        # Example code
        examples = func_info.get("examples", [])
        if examples:
            output.append("\n**💡 Usage Examples:**")
            for i, example in enumerate(examples, 1):
                if i <= 3:  # Limit to first 3 examples
                    output.append(f"```python\n{example}\n```")
                elif i == 4:
                    output.append(f"... {len(examples) - 3} more examples")
                    break

        return "\n".join(output)

    def _format_member_info_enhanced(self, member_info: dict, source: str) -> str:
        """Enhanced format member information with better organization and examples"""
        class_name = member_info.get("class", "Unknown")
        member_name = member_info.get("name", "Unknown")
        member_type = member_info.get("member_type", "unknown")

        # API icon mapping
        api_icons = {"Python API": "🐍", "Objective-C API": "🔧", "Plugin API": "🔌"}
        icon = api_icons.get(source, "📚")

        output = [f"# {icon} {source} - {class_name}.{member_name}\n"]

        # Basic information
        description = member_info.get("description", "No description")
        output.append(f"**📝 Description:** {description}\n")

        # Member type specific information
        if member_type == "property":
            self._format_property_details(member_info, output)
        elif member_type == "method":
            self._format_method_details(member_info, output)

        # Usage examples (priority display)
        examples = member_info.get("examples", [])
        if examples:
            output.append("\n## 💡 Code Examples")
            for _i, example in enumerate(examples[:3], 1):  # Show first 3
                output.append(f"```python\n{example}\n```")
            if len(examples) > 3:
                output.append(f"*... {len(examples) - 3} more examples*")

        # Related query hints
        output.append("\n## 🔍 Related Queries")
        output.append(f"- **Full class:** `python_api_class_info {class_name}`")
        output.append(f'- **Search similar:** `python_api_search "{member_name}"`')

        return "\n".join(output)

    def _format_property_details(self, member_info: dict, output: list) -> None:
        """Format property-specific details"""
        prop_type = member_info.get("type", "Any")
        output.append(f"**🏷️ Type:** `{prop_type}`")

        # Read/write status
        if "read_only" in member_info:
            read_only = "Yes" if member_info.get("read_only") else "No"
            output.append(f"**🔒 Read-only:** {read_only}")

        # Accessor information
        if "getter" in member_info and member_info.get("getter"):
            output.append(f"**📥 Getter:** `{member_info['getter']}`")

        if "setter" in member_info and member_info.get("setter"):
            output.append(f"**📤 Setter:** `{member_info['setter']}`")

    def _format_method_details(self, member_info: dict, output: list) -> None:
        """Format method-specific details"""
        # Parameter information
        parameters = member_info.get("parameters", [])
        if parameters:
            output.append(f"\n## 📋 Parameters ({len(parameters)})")
            for param in parameters[:5]:  # Show first 5 parameters
                param_name = param.get("name", "unnamed")
                param_type = param.get("type", "Any")
                param_desc = param.get("description", "No description")
                default = param.get("default")

                param_line = f"- **`{param_name}`** ({param_type})"
                if default is not None:
                    param_line += f" = {default}"
                param_line += f" - {param_desc}"
                output.append(param_line)

            if len(parameters) > 5:
                output.append(f"*... {len(parameters) - 5} more parameters*")

        # Return value information
        return_type = member_info.get("return_type")
        if return_type:
            output.append(f"\n**↩️ Returns:** `{return_type}`")

        return_desc = member_info.get("return_description")
        if return_desc:
            output.append(f"**📤 Return description:** {return_desc}")

    def _format_constant_info(self, const_info: dict, source: str) -> str:
        """Format constant information for display"""
        constant_name = const_info.get("constant_name", "Unknown")

        # API icon mapping
        api_icons = {"Python API": "🐍", "Objective-C API": "🔧", "Plugin API": "🔌"}
        icon = api_icons.get(source, "📚")

        output = [f"# {icon} {source} - {constant_name}\n"]

        # Basic information
        description = const_info.get("description", "No description")
        output.append(f"**📝 Description:** {description}\n")

        # Type
        const_type = const_info.get("type", "")
        if const_type:
            output.append(f"**🏷️ Type:** `{const_type}`")

        # Value
        value = const_info.get("value", "")
        if value:
            output.append(f"**💎 Value:** `{value}`")

        # Python API specific - category
        category = const_info.get("category")
        if category:
            output.append(f"**📂 Category:** {category}")

        # Version information
        version_added = const_info.get("version_added")
        if version_added:
            output.append(f"**📅 Added in version:** {version_added}")

        # Deprecated mark
        deprecated = const_info.get("deprecated", False)
        if deprecated:
            output.append("**⚠️ Deprecated:** Yes")

        return "\n".join(output)

    def _add_cross_references(self, query: str, source_type: str) -> str:
        """Add cross-references and recommendations between tools"""
        cross_ref = "\n\n## 🔗 Related Resources\n"

        if source_type == "python_api":
            cross_ref += f'💡 **Find implementation examples:** Use `sdk_search "{query}"` to view related code examples and development guides\n'
            cross_ref += "📚 **More learning resources:**\n"
            cross_ref += f'  - Use `handbook_search "{query}"` to view official manual\n'
            cross_ref += f'  - Use `web_search_tutorials "{query}"` to find online tutorials\n'

        return cross_ref

    # ============================================================================
    # Vanilla Tools Methods (Local Accessor)
    # ============================================================================

    def search_vanilla_ui(self, query: str, max_results: int = 5) -> str:
        """
        [VANILLA UI] Search local vanilla UI components (fully localized)

        Features: Searches UI components from vanilla source code in local Repositories.

        Args:
            query: Search keyword
            max_results: Maximum number of results (default: 5)

        Returns:
            Formatted search results or installation guide
        """
        if not self.vanilla_tools:
            from glyphs_info_mcp.shared.core.installation_helper import InstallationHelper

            return InstallationHelper.get_installation_message("vanilla")

        return self.vanilla_tools.search_vanilla_ui(query, max_results)

    def get_vanilla_ui(self, ui_item: str, include_source: bool = True) -> str:
        """
        [VANILLA UI] Get complete information for vanilla UI components

        Features: Reads complete source code and documentation for vanilla UI components from local Repositories.

        Args:
            ui_item: UI component name (e.g., "Button", "TextBox")
            include_source: Whether to include complete source code (default: True)

        Returns:
            Formatted UI component information or installation guide
        """
        if not self.vanilla_tools:
            from glyphs_info_mcp.shared.core.installation_helper import InstallationHelper

            return InstallationHelper.get_installation_message("vanilla")

        return self.vanilla_tools.get_vanilla_ui(ui_item, include_source)

    def list_vanilla_ui(self) -> str:
        """
        [VANILLA UI] List all available vanilla UI components

        Features: Lists all available vanilla UI components in local Repositories.

        Returns:
            Formatted UI component list or installation guide
        """
        if not self.vanilla_tools:
            from glyphs_info_mcp.shared.core.installation_helper import InstallationHelper

            return InstallationHelper.get_installation_message("vanilla")

        return self.vanilla_tools.list_vanilla_ui()

    # ============================================================================
    # API Structure Query Tools (Issue #51)
    # ============================================================================

    def api_get_class_hierarchy(self, format: str = "tree") -> str:
        """
        [API STRUCTURE] Get complete Glyphs API class hierarchy structure

        Features: Provides a structured view of Glyphs API, including inheritance, composition, and protocol implementations

        Args:
            format: Output format
                - "tree": ASCII tree diagram (default)
                - "json": JSON structured data
                - "mermaid": Mermaid chart syntax

        Returns:
            Contains the following information:
            - Inheritance Hierarchy
            - Composition Hierarchy
            - Protocol Implementation
        """
        if not self.is_initialized:
            return "API module not initialized"

        if format not in ["tree", "json", "mermaid"]:
            return f"Invalid format: {format}. Supported values: tree, json, mermaid"

        return self._get_class_hierarchy(format)

    def api_get_class_relationships(
        self, class_name: str, include_examples: bool = True
    ) -> str:
        """
        [API STRUCTURE] Get all relationship information for a specific class

        Features: Displays complete relationship diagram for a specific class, including parent classes, child classes, containment relationships, etc.

        Args:
            class_name: Class name (e.g., "GSLayer", "GSPath")
            include_examples: Whether to include code examples (default: True)

        Returns:
            - Parent Class
            - Child Classes
            - Contains/Has-Many
            - Contained By/Belongs To
            - Implements Protocols
            - References
            - Referenced By
            - Navigation example code
        """
        if not self.is_initialized:
            return "API module not initialized"

        return self._get_class_relationships(class_name, include_examples)

    def api_navigate_structure(
        self,
        start_class: str,
        relationship: str,
        depth: int = 1,
        show_path: bool = True,
    ) -> str:
        """
        [API STRUCTURE] Navigate class structure relationships

        Features: Starts from a specified class, navigates along specific relationship direction, displays hierarchy structure and access paths

        Args:
            start_class: Starting class (e.g., "GSNode")
            relationship: Navigation direction
                - "parent": Search upward for parent classes
                - "children": Search downward for child classes
                - "contains": View contained objects
                - "contained_by": View what contains this class
            depth: Navigation depth (1-5)
            show_path: Whether to show code access paths

        Returns:
            Structured navigation results containing:
            - Hierarchy structure diagram
            - Class information for each level
            - Access path examples (if show_path=True)

        Example:
            api_navigate_structure("GSNode", "contained_by", depth=3)

            Result:
            GSNode (contained by)
            └── GSPath.nodes: List[GSNode]
                └── GSLayer.shapes: List[GSShape]
                    └── GSGlyph.layers: List[GSLayer]

            Access Path:
            node.parent → GSPath
            node.parent.parent → GSLayer
            node.parent.parent.parent → GSGlyph
        """
        if not self.is_initialized:
            return "API module not initialized"

        if relationship not in ["parent", "children", "contains", "contained_by"]:
            return f"Invalid relationship: {relationship}. Supported values: parent, children, contains, contained_by"

        if not (1 <= depth <= 5):
            return f"Invalid depth: {depth}. Range: 1-5"

        return self._navigate_structure(start_class, relationship, depth, show_path)

    # ========== Private Helper Methods (API Structure) ==========

    def _load_api_structure(self) -> dict:
        """Load API structure data from class_hierarchy module.

        Uses the new class_hierarchy.py module which derives data from
        the official Glyphs object model diagram.

        Source: https://docu.glyphsapp.com/_images/objectmodel.png
        """
        return build_structure_dict()

    def _get_class_hierarchy(self, format: str) -> str:
        """Implement class hierarchy query"""
        structure = self._load_api_structure()
        if not structure or "classes" not in structure:
            return "Failed to load API structure data"

        if format == "tree":
            return self._format_hierarchy_tree(structure)
        elif format == "json":
            return json.dumps(structure, ensure_ascii=False, indent=2)
        elif format == "mermaid":
            return self._format_hierarchy_mermaid(structure)

        return "Unsupported format"

    def _format_hierarchy_tree(self, structure: dict) -> str:
        """Format as ASCII tree diagram.

        Dynamically generates tree from COMPOSITION data in class_hierarchy module.
        Source: https://docu.glyphsapp.com/_images/objectmodel.png
        """
        output = ["# Glyphs API Class Hierarchy\n"]
        output.append(f"Source: {OFFICIAL_DIAGRAM_URL}\n")

        # Main structure: starting from Glyphs.app
        output.append("## Composition Hierarchy\n")
        output.append("```")
        output.append("Glyphs.app")
        output.append("├── Styles")
        output.append("│   └── AxisValues ←─(axisID)─ Axes")
        output.append("└── Fonts")
        output.append("    ├── Masters")
        output.append("    │   └── AxisValues ←─(axisID)─ Axes")
        output.append("    ├── Axes")
        output.append("    ├── Glyphs")
        output.append("    │   └── Layers ←─(masterID)─ Masters")
        output.append("    │       ├── Shapes")
        output.append("    │       │   ├── Paths")
        output.append("    │       │   │   └── Nodes")
        output.append("    │       │   └── Components")
        output.append("    │       ├── Anchors")
        output.append("    │       ├── Hints")
        output.append("    │       └── Guides")
        output.append("    ├── Features")
        output.append("    └── Classes")
        output.append("```\n")

        # Inheritance hierarchy
        output.append("## Inheritance Hierarchy\n")
        output.append("```")
        output.append("GSShape (abstract class)")
        output.append("├── GSPath")
        output.append("└── GSComponent")
        output.append("```\n")

        # Key relationships (ID references - dashed lines in diagram)
        output.append("## Key Relationships (ID References)\n")
        output.append("- **axisID**: Links Axes ↔ AxisValues (in both Styles and Masters)")
        output.append("- **masterID**: Links Masters ↔ Layers")

        return "\n".join(output)

    def _format_hierarchy_mermaid(self, structure: dict) -> str:
        """Format as Mermaid chart syntax.

        Source: https://docu.glyphsapp.com/_images/objectmodel.png
        """
        output = ["```mermaid", "graph TD"]

        # Root
        output.append('    Glyphs["Glyphs.app"]')

        # Glyphs.app children
        output.append("    Glyphs --> Styles")
        output.append("    Glyphs --> Fonts")

        # Styles branch
        output.append("    Styles --> AxisValues1[AxisValues]")

        # Fonts branch - main children
        output.append("    Fonts --> Masters")
        output.append("    Fonts --> Axes")
        output.append("    Fonts --> Glyphs2[Glyphs]")
        output.append("    Fonts --> Features")
        output.append("    Fonts --> Classes")

        # Masters branch
        output.append("    Masters --> AxisValues2[AxisValues]")

        # Glyphs branch
        output.append("    Glyphs2 --> Layers")

        # Layers branch
        output.append("    Layers --> Shapes")
        output.append("    Layers --> Anchors")
        output.append("    Layers --> Hints")
        output.append("    Layers --> Guides")

        # Shapes branch (inheritance)
        output.append("    Shapes --> Paths")
        output.append("    Shapes --> Components")

        # Paths branch
        output.append("    Paths --> Nodes")

        # ID references (dashed lines)
        output.append("    Axes -.->|axisID| AxisValues1")
        output.append("    Axes -.->|axisID| AxisValues2")
        output.append("    Masters -.->|masterID| Layers")

        output.append("```")
        return "\n".join(output)

    def _get_class_relationships(self, class_name: str, include_examples: bool) -> str:
        """Implement class relationship query"""
        structure = self._load_api_structure()
        if not structure or "classes" not in structure:
            return "Failed to load API structure data"

        # Find class
        class_info = structure["classes"].get(class_name)
        if not class_info:
            # Try fuzzy matching
            matches = [
                c
                for c in structure["classes"].keys()
                if class_name.lower() in c.lower()
            ]
            if matches:
                return f"Class '{class_name}' not found. Did you mean: {', '.join(matches[:5])}?"
            return f"Class '{class_name}' not found"

        output = [f"# {class_name} - Class Relationships\n"]

        # Description
        if class_info.get("description"):
            output.append(f"**Description:** {class_info['description']}\n")

        # Parent class
        if class_info.get("parent"):
            output.append("## 🔼 Parent Class")
            output.append(f"- {class_info['parent']}\n")

        # Child classes
        if class_info.get("children"):
            output.append("## 🔽 Child Classes")
            for child in class_info["children"]:
                output.append(f"- {child}")
            output.append("")

        # Contained objects
        if class_info.get("contains"):
            output.append("## 📦 Contains (Has-Many)")
            for contained in class_info["contains"]:
                property_info = class_info.get("properties", {})
                prop_name = None
                # Find corresponding property name
                for prop, details in property_info.items():
                    if contained in details.get("type", ""):
                        prop_name = prop
                        break
                if prop_name:
                    output.append(f"- **{contained}** (via `{prop_name}` property)")
                else:
                    output.append(f"- {contained}")
            output.append("")

        # Contained by
        if class_info.get("contained_by"):
            output.append("## 📥 Contained By (Belongs To)")
            for container in class_info["contained_by"]:
                output.append(f"- {container}")
            output.append("")

        # Referenced classes - Issue #53
        if class_info.get("references"):
            output.append("## 🔗 References")
            for ref_class in class_info["references"]:
                output.append(f"- {ref_class}")
            output.append("")

        # Referenced by - Issue #53
        # Reverse lookup: iterate all classes to find those referencing current class
        referenced_by = []
        for cls_name, cls_data in structure["classes"].items():
            if cls_data.get("references") and class_name in cls_data["references"]:
                referenced_by.append(cls_name)

        if referenced_by:
            output.append("## 🔍 Referenced By")
            for ref_by in referenced_by:
                output.append(f"- {ref_by}")
            output.append("")

        # Implements Protocols - Issue #53
        # TODO: Future extension point - need to add 'implements' field in api_structure.json
        # Example data format:
        # "implements": ["NSCopying", "NSCoding", "NSSecureCoding"]
        # When data is available, use the following logic:
        #
        # if class_info.get('implements'):
        #     output.append(f"## 📜 Implements Protocols")
        #     for protocol in class_info['implements']:
        #         output.append(f"- {protocol}")
        #     output.append("")

        # Code examples
        if include_examples and class_info.get("access_paths"):
            output.append("## 💡 Access Path Examples")
            output.append("```python")
            for path in class_info["access_paths"]:
                output.append(f"# {path}")
            output.append("```")

        return "\n".join(output)

    def _navigate_structure(
        self, start_class: str, relationship: str, depth: int, show_path: bool
    ) -> str:
        """Implement structure navigation"""
        structure = self._load_api_structure()
        if not structure or "classes" not in structure:
            return "Failed to load API structure data"

        # Find starting class
        class_info = structure["classes"].get(start_class)
        if not class_info:
            return f"Class '{start_class}' not found"

        output = [f"# {start_class} - {relationship} Navigation (depth {depth})\n"]

        # Execute navigation
        navigation_result = self._navigate_recursive(
            start_class, relationship, depth, 0, structure, []
        )

        output.append("## Structure Diagram\n")
        output.append("```")
        output.extend(navigation_result["tree"])
        output.append("```\n")

        # Display access paths
        if show_path and navigation_result["paths"]:
            output.append("## Access Paths\n")
            output.append("```python")
            for path in navigation_result["paths"]:
                output.append(path)
            output.append("```")

        return "\n".join(output)

    def _navigate_recursive(
        self,
        class_name: str,
        relationship: str,
        max_depth: int,
        current_depth: int,
        structure: dict,
        path: list,
    ) -> dict:
        """Recursively navigate class structure"""
        if current_depth >= max_depth:
            return {"tree": [], "paths": []}

        class_info = structure["classes"].get(class_name)
        if not class_info:
            return {"tree": [], "paths": []}

        indent = "    " * current_depth
        prefix = "└── " if current_depth > 0 else ""

        tree_lines = []
        path_lines = []

        # Navigate based on relationship type
        if relationship == "contained_by":
            containers = class_info.get("contained_by", [])
            for container in containers:
                tree_lines.append(f"{indent}{prefix}{container}")
                # Generate access path
                if current_depth == 0:
                    path_lines.append(f"{class_name.lower()}.parent → {container}")
                else:
                    parent_chain = ".parent" * (current_depth + 1)
                    path_lines.append(
                        f"{class_name.lower()}{parent_chain} → {container}"
                    )

                # Recurse
                sub_result = self._navigate_recursive(
                    container,
                    relationship,
                    max_depth,
                    current_depth + 1,
                    structure,
                    path + [container],
                )
                tree_lines.extend(sub_result["tree"])
                path_lines.extend(sub_result["paths"])

        elif relationship == "contains":
            contained = class_info.get("contains", [])
            for item in contained:
                tree_lines.append(f"{indent}{prefix}{item}")
                # Recurse
                sub_result = self._navigate_recursive(
                    item,
                    relationship,
                    max_depth,
                    current_depth + 1,
                    structure,
                    path + [item],
                )
                tree_lines.extend(sub_result["tree"])
                path_lines.extend(sub_result["paths"])

        elif relationship == "parent":
            parent = class_info.get("parent")
            if parent:
                tree_lines.append(f"{indent}{prefix}{parent}")
                # Generate access path
                if current_depth == 0:
                    path_lines.append(f"{class_name} inherits from {parent}")

                # Recurse
                sub_result = self._navigate_recursive(
                    parent,
                    relationship,
                    max_depth,
                    current_depth + 1,
                    structure,
                    path + [parent],
                )
                tree_lines.extend(sub_result["tree"])
                path_lines.extend(sub_result["paths"])

        elif relationship == "children":
            children = class_info.get("children", [])
            for child in children:
                tree_lines.append(f"{indent}{prefix}{child}")
                # Generate access path
                if current_depth == 0:
                    path_lines.append(f"{child} inherits from {class_name}")

                # Recurse
                sub_result = self._navigate_recursive(
                    child,
                    relationship,
                    max_depth,
                    current_depth + 1,
                    structure,
                    path + [child],
                )
                tree_lines.extend(sub_result["tree"])
                path_lines.extend(sub_result["paths"])

        return {"tree": tree_lines, "paths": path_lines}

    # ============================================================================
    # Module Information
    # ============================================================================

    def get_module_info(self) -> dict[str, Any]:
        """Get module information"""
        # Use statistics provided by Native Accessor
        python_classes = (
            len(self.python_api.symbols.get("classes", []))
            if hasattr(self.python_api, "symbols")
            else 0
        )
        plugin_classes = (
            len(self.sdk_accessor.list_plugin_classes()) if self.sdk_accessor else 0
        )
        drawing_funcs = (
            len(self.sdk_accessor.list_drawing_functions()) if self.sdk_accessor else 0
        )

        info = {
            "name": self.name,
            "type": "unified_api",
            "initialized": self.is_initialized,
            "python_classes": python_classes,
            "drawing_functions": drawing_funcs,
            "plugin_classes": plugin_classes,
            "tools": list(self.get_tools().keys()),
        }

        # Add websearch API info if available
        if self.websearch_api_module and self.websearch_api_module.is_initialized:
            websearch_info = self.websearch_api_module.get_module_info()
            info["websearch_api"] = {
                "objc_api_items_count": websearch_info.get("objc_api_items_count", 0),
                "vanilla_items_count": websearch_info.get("vanilla_items_count", 0),
                "tools": websearch_info.get("tools", []),
            }

        # Add API module info (Header functionality) if available
        if self.objc_api_module and self.objc_api_module.is_initialized:
            api_info = self.objc_api_module.get_module_info()
            info["api_headers"] = {
                "header_files_count": api_info.get("header_files_count", 0),
                "objc_classes": api_info.get("objc_classes", 0),
                "tools": ["search_objc_api_headers", "get_objc_header"],
            }

        return info
