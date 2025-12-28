"""
Plugin API Manager - Uses SDK Native Accessor
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

class PluginAPIManager:
    """Plugin API Manager - Uses SDK Native Accessor to read plugins.py directly"""

    def __init__(self, api_file: Any = None, sdk_accessor: Any = None) -> None:
        """Initialize Plugin API Manager

        Args:
            api_file: Deprecated, kept for backward compatibility
            sdk_accessor: SDK Native Accessor instance (required)
        """
        if sdk_accessor is None:
            raise ValueError("sdk_accessor is a required parameter")

        self.sdk_accessor = sdk_accessor
        logger.info("Plugin API Manager initialized with SDK Native Accessor")

    def search(self, query: str) -> str:
        """Search Plugin API (using SDK Native Accessor)"""
        if not query.strip():
            return "Please provide a search keyword"

        search_results = self.sdk_accessor.search_plugin_classes(query)
        if search_results:
            return self._format_native_search_results(query, search_results[:10])
        else:
            return f"No Plugin API found related to '{query}'"

    def _format_native_search_results(self, query: str, results: list[dict]) -> str:
        """Format Native Accessor search results"""
        output = [f"🔍 Found {len(results)} related Plugin API classes:\n"]

        for i, result in enumerate(results, 1):
            output.append(f"**{i}. {result['name']}** (match score: {result.get('score', 0):.1f})")

            # Base class
            if result.get('base_class'):
                output.append(f"   Inherits from: {result['base_class']}")

            # Documentation
            doc = result.get('doc', '').strip()
            if doc:
                # Show only first line of documentation
                first_line = doc.split('\n')[0]
                output.append(f"   📝 {first_line}")

            # Match type
            match_type = result.get('match_type')
            if match_type == 'name':
                output.append("   ✓ Matches class name")
            elif match_type == 'doc':
                output.append("   ✓ Matches documentation")
            elif match_type == 'methods':
                matching_methods = result.get('matching_methods', [])
                if matching_methods:
                    methods_str = ', '.join(matching_methods[:3])
                    output.append(f"   ✓ Matches methods: {methods_str}")

            # Method count
            methods = result.get('methods', {})
            if methods:
                output.append(f"   🔧 Contains {len(methods)} methods")

            output.append("")  # Empty line

        output.append("💡 Use `get_plugin_details(class_name)` to view details")
        return '\n'.join(output)

    def get_class_overview(self, class_name: str) -> dict[str, Any]:
        """Get class details (using SDK Native Accessor)"""
        plugin_class = self.sdk_accessor.get_plugin_class(class_name)
        if plugin_class:
            return {
                "name": plugin_class["name"],
                "description": plugin_class.get("doc", "No description"),
                "type": "plugin_class",
                "source": "Plugin API (Native)",
                "base_class": plugin_class.get("base_class", ""),
                "methods": plugin_class.get("methods", {}),
                "line_number": plugin_class.get("line_number", 0)
            }
        return {"error": f"Class '{class_name}' not found"}

    def get_class_member(self, class_name: str, member_name: str, member_type: str) -> dict[str, Any]:
        """Get class member details (using SDK Native Accessor)

        Args:
            class_name: Class name
            member_name: Member name (method name)
            member_type: Member type, must be "property" or "method"

        Returns:
            Member details dictionary
        """
        # Get complete class information
        plugin_class = self.sdk_accessor.get_plugin_class(class_name)
        if not plugin_class:
            return {"error": f"Class '{class_name}' not found"}

        # Search methods
        methods = plugin_class.get("methods", {})
        if member_name in methods:
            method_info = methods[member_name]
            return {
                "class_name": class_name,
                "member_name": member_name,
                "member_type": "method",
                "description": method_info.get("doc", "No description"),
                "signature": method_info.get("signature", ""),
                "parameters": method_info.get("params", []),
                "objc_selector": method_info.get("objc_selector"),
                "line_number": method_info.get("line_number", 0)
            }

        return {"error": f"Method '{member_name}' not found in class '{class_name}'"}

    def get_statistics(self) -> dict[str, int]:
        """Get statistics (using SDK Native Accessor)"""
        plugin_classes = self.sdk_accessor.list_plugin_classes()
        total_methods = sum(
            len(cls.get("methods", {}))
            for cls in plugin_classes
        )

        return {
            "plugin_classes": len(plugin_classes),
            "total_methods": total_methods
        }
