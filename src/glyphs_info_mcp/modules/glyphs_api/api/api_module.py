#!/usr/bin/env python3
"""
API search module for Glyphs.app API documentation
"""

import json
import logging
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

# Use shared core library
project_root = Path(__file__).parent.parent.parent.parent
shared_core_path = str(project_root / "src" / "shared")
if shared_core_path not in sys.path:
    sys.path.insert(0, shared_core_path)

from glyphs_info_mcp.shared.core.base_module import BaseMCPModule

# Set up logger
logger = logging.getLogger(__name__)

# Import local Header functionality - using absolute path import
import importlib.util


def import_local_module(file_path: str, module_name: str) -> ModuleType:
    """Dynamically import local module"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Get current directory
current_dir = Path(__file__).parent

# Dynamically import Header related modules
HeaderSearchEngine: type[Any] | None = None
HeaderParser: type[Any] | None = None
try:
    header_search_module = import_local_module(
        str(current_dir / "objc_header_search.py"), "objc_header_search"
    )
    HeaderSearchEngine = header_search_module.HeaderSearchEngine

    header_parser_module = import_local_module(
        str(current_dir / "objc_header_parser.py"), "objc_header_parser"
    )
    HeaderParser = header_parser_module.HeaderParser
except Exception as e:
    logger.warning(f"Failed to import Header modules: {e}")
    HeaderSearchEngine = None
    HeaderParser = None


class APIModule(BaseMCPModule):
    """API documentation search module"""

    def __init__(self, name: str, data_path: Path | None = None):
        super().__init__(name, data_path)
        self.python_api: dict[str, Any] = {}
        self.objc_api: dict[str, Any] = {}
        self.drawing_tools: dict[str, Any] = {}
        self.plugins: dict[str, Any] = {}

        # Header search related attributes
        self.header_search_engine: Any = None
        self.header_parser: Any = None
        self.search_engine: Any = None  # Unified search engine (injected by server.py)

    def initialize(self) -> bool:
        """Initialize the API module (Header search only for Native Accessor architecture)"""
        try:
            # Native Accessor architecture: only initialize Header search functionality
            # No need to load JSON files (data/api directory dependency removed)
            self._initialize_header_search()

            self.is_initialized = True

            header_files_count = (
                self.header_search_engine.get_indexed_files_count()
                if self.header_search_engine
                else 0
            )

            logger.info(
                f"API module initialized with {header_files_count} header files (Native Accessor mode)"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to initialize API module: {e}")
            return False

    def _load_api_data(self, api_path: Path) -> None:
        """Load API data from JSON files"""
        try:
            # Load Python API
            python_file = api_path / "python_api.json"
            if python_file.exists():
                self.python_api = json.loads(python_file.read_text(encoding="utf-8"))

            # Load Objective-C API
            objc_file = api_path / "objc_api.json"
            if objc_file.exists():
                self.objc_api = json.loads(objc_file.read_text(encoding="utf-8"))

            # Load Drawing Tools
            drawing_file = api_path / "drawing_tools.json"
            if drawing_file.exists():
                self.drawing_tools = json.loads(
                    drawing_file.read_text(encoding="utf-8")
                )

            # Load Plugins
            plugins_file = api_path / "plugins.json"
            if plugins_file.exists():
                self.plugins = json.loads(plugins_file.read_text(encoding="utf-8"))

        except Exception as e:
            logger.error(f"Failed to load API data: {e}")

    def _initialize_header_search(self) -> None:
        """Initialize Header search functionality"""
        try:
            if HeaderSearchEngine is None or HeaderParser is None:
                logger.warning(
                    "Header modules not available, skipping header search initialization"
                )
                self.header_search_engine = None
                self.header_parser = None
                self.headers_base_path = None
                return

            # Create Header search engine and parser
            self.header_search_engine = HeaderSearchEngine()
            self.header_parser = HeaderParser()

            # Detect Glyphs 3 Headers path
            import os

            # Prefer environment variable
            env_headers_path = os.getenv("GLYPHS_APP_HEADERS_PATH")
            if env_headers_path:
                headers_path = Path(env_headers_path)
            else:
                # Use default Glyphs 3.app path
                headers_path = Path(
                    "/Applications/Glyphs 3.app/Contents/Frameworks/GlyphsCore.framework/Versions/A/Headers"
                )

            # Check if path exists
            if headers_path.exists():
                self.headers_base_path = headers_path
                self.header_search_engine.build_index_from_directory(headers_path)
                logger.info(
                    f"Header search engine initialized with Glyphs 3 Headers: {headers_path}"
                )
                logger.info(
                    f"   Indexed {self.header_search_engine.get_indexed_files_count()} header files"
                )
            else:
                logger.warning(
                    f"Glyphs 3 Headers directory not found: {headers_path}"
                )
                logger.warning(
                    "   Please ensure Glyphs 3 is installed at: /Applications/Glyphs 3.app"
                )
                logger.warning(
                    "   Or set GLYPHS_APP_HEADERS_PATH environment variable to custom location"
                )
                self.headers_base_path = None

        except Exception as e:
            logger.error(f"Failed to initialize header search: {e}")
            self.header_search_engine = None
            self.header_parser = None
            self.headers_base_path = None

    def set_search_engine(self, search_engine: Any) -> None:
        """Set unified search engine (called by server.py)"""
        self.search_engine = search_engine

    def register_tools(self, mcp_instance: Any) -> None:
        """Register MCP tools for API functionality"""

        @mcp_instance.tool()
        def search_python_api(query: str, search_type: str = "all") -> str:
            """
            Search Python API documentation

            Args:
                query: Search query
                search_type: Type of search ('classes', 'methods', 'properties', 'all')

            Returns:
                Search results from Python API
            """
            if not self.is_initialized:
                return "API module not initialized"

            return self._search_python_api(query, search_type)

        @mcp_instance.tool()
        def search_objc_api(query: str, search_type: str = "all") -> str:
            """
            Search Objective-C API documentation

            Args:
                query: Search query
                search_type: Type of search ('classes', 'methods', 'properties', 'all')

            Returns:
                Search results from Objective-C API
            """
            if not self.is_initialized:
                return "API module not initialized"

            return self._search_objc_api(query, search_type)

        @mcp_instance.tool()
        def search_drawing_tools(query: str) -> str:
            """
            Search Drawing Tools API

            Args:
                query: Search query

            Returns:
                Search results from Drawing Tools API
            """
            if not self.is_initialized:
                return "API module not initialized"

            return self._search_drawing_tools(query)

        @mcp_instance.tool()
        def search_plugins_api(query: str) -> str:
            """
            Search Plugins API documentation

            Args:
                query: Search query

            Returns:
                Search results from Plugins API
            """
            if not self.is_initialized:
                return "API module not initialized"

            return self._search_plugins_api(query)

        @mcp_instance.tool()
        def get_class_details(class_name: str, api_type: str = "python") -> str:
            """
            Get detailed information about a specific class

            Args:
                class_name: Name of the class
                api_type: API type ('python' or 'objc')

            Returns:
                Detailed class information
            """
            if not self.is_initialized:
                return "API module not initialized"

            return self._get_class_details(class_name, api_type)

        @mcp_instance.tool()
        def get_api_overview() -> str:
            """
            Get overview of available APIs

            Returns:
                Summary of all available APIs
            """
            if not self.is_initialized:
                return "API module not initialized"

            return self._get_api_overview()

        # Header search related tools
        @mcp_instance.tool()
        def api_search_objc_headers(query: str, max_results: int = 5) -> str:
            """
            [OBJECTIVE-C HEADERS] Search Objective-C Header files

            Search within 174 Header files in GlyphsCore.framework. These Headers
            define core protocols and classes for Objective-C plugin development, serving as the foundation for Xcode development.

            Use cases:
            - View Objective-C plugin protocol definitions (e.g., GlyphsReporterProtocol)
            - Confirm complete properties and method signatures of classes
            - API reference for Xcode plugin development

            Related tools:
            - Use sdk_list_xcode_templates to view complete Xcode templates
            - Use sdk_list_xcode_samples to view actual sample projects

            Args:
                query: Search keyword (class name, method name, protocol name)
                max_results: Maximum number of results (default: 5)

            Returns:
                List of matching Header files and related content
            """
            if not self.is_initialized:
                return "API module not initialized"

            return self._search_objc_api_headers(query, max_results)

        @mcp_instance.tool()
        def api_get_objc_header(header_query: str) -> str:
            """
            [OBJECTIVE-C HEADERS] Get Objective-C Header file content

            Get complete Header content by file name or class name. Header files contain
            Objective-C protocol definitions, class interfaces, and method declarations,
            serving as core reference material for Xcode plugin development.

            Use cases:
            - View complete protocol definitions and method signatures
            - Confirm class properties and method lists
            - API documentation for Xcode plugin development

            Related tools:
            - Use sdk_get_xcode_template to view template code using these Headers
            - Use sdk_get_xcode_sample to view actual usage examples

            Args:
                header_query: Header file name or class name (e.g., "GSFont", "GSFont.h")

            Returns:
                Complete Header file content
            """
            if not self.is_initialized:
                return "API module not initialized"

            return self._get_objc_header(header_query)

    def _search_python_api(self, query: str, search_type: str = "all") -> str:
        """Search Python API"""
        if not query.strip():
            return "Please provide a search query"

        results = []
        query_lower = query.lower()

        classes = self.python_api.get("classes", [])

        for cls in classes:
            class_name = cls.get("name", "")

            # Search class name
            if search_type in ["all", "classes"] and query_lower in class_name.lower():
                results.append(
                    {
                        "type": "class",
                        "name": class_name,
                        "description": cls.get("description", ""),
                        "class": class_name,
                    }
                )

            # Search methods
            if search_type in ["all", "methods"]:
                for method in cls.get("methods", []):
                    method_name = method.get("name", "")
                    if query_lower in method_name.lower():
                        results.append(
                            {
                                "type": "method",
                                "name": method_name,
                                "description": method.get("description", ""),
                                "class": class_name,
                                "signature": method.get("signature", ""),
                            }
                        )

            # Search properties
            if search_type in ["all", "properties"]:
                for prop in cls.get("properties", []):
                    prop_name = prop.get("name", "")
                    if query_lower in prop_name.lower():
                        results.append(
                            {
                                "type": "property",
                                "name": prop_name,
                                "description": prop.get("description", ""),
                                "class": class_name,
                                "type_info": prop.get("type", ""),
                            }
                        )

        if not results:
            return f"No Python API results found for '{query}'"

        return self._format_api_results("Python API", query, results[:10])

    def _search_objc_api(self, query: str, search_type: str = "all") -> str:
        """Search Objective-C API"""
        if not query.strip():
            return "Please provide a search query"

        results = []
        query_lower = query.lower()

        classes = self.objc_api.get("classes", [])

        for cls in classes:
            class_name = cls.get("name", "")

            # Search class name
            if search_type in ["all", "classes"] and query_lower in class_name.lower():
                results.append(
                    {
                        "type": "class",
                        "name": class_name,
                        "description": cls.get("description", ""),
                        "class": class_name,
                    }
                )

            # Search methods
            if search_type in ["all", "methods"]:
                for method in cls.get("methods", []):
                    method_name = method.get("name", "")
                    if query_lower in method_name.lower():
                        results.append(
                            {
                                "type": "method",
                                "name": method_name,
                                "description": method.get("description", ""),
                                "class": class_name,
                                "signature": method.get("signature", ""),
                            }
                        )

            # Search properties
            if search_type in ["all", "properties"]:
                for prop in cls.get("properties", []):
                    prop_name = prop.get("name", "")
                    if query_lower in prop_name.lower():
                        results.append(
                            {
                                "type": "property",
                                "name": prop_name,
                                "description": prop.get("description", ""),
                                "class": class_name,
                                "type_info": prop.get("type", ""),
                            }
                        )

        if not results:
            return f"No Objective-C API results found for '{query}'"

        return self._format_api_results("Objective-C API", query, results[:10])

    def _search_drawing_tools(self, query: str) -> str:
        """Search Drawing Tools API"""
        if not query.strip():
            return "Please provide a search query"

        results = []
        query_lower = query.lower()

        functions = self.drawing_tools.get("functions", [])

        for func in functions:
            func_name = func.get("name", "")
            if (
                query_lower in func_name.lower()
                or query_lower in func.get("description", "").lower()
            ):
                results.append(
                    {
                        "type": "function",
                        "name": func_name,
                        "description": func.get("description", ""),
                        "signature": func.get("signature", ""),
                        "parameters": func.get("parameters", []),
                    }
                )

        if not results:
            return f"No Drawing Tools results found for '{query}'"

        return self._format_drawing_tools_results(query, results[:10])

    def _search_plugins_api(self, query: str) -> str:
        """Search Plugins API"""
        if not query.strip():
            return "Please provide a search query"

        results = []
        query_lower = query.lower()

        plugins = self.plugins.get("plugins", [])

        for plugin in plugins:
            plugin_name = plugin.get("name", "")
            if (
                query_lower in plugin_name.lower()
                or query_lower in plugin.get("description", "").lower()
            ):
                results.append(
                    {
                        "type": "plugin",
                        "name": plugin_name,
                        "description": plugin.get("description", ""),
                        "category": plugin.get("category", ""),
                        "methods": plugin.get("methods", []),
                    }
                )

        if not results:
            return f"No Plugins API results found for '{query}'"

        return self._format_plugins_results(query, results[:10])

    def _get_class_details(self, class_name: str, api_type: str = "python") -> str:
        """Get detailed class information"""
        api_data = self.python_api if api_type == "python" else self.objc_api
        classes = api_data.get("classes", [])

        for cls in classes:
            if cls.get("name", "").lower() == class_name.lower():
                return self._format_class_details(cls, api_type)

        return f"Class '{class_name}' not found in {api_type} API"

    def _format_class_details(self, cls: dict, api_type: str) -> str:
        """Format detailed class information"""
        output = [f"# {cls.get('name', 'Unknown')} ({api_type.title()} API)\n"]

        if cls.get("description"):
            output.append(f"**Description:** {cls['description']}\n")

        if cls.get("properties"):
            output.append("## Properties\n")
            for prop in cls["properties"][:10]:  # Limit to 10
                output.append(f"- **{prop.get('name', '')}** ({prop.get('type', '')})")
                if prop.get("description"):
                    output.append(f"  {prop['description'][:100]}...")
                output.append("")

        if cls.get("methods"):
            output.append("## Methods\n")
            for method in cls["methods"][:10]:  # Limit to 10
                output.append(f"- **{method.get('name', '')}**")
                if method.get("signature"):
                    output.append(f"  `{method['signature']}`")
                if method.get("description"):
                    output.append(f"  {method['description'][:100]}...")
                output.append("")

        return "\n".join(output)

    def _format_api_results(
        self, api_name: str, query: str, results: list[dict]
    ) -> str:
        """Format API search results"""
        output = [f"# {api_name} Search Results: \"{query}\"\n"]
        output.append(f"Found {len(results)} results\n")

        for i, result in enumerate(results, 1):
            output.append(f"## {i}. {result['name']} ({result['type']})")

            if result.get("class"):
                output.append(f"**Class:** {result['class']}")

            if result.get("signature"):
                output.append(f"**Signature:** `{result['signature']}`")

            if result.get("type_info"):
                output.append(f"**Type:** {result['type_info']}")

            if result.get("description"):
                desc = (
                    result["description"][:200] + "..."
                    if len(result["description"]) > 200
                    else result["description"]
                )
                output.append(f"**Description:** {desc}")

            output.append("")

        return "\n".join(output)

    def _format_drawing_tools_results(self, query: str, results: list[dict]) -> str:
        """Format Drawing Tools results"""
        output = [f"# Drawing Tools Search Results: \"{query}\"\n"]
        output.append(f"Found {len(results)} functions\n")

        for i, result in enumerate(results, 1):
            output.append(f"## {i}. {result['name']}")

            if result.get("signature"):
                output.append(f"**Signature:** `{result['signature']}`")

            if result.get("description"):
                output.append(f"**Description:** {result['description']}")

            if result.get("parameters"):
                output.append("**Parameters:**")
                for param in result["parameters"]:
                    output.append(f"- {param}")

            output.append("")

        return "\n".join(output)

    def _format_plugins_results(self, query: str, results: list[dict]) -> str:
        """Format Plugins results"""
        output = [f"# Plugins API Search Results: \"{query}\"\n"]
        output.append(f"Found {len(results)} plugins\n")

        for i, result in enumerate(results, 1):
            output.append(f"## {i}. {result['name']}")

            if result.get("category"):
                output.append(f"**Category:** {result['category']}")

            if result.get("description"):
                output.append(f"**Description:** {result['description']}")

            if result.get("methods"):
                output.append(f"**Methods:** {len(result['methods'])} available")

            output.append("")

        return "\n".join(output)

    def _get_api_overview(self) -> str:
        """Get API overview"""
        output = ["# 📚 Glyphs.app API Overview\n"]

        # Python API stats
        python_classes = len(self.python_api.get("classes", []))
        output.append("## Python API")
        output.append(f"- **Classes:** {python_classes}")

        # Objective-C API stats
        objc_classes = len(self.objc_api.get("classes", []))
        output.append("## Objective-C API")
        output.append(f"- **Classes:** {objc_classes}")

        # Drawing Tools stats
        drawing_functions = len(self.drawing_tools.get("functions", []))
        output.append("## Drawing Tools")
        output.append(f"- **Functions:** {drawing_functions}")

        # Plugins stats
        plugin_count = len(self.plugins.get("plugins", []))
        output.append("## Plugins")
        output.append(f"- **Plugins:** {plugin_count}")

        output.append(
            f"\n**Total API Items:** {python_classes + objc_classes + drawing_functions + plugin_count}"
        )

        return "\n".join(output)

    def _search_objc_api_headers(self, query: str, max_results: int = 5) -> str:
        """Search Objective-C Header files"""
        if not query.strip():
            return "Please provide a search keyword"

        # Use unified search engine for vocabulary conversion (if available)
        processed_query = query
        user_language = "zh"

        if self.search_engine and self.search_engine.query_processor:
            processed_query, user_language = (
                self.search_engine.query_processor.preprocess_query(query)
            )

        # If header_search_engine is available, use it first
        if self.header_search_engine:
            results = self.header_search_engine.search(processed_query, max_results)
            if results:
                return self._format_header_search_results(
                    results, query, processed_query, user_language
                )

        # Otherwise search existing API list files
        results = self._search_api_list_files(processed_query, max_results)

        if not results:
            return f"No Objective-C API items found related to '{query}'"

        # Format results
        output = [f"# 🔍 Found {len(results)} Objective-C API results"]
        output.append(f"**Search keyword:** {query}")

        if processed_query != query:
            output.append(f"**Processed query:** {processed_query}")

        output.append("")

        for i, result in enumerate(results, 1):
            output.append(f"## {i}. {result['name']}")
            output.append(f"**Type:** {result['type']}")
            output.append(f"**Relevance score:** {result['score']:.2f}")
            if result.get("url"):
                output.append(f"**Documentation URL:** {result['url']}")
            output.append("")

        formatted_result = "\n".join(output)

        # Use unified search engine for post-processing (if available)
        if self.search_engine and self.search_engine.query_processor:
            return self.search_engine.query_processor.postprocess_output(
                formatted_result, user_language
            )
        else:
            return formatted_result

    def _format_header_search_results(
        self, results: list[dict], query: str, processed_query: str, user_language: str
    ) -> str:
        """Format raw Header search results"""
        output = [f"# 🔍 Found {len(results)} Objective-C Header results"]
        output.append(f"**Search keyword:** {query}")

        if processed_query != query:
            output.append(f"**Processed query:** {processed_query}")

        output.append("")

        for i, result in enumerate(results, 1):
            output.append(f"## {i}. {result['file_name']}")
            output.append(f"**Match type:** {result['match_type']}")
            output.append(f"**Relevance score:** {result['relevance_score']:.2f}")
            output.append(f"**Matched content:** {result['matched_content']}")
            output.append("")

        formatted_result = "\n".join(output)

        if self.search_engine and self.search_engine.query_processor:
            return self.search_engine.query_processor.postprocess_output(
                formatted_result, user_language
            )
        else:
            return formatted_result

    def _search_api_list_files(
        self, query: str, max_results: int = 5
    ) -> list[dict[str, Any]]:
        """Search in API list files"""
        results: list[dict[str, Any]] = []
        query_lower = query.lower()

        try:
            # Search API list file
            api_list_file = (
                self.get_data_file("web_search") / "web_search_objc_api-list.md"
            )
            if api_list_file.exists():
                content = api_list_file.read_text(encoding="utf-8")
                lines = content.split("\n")

                for line in lines:
                    line = line.strip()
                    if not line or line.startswith("#") or line.startswith("http"):
                        continue

                    # Check if contains query string
                    if query_lower in line.lower():
                        # Parse line format: Classes/GSFont or Protocols/GSGlyphViewControllerProtocol
                        parts = line.split("/")
                        if len(parts) >= 2:
                            api_type = parts[0]
                            api_name = parts[1]

                            # Calculate relevance score
                            score = 1.0 if query_lower == api_name.lower() else 0.8
                            if query_lower in api_name.lower():
                                score += 0.2

                            results.append(
                                {
                                    "name": api_name,
                                    "type": api_type,
                                    "score": min(score, 1.0),
                                    "url": f"https://docu.glyphsapp.com/Core/{line}.html",
                                    "full_path": line,
                                }
                            )

            # Also search hierarchy file
            hierarchy_file = (
                self.get_data_file("api") / "docu_glyphsapp_com_Core_hierarchy_html.md"
            )
            if hierarchy_file.exists():
                content = hierarchy_file.read_text(encoding="utf-8")
                lines = content.split("\n")

                for line in lines:
                    if query_lower in line.lower() and "[" in line and "]" in line:
                        # Parse Markdown link format: - [GSGlyphViewControllerProtocol](https://docu.glyphsapp.com/Core/Protocols/GSGlyphViewControllerProtocol.html)
                        import re

                        match = re.search(r"\[([^\]]+)\]\((https://[^)]+)\)", line)
                        if match:
                            name = match.group(1)
                            url = match.group(2)

                            # Avoid duplicates
                            if not any(r["name"] == name for r in results):
                                score = 0.9 if query_lower == name.lower() else 0.7
                                api_type = "Protocol" if "Protocol" in url else "Class"

                                results.append(
                                    {
                                        "name": name,
                                        "type": api_type,
                                        "score": score,
                                        "url": url,
                                        "full_path": name,
                                    }
                                )

        except Exception as e:
            logger.error(f"Error searching API list files: {e}")

        # Sort by score and limit results
        results.sort(key=lambda x: float(x["score"]), reverse=True)
        return results[:max_results]

    def _get_objc_header(self, header_query: str) -> str:
        """Get Objective-C Header file content"""
        if not header_query.strip():
            return "Please provide Header file name or class name"

        if not self.header_search_engine:
            return "Header search engine not initialized"

        # Check if Headers path is available
        if not self.headers_base_path:
            return """Glyphs 3 Headers not found

