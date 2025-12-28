#!/usr/bin/env python3
"""
Glyphs.app Plugin Tools Module

Provides MCP tools for plugin search, query, and code generation functionality
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any

# Use shared core library
project_root = Path(__file__).parent.parent.parent
shared_core_path = str(project_root / "src" / "shared")
if shared_core_path not in sys.path:
    sys.path.insert(0, shared_core_path)

from glyphs_info_mcp.shared.core.base_module import BaseMCPModule

logger = logging.getLogger(__name__)

class PluginToolsModule(BaseMCPModule):
    """Plugin tools module for MCP integration"""

    def __init__(self, name: str, data_path: Path | None = None):
        super().__init__(name, data_path)
        self.plugin_manager: PluginToolsManager | None = None

    def initialize(self) -> bool:
        """Initialize the plugin tools module"""
        try:
            # Check if data_path directly contains plugin metadata (when passed as glyphs-plugins dir)
            if (self.data_path / "metadata").exists():
                plugins_dir = self.data_path
            else:
                # Otherwise look for plugins subdirectory
                plugins_dir = self.get_data_file("plugins")
                if not plugins_dir.exists():
                    logger.error(f"Plugins directory not found: {plugins_dir}")
                    return False

            self.plugin_manager = PluginToolsManager(str(plugins_dir))
            self.is_initialized = True

            logger.info("Plugin tools module initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize plugin tools module: {e}")
            return False

    def register_tools(self, mcp_instance: Any) -> None:
        """Register MCP tools for plugin functionality"""

        @mcp_instance.tool()
        def search_plugins(query: str, plugin_type: str | None = None) -> str:
            """
            Search for Glyphs.app plugins by name, type, or functionality

            Args:
                query: Search query string
                plugin_type: Optional plugin type filter

            Returns:
                Search results for plugins matching the query
            """
            if not self.is_initialized or self.plugin_manager is None:
                return "Plugin tools module not initialized"

            return self.plugin_manager.search_plugins(query, plugin_type)

        @mcp_instance.tool()
        def get_plugin_details(plugin_name: str) -> str:
            """
            Get detailed information about a specific plugin type

            Args:
                plugin_name: Name of the plugin class

            Returns:
                Detailed information about the plugin including methods and usage
            """
            if not self.is_initialized or self.plugin_manager is None:
                return "Plugin tools module not initialized"

            return self.plugin_manager.get_plugin_details(plugin_name)

        @mcp_instance.tool()
        def get_method_details(method_name: str) -> str:
            """
            Get detailed information about a specific plugin method

            Args:
                method_name: Name of the method to look up

            Returns:
                Detailed information about the method across all plugins
            """
            if not self.is_initialized or self.plugin_manager is None:
                return "Plugin tools module not initialized"

            return self.plugin_manager.get_method_details(method_name)

        @mcp_instance.tool()
        def generate_plugin_code(plugin_type: str, plugin_name: str) -> str:
            """
            Generate code template for a specific plugin type

            Args:
                plugin_type: Type of plugin to generate (e.g., FileFormatPlugin, ReporterPlugin)
                plugin_name: Custom name for the generated plugin

            Returns:
                Generated Python code template for the plugin
            """
            if not self.is_initialized or self.plugin_manager is None:
                return "Plugin tools module not initialized"

            return self.plugin_manager.generate_plugin_code(plugin_type, plugin_name)

        @mcp_instance.tool()
        def list_available_plugins() -> str:
            """
            List all available plugin types with their descriptions

            Returns:
                List of all available plugin types and their purposes
            """
            if not self.is_initialized or self.plugin_manager is None:
                return "Plugin tools module not initialized"

            return self.plugin_manager.list_available_plugins()

        @mcp_instance.tool()
        def get_inheritance_info() -> str:
            """
            Get plugin class inheritance hierarchy information

            Returns:
                Information about plugin class inheritance relationships
            """
            if not self.is_initialized or self.plugin_manager is None:
                return "Plugin tools module not initialized"

            return self.plugin_manager.get_inheritance_info()

    def get_module_info(self) -> dict[str, Any]:
        """Get module information"""
        plugin_count = 0
        method_count = 0

        if self.plugin_manager:
            plugin_count = len(self.plugin_manager.plugin_registry.get("plugins", {}))
            method_count = len(self.plugin_manager.method_index.get("methods", {}))

        return {
            'name': self.name,
            'type': 'plugins',
            'initialized': self.is_initialized,
            'plugin_count': plugin_count,
            'method_count': method_count,
            'tools': [
                'search_plugins', 'get_plugin_details', 'get_method_details',
                'generate_plugin_code', 'list_available_plugins', 'get_inheritance_info'
            ]
        }

    def get_tools(self) -> dict[str, Any]:
        """Get MCP tools provided by this module"""
        if not self.is_initialized or not self.plugin_manager:
            return {}

        return {
            'search_plugins': self.plugin_manager.search_plugins,
            'get_plugin_details': self.plugin_manager.get_plugin_details,
            'get_method_details': self.plugin_manager.get_method_details,
            'generate_plugin_code': self.plugin_manager.generate_plugin_code,
            'list_available_plugins': self.plugin_manager.list_available_plugins,
            'get_inheritance_info': self.plugin_manager.get_inheritance_info
        }


class PluginToolsManager:
    """Plugin tools manager for handling plugin data using SDK Native Accessor"""

    def __init__(self, plugins_resource_dir: str, sdk_accessor: Any = None):
        """
        Initialize plugin tools manager

        Args:
            plugins_resource_dir: Path to plugin resources directory (legacy)
            sdk_accessor: SDK Native Accessor instance (new)
        """
        self.resource_dir = Path(plugins_resource_dir)
        self.metadata_dir = self.resource_dir / "metadata"
        self.reference_dir = self.resource_dir / "reference"
        self.templates_dir = self.resource_dir / "templates"
        self.guides_dir = self.resource_dir / "guides"

        # SDK Native Accessor (preferred)
        self.sdk_accessor: Any = sdk_accessor

        # Plugin templates cache (loaded from accessor or JSON)
        self.plugin_registry: dict[str, Any] = {}
        self.method_index: dict[str, Any] = {}
        self.inheritance_map: dict[str, Any] = {}

        self._load_metadata()

    def _load_metadata(self) -> None:
        """Load metadata from SDK Native Accessor or fallback to JSON"""
        try:
            # Prefer SDK Native Accessor
            if self.sdk_accessor:
                logger.info("Loading plugin templates from SDK Native Accessor")
                self._load_from_accessor()
            else:
                # Fallback to JSON files (legacy support)
                logger.warning("SDK Native Accessor not available, falling back to JSON files")
                self._load_from_json()

        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")

    def _load_from_accessor(self) -> None:
        """Load template data from SDK Native Accessor"""
        templates = self.sdk_accessor.list_plugin_templates()

        # Convert to legacy format for backward compatibility
        self.plugin_registry = {"plugins": {}}

        for template in templates:
            plugin_name = template["name"]
            self.plugin_registry["plugins"][plugin_name] = {
                "purpose": template.get("description", template.get("doc", "No description")),
                "base_classes": [template.get("base_class", "NSObject")],
                "file_path": template["path"],
                "methods": {},  # Parsed from source code
                "required_methods": template.get("required_methods", []),
                "optional_methods": template.get("optional_methods", [])
            }

        logger.info(f"Loaded {len(templates)} plugin templates from SDK Native Accessor")

    def _load_from_json(self) -> None:
        """Load from JSON files (legacy support)"""
        # Load plugin registry
        registry_file = self.metadata_dir / "plugin_registry.json"
        if registry_file.exists():
            with open(registry_file, encoding='utf-8') as f:
                self.plugin_registry = json.load(f)
            logger.info("Plugin registry loaded from JSON")

        # Load method index
        method_file = self.metadata_dir / "method_index.json"
        if method_file.exists():
            with open(method_file, encoding='utf-8') as f:
                self.method_index = json.load(f)
            logger.info("Method index loaded from JSON")

        # Load inheritance map
        inheritance_file = self.metadata_dir / "inheritance_map.json"
        if inheritance_file.exists():
            with open(inheritance_file, encoding='utf-8') as f:
                self.inheritance_map = json.load(f)
            logger.info("Inheritance map loaded from JSON")

    def search_plugins(self, query: str, plugin_type: str | None = None) -> str:
        """
        Search plugin classes and methods with smart routing

        Args:
            query: Search keyword
            plugin_type: Optional plugin type filter

        Returns:
            Formatted search results
        """
        if not query.strip():
            return "Please provide a search query"

        # Use smart routing for multi-word queries
        if ' ' in query.strip():
            return self._smart_search_plugins(query, plugin_type)
        else:
            return self._simple_search_plugins(query, plugin_type)

    def _simple_search_plugins(self, query: str, plugin_type: str | None = None) -> str:
        """Simple search for plugins"""
        query_lower = query.lower()
        results = []

        # Search plugin classes
        plugins = self.plugin_registry.get("plugins", {})
        for plugin_name, plugin_info in plugins.items():
            if plugin_type and plugin_name != plugin_type:
                continue

            # Check plugin name
            if query_lower in plugin_name.lower():
                results.append({
                    "type": "plugin_class",
                    "name": plugin_name,
                    "info": plugin_info,
                    "relevance": 100
                })
                continue

            # Check description and purpose
            purpose = plugin_info.get("purpose", "").lower()
            if query_lower in purpose:
                results.append({
                    "type": "plugin_class",
                    "name": plugin_name,
                    "info": plugin_info,
                    "relevance": 80
                })
                continue

            # Check method names
            methods = plugin_info.get("methods", {})
            matching_methods = []
            for method_name in methods.keys():
                if query_lower in method_name.lower():
                    matching_methods.append(method_name)

            if matching_methods:
                results.append({
                    "type": "plugin_methods",
                    "name": plugin_name,
                    "info": plugin_info,
                    "matching_methods": matching_methods,
                    "relevance": 60
                })

        # Search method index
        methods = self.method_index.get("methods", {})
        for method_name, method_locations in methods.items():
            if query_lower in method_name.lower():
                results.append({
                    "type": "method_global",
                    "name": method_name,
                    "locations": method_locations,
                    "relevance": 70
                })

        # Sort results
        results.sort(key=lambda x: x["relevance"], reverse=True)

        if not results:
            return f"No results found for '{query}'"

        return self._format_search_results(query, results[:10])

    def _smart_search_plugins(self, query: str, plugin_type: str | None = None) -> str:
        """Smart search for plugins using query analysis"""
        results = []

        # Detect query type and route appropriately
        query_words = query.lower().split()

        # Plugin specific keywords
        plugin_keywords = ['plugin', 'filter', 'reporter', 'fileformat', 'tool', 'export', 'import']
        method_keywords = ['method', 'function', 'callback', 'hook', 'event']
        ui_keywords = ['ui', 'interface', 'dialog', 'window', 'menu']

        # Score different aspects
        plugin_score = sum(1 for word in query_words if word in plugin_keywords)
        method_score = sum(1 for word in query_words if word in method_keywords)
        ui_score = sum(1 for word in query_words if word in ui_keywords)

        # Enhanced search with category-specific results
        plugins = self.plugin_registry.get("plugins", {})

        # Search by category priority - always search, not just if score > 0
        # Multi-criteria search
        for plugin_name, plugin_info in plugins.items():
            if plugin_type and plugin_name != plugin_type:
                continue

            # Check if query words match plugin name, purpose, or methods
            plugin_name_lower = plugin_name.lower()
            purpose_lower = plugin_info.get("purpose", "").lower()
            methods = plugin_info.get("methods", {})

            # Calculate relevance score
            relevance = 0
            matched_aspects = []

            # Check plugin name
            if any(word in plugin_name_lower for word in query_words):
                relevance += 100
                matched_aspects.append("name")

            # Check purpose/description
            if any(word in purpose_lower for word in query_words):
                relevance += 80
                matched_aspects.append("purpose")

            # Check method names
            matching_methods = []
            for method_name in methods.keys():
                if any(word in method_name.lower() for word in query_words):
                    matching_methods.append(method_name)
                    relevance += 60
                    matched_aspects.append("methods")

            # Add bonus score for keyword matches
            if plugin_score > 0:
                relevance += plugin_score * 20
            if method_score > 0:
                relevance += method_score * 15
            if ui_score > 0:
                relevance += ui_score * 10

            if relevance > 0:
                results.append({
                    "type": "plugin_class",
                    "name": plugin_name,
                    "info": plugin_info,
                    "matching_methods": matching_methods,
                    "matched_aspects": matched_aspects,
                    "relevance": relevance
                })

        # Sort results
        results.sort(key=lambda x: x["relevance"], reverse=True)

        if results:
            return f"# 🔍 Smart Search: {query}\n\n" + self._format_smart_search_results(query, results[:10])
        else:
            # Fallback to simple search
            return self._simple_search_plugins(query, plugin_type)

    def _format_smart_search_results(self, query: str, results: list[dict]) -> str:
        """Format smart search results"""
        output = [f"Found {len(results)} related results:\n"]

        for i, result in enumerate(results, 1):
            output.append(f"**{i}. {result['name']}** (Relevance: {result['relevance']})")

            purpose = result["info"].get("purpose", "No description")
            output.append(f"**Purpose**: {purpose}")

            if "matched_aspects" in result:
                aspects = result["matched_aspects"]
                if "name" in aspects:
                    output.append("✓ Matches plugin name")
                if "purpose" in aspects:
                    output.append("✓ Matches description")
                if "methods" in aspects and result.get("matching_methods"):
                    output.append(f"✓ Matches methods: {', '.join(result['matching_methods'])}")

            base_classes = result["info"].get("base_classes", [])
            if base_classes:
                output.append(f"**Base Classes**: {', '.join(base_classes)}")

            output.append("")  # Empty line between results

        return "\n".join(output)

    def _format_search_results(self, query: str, results: list[dict]) -> str:
        """Format search results"""
        output = [f"Found {len(results)} results for '{query}':\n"]

        for i, result in enumerate(results, 1):
            if result["type"] == "plugin_class":
                output.append(f"**{i}. Plugin Class: {result['name']}**")
                purpose = result["info"].get("purpose", "No description")
                output.append(f"Purpose: {purpose}")

                base_classes = result["info"].get("base_classes", [])
                if base_classes:
                    output.append(f"Base Class: {', '.join(base_classes)}")

                required_methods = result["info"].get("required_methods", [])
                if required_methods:
                    output.append(f"Required Methods: {', '.join(required_methods)}")

            elif result["type"] == "plugin_methods":
                output.append(f"**{i}. Plugin: {result['name']} (Methods)**")
                output.append(f"Matching Methods: {', '.join(result['matching_methods'])}")
                purpose = result["info"].get("purpose", "No description")
                output.append(f"Purpose: {purpose}")

            elif result["type"] == "method_global":
                output.append(f"**{i}. Method: {result['name']}**")
                locations = result["locations"][:3]  # Limit display count
                for loc in locations:
                    plugin = loc.get("plugin", "Unknown")
                    output.append(f"  - Found in: {plugin}")

            output.append("")  # Empty line separator

        return '\n'.join(output)

    def get_plugin_details(self, plugin_name: str) -> str:
        """
        Get detailed plugin information

        Args:
            plugin_name: Plugin class name

        Returns:
            Detailed plugin information
        """
        plugins = self.plugin_registry.get("plugins", {})
        if plugin_name not in plugins:
            available = list(plugins.keys())
            return f"Plugin '{plugin_name}' not found. Available plugins: {', '.join(available)}"

        plugin_info = plugins[plugin_name]

        output = [f"# {plugin_name}\n"]

        # Basic information
        purpose = plugin_info.get("purpose", "No description available")
        output.append(f"**Purpose**: {purpose}\n")

        # Base classes
        base_classes = plugin_info.get("base_classes", [])
        if base_classes:
            output.append(f"**Base Classes**: {', '.join(base_classes)}\n")

        # Required methods
        required_methods = plugin_info.get("required_methods", [])
        if required_methods:
            output.append(f"**Required Methods**: {', '.join(required_methods)}\n")

        # Optional methods
        optional_methods = plugin_info.get("optional_methods", [])
        if optional_methods:
            output.append(f"**Optional Methods**: {', '.join(optional_methods)}\n")

        # Usage notes
        usage_notes = plugin_info.get("usage_notes", [])
        if usage_notes:
            output.append("**Usage Notes**:")
            for note in usage_notes:
                output.append(f"- {note}")
            output.append("")

        # Method details
        methods = plugin_info.get("methods", {})
        if methods:
            output.append("## Available Methods\n")
            for method_name, method_info in methods.items():
                output.append(f"### {method_name}")

                docstring = method_info.get("docstring", "").strip()
                if docstring:
                    # Clean docstring format
                    cleaned_doc = docstring.replace('\t', '').replace('\n\t\t', '\n')
                    output.append(f"```\n{cleaned_doc}\n```")

                parameters = method_info.get("parameters", [])
                if parameters:
                    output.append(f"**Parameters**: {', '.join(parameters)}")

                output.append("")

        # File path information
        file_path = plugin_info.get("file_path", "")
        if file_path:
            output.append(f"**Source File**: `{file_path}`")

        return '\n'.join(output)

    def get_method_details(self, method_name: str) -> str:
        """
        Get detailed method information

        Args:
            method_name: Method name

        Returns:
            Detailed method information
        """
        methods = self.method_index.get("methods", {})
        if method_name not in methods:
            return f"Method '{method_name}' not found in index"

        method_locations = methods[method_name]

        output = [f"# Method: {method_name}\n"]
        output.append(f"Found in {len(method_locations)} plugin(s):\n")

        for i, location in enumerate(method_locations, 1):
            plugin = location.get("plugin", "Unknown")
            output.append(f"## {i}. {plugin}")

            docstring = location.get("docstring", "").strip()
            if docstring:
                cleaned_doc = docstring.replace('\t', '').replace('\n\t\t', '\n')
                output.append(f"```\n{cleaned_doc}\n```")

            parameters = location.get("parameters", [])
            if parameters:
                output.append(f"**Parameters**: {', '.join(parameters)}")

            file_path = location.get("file_path", "")
            line_number = location.get("line_number", 0)
            if file_path:
                output.append(f"**Location**: `{file_path}:{line_number}`")

            output.append("")

        return '\n'.join(output)

    def generate_plugin_code(self, plugin_type: str, plugin_name: str) -> str:
        """
        Generate plugin code template

        Args:
            plugin_type: Plugin type
            plugin_name: Custom plugin name

        Returns:
            Generated code
        """
        # Check if plugin type exists
        plugins = self.plugin_registry.get("plugins", {})
        if plugin_type not in plugins:
            available = list(plugins.keys())
            return f"Plugin type '{plugin_type}' not found. Available types: {', '.join(available)}"

        # Prefer SDK Native Accessor to get complete source code
        if self.sdk_accessor:
            try:
                template = self.sdk_accessor.get_plugin_template(plugin_type)
                if template:
                    # Return complete source code with template variables replaced
                    generated_code = template["source"]
                    generated_code = generated_code.replace("____PluginClassName____", plugin_name)
                    generated_code = generated_code.replace("____PluginName____", plugin_name)

                    return f"# Generated Plugin: {plugin_name}\n\n{generated_code}"
            except Exception as e:
                logger.warning(f"Failed to get template from accessor: {e}, falling back to JSON")

        # Fallback to legacy template files
        template_mapping = {
            "FileFormatPlugin": "file_format_plugin_template.py",
            "ReporterPlugin": "reporter_plugin_template.py",
            "FilterWithDialog": "filter_plugin_template.py",
            "FilterWithoutDialog": "filter_plugin_template.py",
        }

        template_file = template_mapping.get(plugin_type)
        if not template_file:
            return f"No template available for plugin type '{plugin_type}'"

        template_path = self.templates_dir / template_file
        if not template_path.exists():
            return f"Template file not found: {template_file}"

        try:
            with open(template_path, encoding='utf-8') as f:
                template_content = f.read()

            # Replace template variables
            generated_code = template_content.replace("{{PLUGIN_NAME}}", plugin_name)

            return generated_code

        except Exception as e:
            return f"Error generating code: {e}"

    def list_available_plugins(self) -> str:
        """List all available plugin types"""
        plugins = self.plugin_registry.get("plugins", {})
        if not plugins:
            return "No plugins found in registry"

        output = ["# Available Plugin Types\n"]

        for plugin_name, plugin_info in plugins.items():
            purpose = plugin_info.get("purpose", "No description")
            required_methods = plugin_info.get("required_methods", [])

            output.append(f"## {plugin_name}")
            output.append(f"**Purpose**: {purpose}")

            if required_methods:
                output.append(f"**Required Methods**: {', '.join(required_methods)}")

            output.append("")

        return '\n'.join(output)

    def get_inheritance_info(self) -> str:
        """Get inheritance relationship information"""
        hierarchy = self.inheritance_map.get("hierarchy", {})
        if not hierarchy:
            return "No inheritance information available"

        output = ["# Plugin Class Inheritance\n"]

        for plugin_name, plugin_info in hierarchy.items():
            base_classes = plugin_info.get("base_classes", [])
            purpose = plugin_info.get("purpose", "No description")

            output.append(f"## {plugin_name}")
            if base_classes:
                output.append(f"**Inherits from**: {', '.join(base_classes)}")
            output.append(f"**Purpose**: {purpose}")
            output.append("")

        return '\n'.join(output)
