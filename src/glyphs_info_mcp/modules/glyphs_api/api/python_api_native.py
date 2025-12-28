#!/usr/bin/env python3
"""
Python API Manager - Native Accessor Version

Uses PythonAPINativeAccessor to read __init__.py directly,
replacing the original JSON file loading approach.

Maintains backward-compatible API interface.
"""

import itertools
import logging
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Add shared core library path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent.parent
shared_core_path = str(project_root / "src" / "shared")
if shared_core_path not in sys.path:
    sys.path.insert(0, shared_core_path)

from glyphs_info_mcp.shared.core.python_api_native_accessor import PythonAPINativeAccessor


class PythonAPIManager:
    """Python API Manager - Uses Native Accessor"""

    def __init__(self, init_file: Path):
        """Initialize Python API Manager

        Args:
            init_file: __init__.py file path
        """
        self.init_file = init_file
        self.accessor = PythonAPINativeAccessor(init_file)
        logger.info("Python API Manager initialized with Native Accessor")

    def search(self, query: str, search_scope: str = 'all', max_results: int = 10, **kwargs: Any) -> str:
        """Search Python API - Layered search strategy

        Layered search strategy (referencing Issue #72/#73 match_type mechanism):
        - Symbol layer: Search symbol index (class, function, constant names) - fast
        - Member layer: Search class members (properties, methods) - slower but complete

        When scope='all', returns results from both layers for AI to decide.
        New scope values: 'members', 'properties', 'methods' for direct member layer search.

        Args:
            query: Search keyword
            search_scope: Search scope
                - 'all': Search all (symbol layer + member layer)
                - 'classes': Search classes only (symbol layer)
                - 'functions': Search functions only (symbol layer)
                - 'constants': Search constants only (symbol layer)
                - 'members': Search class members only (properties + methods, member layer)
                - 'properties': Search properties only (member layer)
                - 'methods': Search methods only (member layer)
            max_results: Maximum number of results
            **kwargs: Other parameters (backward compatible)

        Returns:
            Formatted search results
        """
        all_results = []

        # Symbol layer search: execute when scope is all/classes/functions/constants
        if search_scope in ['all', 'classes', 'functions', 'constants']:
            symbol_results = self.accessor.search(query, symbol_type=search_scope)
            for r in symbol_results:
                r['match_type'] = 'symbol'
            all_results.extend(symbol_results)

        # Member layer search: execute when scope is all/members/properties/methods
        if search_scope in ['all', 'members', 'properties', 'methods']:
            member_results = self._search_class_members(query, max_results * 2)  # Search more for filtering
            # Filter by scope
            if search_scope == 'properties':
                member_results = [r for r in member_results if r.get('type') == 'property']
            elif search_scope == 'methods':
                member_results = [r for r in member_results if r.get('type') == 'method']
            for r in member_results:
                r['match_type'] = 'member'
            all_results.extend(member_results)

        if not all_results:
            # Provide search suggestions
            suggestion = self._get_search_suggestion(query, search_scope)
            return f"No Python API found related to '{query}'\n\n{suggestion}"

        # Deduplicate and sort
        all_results = self._deduplicate_and_sort(all_results)

        # Limit number of results
        all_results = all_results[:max_results]

        # Format as layered output
        return self._format_layered_results(query, all_results)

    def _search_class_members(self, query: str, max_results: int) -> list[dict[str, Any]]:
        """Search class members (properties and methods)

        Second layer search: iterate through all classes, search their property and method names.

        Args:
            query: Search keyword
            max_results: Maximum number of results

        Returns:
            Search results list
        """
        query_lower = query.lower()

        from collections.abc import Iterator

        def _iter_members() -> Iterator[dict[str, Any]]:
            """Internal generator: iterate through all class members and yield matching results"""
            for class_name in self.accessor.symbols.get('classes', []):
                try:
                    class_info = self.accessor.get_class(class_name)
                    if not class_info:
                        continue

                    for member_type, members in [
                        ('property', class_info.get('properties', [])),
                        ('method', class_info.get('methods', [])),
                    ]:
                        for member_name in members:
                            if query_lower in member_name.lower():
                                yield {
                                    'type': member_type,
                                    'class': class_name,
                                    'name': member_name,
                                    'score': 0.8 if query_lower == member_name.lower() else 0.5,
                                }
                except Exception as e:
                    logger.debug(f"Skip class {class_name} during member search: {e}")
                    continue

        # Use itertools.islice to limit results, avoiding multiple break checks
        results = list(itertools.islice(_iter_members(), max_results))

        # Sort by score
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        return results

    def _get_search_suggestion(self, query: str, scope: str) -> str:
        """Provide search suggestions"""
        suggestions = []
        suggestions.append("💡 **Search suggestions**:")
        if scope in ['members', 'properties', 'methods']:
            suggestions.append("- Try using `scope='all'` to search all APIs")
        else:
            suggestions.append("- Try using `scope='members'` to search class properties and methods")
        suggestions.append("- Try using more generic terms (e.g., 'font', 'glyph', 'layer')")
        suggestions.append("- Use `api_get_python_class` to view complete member list for a specific class")
        return "\n".join(suggestions)

    def _deduplicate_and_sort(self, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Deduplicate and sort search results

        Sorting rules:
        1. Sort by score in descending order
        2. When scores are equal, symbol layer takes priority over member layer

        Args:
            results: Search results list

        Returns:
            Deduplicated and sorted results list
        """
        # Deduplicate: use (type, class, name) as unique key
        seen = set()
        unique_results = []
        for r in results:
            # Create unique key
            key = (r.get('type'), r.get('class', ''), r.get('name'))
            if key not in seen:
                seen.add(key)
                unique_results.append(r)

        # Sort: by score descending, symbol layer first when scores are equal
        def sort_key(item: dict[str, Any]) -> tuple[float, int]:
            score = item.get('score', 0)
            # match_type weight: symbol=1, member=0
            match_type_weight = 1 if item.get('match_type') == 'symbol' else 0
            return (-score, -match_type_weight)

        unique_results.sort(key=sort_key)
        return unique_results

    def _format_layered_results(self, query: str, results: list[dict[str, Any]]) -> str:
        """Format layered search results

        Based on #72/#73 match_type mechanism, display results grouped by layer.

        Args:
            query: Search keyword
            results: Search results list (containing match_type field)

        Returns:
            Formatted layered results string
        """
        # Separate symbol layer and member layer results
        symbol_results = [r for r in results if r.get('match_type') == 'symbol']
        member_results = [r for r in results if r.get('match_type') == 'member']

        output = [f"🐍 Python API Search \"{query}\" found {len(results)} items:\n"]

        # API type icon mapping
        type_icons = {
            'class': '📦',
            'property': '⚙️',
            'method': '🔧',
            'function': '⚡',
            'constant': '🔢'
        }

        # API type names
        type_names = {
            'class': 'class',
            'property': 'property',
            'method': 'method',
            'function': 'function',
            'constant': 'constant'
        }

        item_index = 1

        # Symbol layer results
        if symbol_results:
            output.append("📌 **Symbol Layer Matches** (classes/functions/constants)")
            for item in symbol_results:
                item_type = item.get('type', 'unknown')
                icon = type_icons.get(item_type, '❓')
                type_name = type_names.get(item_type, 'unknown')

                if item_type == 'class':
                    output.append(f"{item_index}. {icon} **{item['name']}** ({type_name})")
                    output.append(f"   💡 Use `api_get_python_class {item['name']}` to view details")
                elif item_type == 'function':
                    output.append(f"{item_index}. {icon} **{item['name']}()** ({type_name})")
                    output.append("   💡 Global function, can be used directly")
                elif item_type == 'constant':
                    output.append(f"{item_index}. {icon} **{item['name']}** ({type_name})")
                    output.append("   💡 Global constant, can be used directly")

                item_index += 1
            output.append("")  # Empty line separator

        # Member layer results
        if member_results:
            output.append("📋 **Member Layer Matches** (class properties/methods)")
            for item in member_results:
                item_type = item.get('type', 'unknown')
                icon = type_icons.get(item_type, '❓')
                type_name = type_names.get(item_type, 'unknown')
                class_name = item.get('class', '')

                if item_type == 'property':
                    output.append(f"{item_index}. {icon} **{class_name}.{item['name']}** ({type_name})")
                    output.append(f"   💡 Use `api_get_python_member {class_name} {item['name']} property` to view details")
                elif item_type == 'method':
                    output.append(f"{item_index}. {icon} **{class_name}.{item['name']}()** ({type_name})")
                    output.append(f"   💡 Use `api_get_python_member {class_name} {item['name']} method` to view details")

                item_index += 1
            output.append("")  # Empty line separator

        # Footer hints
        output.append("---")
        output.append("📌 **Hint**: Use the commands above to get complete API docs, parameter descriptions, and usage examples")
        if symbol_results and member_results:
            output.append("💡 **Advanced**: Use `scope='members'` to search class members only, skipping symbol layer")

        return "\n".join(output)

    def get_class_info(self, class_name: str, detail_level: str = 'standard') -> dict:
        """Get class information - simplified version (returns list format directly)

        Args:
            class_name: Class name
            detail_level: Detail level (temporarily kept for compatibility, may be removed in future)

        Returns:
            Class info dictionary (properties and methods are in list format)
        """
        # Return accessor's raw output directly, no complex transformation
        class_info = self.accessor.get_class(class_name)

        # Keep detail_level parameter for backward compatibility, but doesn't affect data structure
        # properties and methods are always in list format
        return class_info

    def get_all_classes(self) -> list[str]:
        """Get all class names (backward compatible)"""
        return self.accessor.symbols.get('classes', [])

    def get_all_functions(self) -> list[str]:
        """Get all function names (backward compatible)"""
        return self.accessor.symbols.get('functions', [])

    def get_all_constants(self) -> list[str]:
        """Get all constant names (backward compatible)"""
        return self.accessor.symbols.get('constants', [])

    def get_class_overview(self, class_name: str) -> dict:
        """Get class overview (backward compatible with old API)

        Args:
            class_name: Class name

        Returns:
            Class info dictionary
        """
        return self.get_class_info(class_name, detail_level='standard')

    def get_class_member(self, class_name: str, member_name: str, member_type: str) -> dict:
        """Get class member information

        Args:
            class_name: Class name
            member_name: Member name
            member_type: Member type, must be 'property' or 'method'

        Returns:
            Member info dictionary
        """
        if member_type == "property":
            return self.accessor.get_property(class_name, member_name)

        elif member_type == "method":
            return self.accessor.get_method(class_name, member_name)

        else:
            return {'error': f'Invalid member_type: {member_type}, please use "property" or "method"'}