Please verify:
1. Glyphs 3 is installed at: /Applications/Glyphs 3.app
2. Or set GLYPHS_APP_HEADERS_PATH environment variable to the correct path

Example:
export GLYPHS_APP_HEADERS_PATH="/Applications/Glyphs 3.app/Contents/Frameworks/GlyphsCore.framework/Versions/A/Headers"
"""

        # Clean query, ensure .h extension
        query = header_query.strip()
        if not query.endswith(".h"):
            query += ".h"

        # Read file from Glyphs 3 Headers directory
        header_file = self.headers_base_path / query

        if header_file.exists():
            try:
                content = header_file.read_text(encoding="utf-8")

                output = [f"# 📄 {query} - Objective-C Header File"]
                output.append(f"**File path:** {header_file}")
                output.append(f"**File size:** {len(content)} characters")
                output.append("")
                output.append("## File Content")
                output.append("")
                output.append("```objective-c")
                output.append(content)
                output.append("```")

                return "\n".join(output)

            except Exception as e:
                return f"Failed to read Header file: {e}"
        else:
            # If direct file doesn't exist, try searching for similar file names
            search_results = self.header_search_engine.search(
                header_query, max_results=5
            )

            if search_results:
                suggestions = [r["file_name"] for r in search_results]
                return f"""Header file not found: {query}

