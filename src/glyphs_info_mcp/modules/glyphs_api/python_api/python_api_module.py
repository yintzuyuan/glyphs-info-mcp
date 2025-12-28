#!/usr/bin/env python3
"""
Python API Module for Glyphs.app
Handles Python API queries and documentation
"""

import logging
import sys
from pathlib import Path
from typing import Any, Callable

# Use shared core library
project_root = Path(__file__).parent.parent.parent.parent
shared_core_path = str(project_root / "src" / "shared")
if shared_core_path not in sys.path:
    sys.path.insert(0, shared_core_path)

from glyphs_info_mcp.shared.core.base_module import BaseMCPModule

logger = logging.getLogger(__name__)

# Dynamically import PythonAPIManager
import importlib.util

def import_manager(module_path: str, class_name: str) -> type[Any]:
    """Dynamically import manager class"""
    spec = importlib.util.spec_from_file_location(class_name.lower(), module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, class_name)

# Get PythonAPIManager path
api_dir = Path(__file__).parent.parent / "api"
PythonAPIManager = import_manager(str(api_dir / "python_api_native.py"), "PythonAPIManager")


class PythonAPIModule(BaseMCPModule):
    """Python API Module - Handles Python API queries"""

    def __init__(self, name: str = "python-api", data_path: Path | None = None):
        super().__init__(name, data_path)
        self.python_api: Any = None
        self.search_engine: Any = None  # Will be injected by server.py

    def set_search_engine(self, search_engine: Any) -> None:
        """Set unified search engine (called by server.py)"""
        self.search_engine = search_engine

    def initialize(self) -> bool:
        """Initialize Python API module"""
        try:
            # Get __init__.py path
            project_root = Path(__file__).parent.parent.parent.parent
            init_file = project_root / "data" / "official" / "GlyphsSDK" / \
                       "ObjectWrapper" / "GlyphsApp" / "__init__.py"

            # Use PythonAPIManager (Native version)
            self.python_api = PythonAPIManager(init_file)
            self.is_initialized = True

            logger.info("Python API Module initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Python API module: {e}")
            return False

    def core_search(
        self, query: str, max_results: int = 5, **kwargs: Any
    ) -> list[dict[str, Any]]:
        """Core search function - exclusively for unified search engine

        Returns structured search results without vocabulary processing or formatting

        Args:
            query: Search query (pre-processed)
            max_results: Maximum number of results
            **kwargs: Additional parameters (e.g., scope)

        Returns:
            List of structured search results
        """
        if not self.is_initialized:
            return []

        results: list[dict[str, Any]] = []
        scope = kwargs.get("scope", "auto")

        try:
            # Use internal Python API search
            python_results = self._search_python_api_structured(query, max_results, scope)
            results.extend(python_results)

        except Exception as e:
            logger.error(f"Python API core search failed: {e}")

        return results[:max_results]

    def _search_python_api_structured(self, query: str, max_results: int, scope: str) -> list[dict[str, Any]]:
        """Search in Python API (simplified version - returns formatted string directly)"""
        results: list[dict[str, Any]] = []

        if self.python_api is None:
            return results

        try:
            # Use Python API Manager's indexed search (already formatted)
            search_result = self.python_api.search(query, search_scope=scope, max_results=max_results)

            # Return entire result as single item (already in optimal format)
            if search_result and "Not found" not in search_result and "No Python API found" not in search_result:
                results.append({
                    'title': f"Python API Search Results: '{query}'",
                    'content': search_result,
                    'type': 'api_index',
                    'source': 'python_api',
                    'score': 0.9
                })

        except Exception as e:
            logger.error(f"Python API search failed: {e}")

        return results

    def get_tools(self) -> dict[str, Callable[..., Any]]:
        """Get available tools dictionary"""
        return {
            'api_search_python': self.python_api_search,
            'api_get_python_class': self.python_api_class_info,
            'api_get_python_member': self.python_api_member_info
        }

    def get_module_info(self) -> dict[str, Any]:
        """Get module information"""
        return {
            'name': self.name,
            'description': 'Python API Query Module',
            'tools_count': 3,
            'status': 'initialized' if self.is_initialized else 'not_initialized'
        }

    # ========== Public Tool Methods ==========

    def python_api_class_info(self, class_name: str, detail_level: str = "overview") -> str:
        """
        [PYTHON API] Python class information tool with multiple detail levels

        Function: Provides Python API class information at different detail levels to address information overload.

        Args:
            class_name: Class name (e.g., GSFont, GSGlyph, GSLayer)
            detail_level: Detail level
                - "overview": Summary + key members + query guidance (default)
                - "detailed": Categorized member list + type info + usage hints
                - "full": Complete member info (for large development tasks)

        Returns:
            Formatted Python API class information
        """
        if not self.is_initialized:
            return "API module not initialized"

        if detail_level not in ["overview", "detailed", "full"]:
            return f"Invalid detail_level: {detail_level}. Supported values: overview, detailed, full"

        return self._get_python_class_info(class_name, detail_level)

    def python_api_search(self, query: str, scope: str = "auto", max_results: int = 5) -> str:
        """
        [PYTHON API] Query Glyphs Python API specifications and documentation

        Purpose: Find official documentation and specifications for API classes, methods, and properties
        Content types: API reference docs, type definitions, parameter descriptions, return values
        Complementary tools: Use `sdk_search` to get actual code examples and implementation guidance

        Use cases:
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

        # Use local Python search logic directly to avoid mixing with Header search
        processed_query = query
        user_language = 'zh'

        # Use term processor for preprocessing (if available)
        if self.search_engine and self.search_engine.query_processor:
            processed_query, user_language = self.search_engine.query_processor.preprocess_query(query)

        result = self._python_search(processed_query, scope, max_results)

        # Use term processor for post-processing
        if self.search_engine and self.search_engine.query_processor:
            result = self.search_engine.query_processor.postprocess_output(result, user_language)

        # Add related tool recommendations
        result += self._add_cross_references(processed_query, "python_api")

        return result

    def python_api_member_info(self, class_name: str, member_name: str, member_type: str) -> str:
        """
        [PYTHON API] Get detailed information and usage examples for Python API class members

        Function: Provides complete documentation, parameter descriptions, and code examples for specific Python API class members.

        Args:
            class_name: Class name (e.g., GSFont, GSGlyph, GSLayer)
            member_name: Member name (method, property, etc.)
            member_type: Member type, must be "property" or "method"

        Returns:
            Detailed documentation and usage examples for Python API member
        """
        if not self.is_initialized:
            return "API module not initialized"

        return self._get_python_member_info(class_name, member_name, member_type)

    # ========== Private Helper Methods ==========

    def _get_python_class_info(self, class_name: str, detail_level: str) -> str:
        """Implementation for python class info - uses new concise format"""
        if self.python_api is None:
            return f"Class '{class_name}' not found"
        result = self.python_api.get_class_info(class_name, detail_level)
        if result and 'error' not in result:
            formatted_info = self._format_class_info_simple(result, detail_level)
            return formatted_info

        return f"Class '{class_name}' not found"

    def _format_class_info_simple(self, class_info: dict, detail_level: str) -> str:
        """Minimal formatting (using list directly, for Native Accessor)"""
        output = [f"# 🐍 {class_info['name']}\n"]

        # Description
        if class_info.get('description'):
            output.append(f"{class_info['description']}\n")

        properties = class_info.get('properties', [])
        methods = class_info.get('methods', [])

        # Statistics
        output.append("## 📊 Members")
        output.append(f"- Properties: {len(properties)}")
        output.append(f"- Methods: {len(methods)}\n")

        # Properties list (concise)
        if properties:
            if detail_level == 'overview':
                shown = properties[:10]
                output.append("## Key Properties")
                output.append(", ".join(shown))
                if len(properties) > 10:
                    output.append(f"... (+{len(properties)-10} more)")
            else:
                output.append("## All Properties")
                output.append("\n".join(f"- {p}" for p in properties))

        # Methods list (concise)
        if methods:
            if detail_level == 'overview':
                shown = methods[:10]
                output.append("\n## Key Methods")
                output.append(", ".join(f"{m}()" for m in shown))
                if len(methods) > 10:
                    output.append(f"... (+{len(methods)-10} more)")
            else:
                output.append("\n## All Methods")
                output.append("\n".join(f"- {m}()" for m in methods))

        # Query hint
        output.append("\n## 💡 Query Details")
        output.append(f"Use `api_get_python_member {class_info['name']} <member_name> <property|method>` to view detailed info")

        return "\n".join(output)

    def _python_search(self, query: str, scope: str, max_results: int) -> str:
        """Implementation for unified python search - uses global search uniformly"""
        # Note: scope parameter retained for API compatibility, but uses global search
        # Reason: scoped search methods (_search_methods, _search_properties, etc.) had poor results
        return self._search_python_api(query, max_results)

    def _get_python_member_info(self, class_name: str, member_name: str, member_type: str) -> str:
        """Enhanced implementation for python member info"""
        if self.python_api is None:
            return f"Member '{member_name}' (type: {member_type}) not found in class '{class_name}'"
        result = self.python_api.get_class_member(class_name, member_name, member_type)
        if result and 'error' not in result:
            return self._format_member_info_enhanced(result, "Python API")

        return f"Member '{member_name}' (type: {member_type}) not found in class '{class_name}'"

    def _search_python_api(self, query: str, max_results: int) -> str:
        """Implementation for Python API search with smart routing"""
        if self.python_api is None:
            return f"No Python API found related to '{query}'"
        if ' ' in query.strip():
            # Multi-word query - use smart routing
            return self._smart_search_python_api(query, max_results)
        else:
            # Single word query - use direct search
            return self.python_api.search(query)

    def _smart_search_python_api(self, query: str, max_results: int) -> str:
        """Enhanced smart search for Python API with better relevance"""
        if self.python_api is None:
            return f"No Python API found related to '{query}'"

        query_words = query.lower().split()

        # Glyphs-specific class keywords
        class_keywords = ['gsfont', 'gsglyph', 'gslayer', 'gspath', 'gsnode', 'gsanchor', 'gsguide', 'gsmaster']

        # Check if query is about a specific class
        class_match = None
        for word in query_words:
            if word in class_keywords:
                class_match = word
                break

        if class_match:
            # Try to get class overview first
            result = self.python_api.get_class_overview(class_match.upper())
            if result and 'error' not in result:
                return f"# 🐍 Python API - {class_match.upper()}\n\n{self._format_class_info(result)}"

        # Enhanced multi-word search strategy
        if len(query_words) > 1:
            return self._enhanced_multi_word_search(query, query_words, max_results)
        else:
            # Single word search - use direct search
            return self._single_word_search(query, max_results)

    def _format_class_info(self, class_info: dict) -> str:
        """Format class information for display"""
        output = []

        if class_info.get('description'):
            output.append(f"**Description:** {class_info['description']}")

        if class_info.get('methods'):
            output.append(f"**Method Count:** {len(class_info['methods'])}")

        if class_info.get('properties'):
            output.append(f"**Property Count:** {len(class_info['properties'])}")

        return "\n".join(output) if output else "No information available"

    def _enhanced_multi_word_search(self, query: str, query_words: list[str], max_results: int) -> str:
        """Enhanced multi-word search with better relevance scoring"""
        if self.python_api is None:
            return f"No Python API found related to '{query}'"

        # Define search priority: object terms > action terms
        object_terms = ['background', 'anchor', 'bounds', 'width', 'height', 'layer', 'glyph', 'font',
                       'color', 'path', 'node', 'guide', 'master', 'component']
        action_terms = ['add', 'remove', 'get', 'set', 'create', 'delete', 'update', 'find']

        # Separate words by priority
        primary_words = [w for w in query_words if w in object_terms]
        secondary_words = [w for w in query_words if w in action_terms]
        other_words = [w for w in query_words if w not in object_terms and w not in action_terms and len(w) > 2]

        # Search priority: primary > other > secondary
        search_order = primary_words + other_words + secondary_words

        # Try each word in priority order
        best_result: str | None = None
        best_word: str | None = None

        for word in search_order:
            word_result = self.python_api.search(word)
            if word_result and not word_result.startswith("Not found") and "No Python API found" not in word_result:
                # If this is a primary word (object term), use it immediately
                if word in object_terms:
                    return f"# 🔍 Multi-word Search: {query}\n\n## Key Search Results for '{word}':\n{word_result}"

                # Otherwise, store as best result if we haven't found one yet
                if best_result is None:
                    best_result = word_result
                    best_word = word

        # Return best result found
        if best_result:
            return f"# 🔍 Multi-word Search: {query}\n\n## Related Search Results for '{best_word}':\n{best_result}"

        # Fallback to complete phrase search
        complete_result = self.python_api.search(query)
        if complete_result and not complete_result.startswith("Not found") and "No Python API found" not in complete_result:
            return f"# 🔍 Complete Query: {query}\n\n{complete_result}"

        return f"No Python API found related to '{query}'"

    def _single_word_search(self, query: str, max_results: int) -> str:
        """Enhanced single word search"""
        if self.python_api is None:
            return f"No Python API found related to '{query}'"
        result = self.python_api.search(query)
        if result and not result.startswith("Not found") and "No Python API found" not in result:
            return f"# 🔍 Python API Search: {query}\n\n{result}"

        return f"No Python API found related to '{query}'"

    def _format_member_info_enhanced(self, member_info: dict, source: str) -> str:
        """Enhanced format member information with better organization and examples"""
        class_name = member_info.get('class', 'Unknown')
        member_name = member_info.get('name', 'Unknown')
        member_type = member_info.get('member_type', 'unknown')

        # API icon mapping
        api_icons = {
            "Python API": "🐍",
            "Objective-C API": "🔧",
            "Plugin API": "🔌"
        }
        icon = api_icons.get(source, "📚")

        output = [f"# {icon} {source} - {class_name}.{member_name}\n"]

        # Basic info
        description = member_info.get('description', 'No description')
        output.append(f"**📝 Description:** {description}\n")

        # Member type specific info
        if member_type == "property":
            self._format_property_details(member_info, output)
        elif member_type == "method":
            self._format_method_details(member_info, output)

        # Usage examples (priority display)
        examples = member_info.get('examples', [])
        if examples:
            output.append("\n## 💡 Code Examples")
            for _i, example in enumerate(examples[:3], 1):  # Show first 3
                output.append(f"```python\n{example}\n```")
            if len(examples) > 3:
                output.append(f"*... {len(examples) - 3} more examples*")

        # Related query hints
        output.append("\n## 🔍 Related Queries")
        output.append(f"- **Full Class:** `python_api_class_info {class_name}`")
        output.append(f"- **Search Similar:** `python_api_search \"{member_name}\"`")

        return "\n".join(output)

    def _format_property_details(self, member_info: dict, output: list) -> None:
        """Format property-specific details"""
        prop_type = member_info.get('type', 'Any')
        output.append(f"**🏷️ Type:** `{prop_type}`")

        # Read/write status
        if 'read_only' in member_info:
            read_only = "Yes" if member_info.get('read_only') else "No"
            output.append(f"**🔒 Read-only:** {read_only}")

        # Accessor info
        if 'getter' in member_info and member_info.get('getter'):
            output.append(f"**📥 Getter:** `{member_info['getter']}`")

        if 'setter' in member_info and member_info.get('setter'):
            output.append(f"**📤 Setter:** `{member_info['setter']}`")

    def _format_method_details(self, member_info: dict, output: list) -> None:
        """Format method-specific details"""
        # Parameter info
        parameters = member_info.get('parameters', [])
        if parameters:
            output.append(f"\n## 📋 Parameters ({len(parameters)})")
            for param in parameters[:5]:  # Show first 5 parameters
                param_name = param.get('name', 'unnamed')
                param_type = param.get('type', 'Any')
                param_desc = param.get('description', 'No description')
                default = param.get('default')

                param_line = f"- **`{param_name}`** ({param_type})"
                if default is not None:
                    param_line += f" = {default}"
                param_line += f" - {param_desc}"
                output.append(param_line)

            if len(parameters) > 5:
                output.append(f"*... {len(parameters) - 5} more parameters*")

        # Return value info
        return_type = member_info.get('return_type')
        if return_type:
            output.append(f"\n**↩️ Returns:** `{return_type}`")

        return_desc = member_info.get('return_description')
        if return_desc:
            output.append(f"**📤 Return Description:** {return_desc}")

    def _add_cross_references(self, query: str, source_type: str) -> str:
        """Add cross-references and recommendations between tools"""
        cross_ref = "\n\n## 🔗 Related Resources\n"

        if source_type == "python_api":
            cross_ref += f"💡 **Find Implementation Examples**: Use `sdk_search \"{query}\"` to view related code examples and development guides\n"
            cross_ref += "📚 **More Learning Resources**:\n"
            cross_ref += f"  - Use `handbook_search \"{query}\"` to view official handbook explanations\n"
            cross_ref += f"  - Use `web_search_tutorials \"{query}\"` to find online tutorials\n"

        return cross_ref