Possible similar files:
{chr(10).join(f"- {s}" for s in suggestions)}

**Suggestion**: First use `api_search_objc_headers` tool to search for the correct file name"""
            else:
                return f"Header file not found: {query}"

    def core_search(
        self, query: str, max_results: int = 5, **kwargs: Any
    ) -> list[dict[str, Any]]:
        """Core search method for unified search engine"""
        if not self.header_search_engine:
            return []

        # Execute Header search
        header_results = self.header_search_engine.search(query, max_results)

        # Convert to unified format
        unified_results = []
        for result in header_results:
            unified_results.append(
                {
                    "title": f"{result['file_name']} ({result['match_type']})",
                    "content": result["matched_content"],
                    "score": result["relevance_score"],
                    "source": "objc_headers",
                    "metadata": {
                        "file_name": result["file_name"],
                        "match_type": result["match_type"],
                    },
                }
            )

        return unified_results

    def get_tools(self) -> dict[str, Any]:
        """Get available tools list (for test compatibility)"""
        tools = {
            "search_python_api": self._search_python_api,
            "search_objc_api": self._search_objc_api,
            "search_drawing_tools": self._search_drawing_tools,
            "search_plugins_api": self._search_plugins_api,
            "get_class_details": self._get_class_details,
            "get_api_overview": self._get_api_overview,
        }

        # Add Header related tools (always included, even if not initialized yet)
        tools["api_search_objc_headers"] = self._search_objc_api_headers
        tools["api_get_objc_header"] = self._get_objc_header

        return tools

    def get_module_info(self) -> dict[str, Any]:
        """Get module information"""
        return {
            "name": self.name,
            "type": "api",
            "initialized": self.is_initialized,
            "python_classes": len(self.python_api.get("classes", [])),
            "objc_classes": len(self.objc_api.get("classes", [])),
            "drawing_functions": len(self.drawing_tools.get("functions", [])),
            "plugins": len(self.plugins.get("plugins", [])),
            "tools": [
                "search_python_api",
                "search_objc_api",
                "search_drawing_tools",
                "search_plugins_api",
                "get_class_details",
                "get_api_overview",
                "api_search_objc_headers",
                "api_get_objc_header",
            ],
            "header_files_count": (
                self.header_search_engine.get_indexed_files_count()
                if self.header_search_engine
                else 0
            ),
        }
