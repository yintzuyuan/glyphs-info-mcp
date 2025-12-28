#!/usr/bin/env python3
"""
Vanilla Tools - Local Vanilla UI Query Tool

Fully depends on vanilla source code in local Repositories,
removes all network search and JSON index dependencies.
"""

import logging
import sys
from pathlib import Path

# Use shared core library
project_root = Path(__file__).parent.parent.parent
shared_core_path = str(project_root / "src" / "shared")
if shared_core_path not in sys.path:
    sys.path.insert(0, shared_core_path)

from glyphs_info_mcp.shared.core.installation_helper import InstallationHelper
from glyphs_info_mcp.shared.core.vanilla_local_accessor import VanillaLocalAccessor

logger = logging.getLogger(__name__)


class VanillaTools:
    """Vanilla UI Tools - Fully localized"""

    def __init__(self, vanilla_accessor: VanillaLocalAccessor):
        """Initialize Vanilla Tools

        Args:
            vanilla_accessor: Vanilla Local Accessor instance
        """
        self.vanilla_accessor = vanilla_accessor

    def search_vanilla_ui(
        self, query: str, max_results: int = 5
    ) -> str:
        """Search local vanilla UI components (fully local search)

        Args:
            query: Search keyword
            max_results: Maximum number of results

        Returns:
            Formatted search results or error message
        """
        # Check if vanilla is available
        if not self.vanilla_accessor.is_available():
            return InstallationHelper.get_installation_message("vanilla")

        # Local search
        results = self.vanilla_accessor.search_vanilla_classes(
            query, max_results=max_results
        )

        # Provide suggestions when no results
        if not results:
            available_items = self.vanilla_accessor.list_vanilla_classes()
            return InstallationHelper.get_not_found_message(
                "vanilla", query, available_items
            )

        # Format results
        return self._format_search_results(results, query)

    def get_vanilla_ui(
        self, ui_item: str, include_source: bool = True
    ) -> str:
        """Read complete vanilla UI component information from local

        Args:
            ui_item: UI component name (e.g., "Button", "TextBox")
            include_source: Whether to include complete source code

        Returns:
            Formatted UI component information or error message
        """
        # Check if vanilla is available
        if not self.vanilla_accessor.is_available():
            return InstallationHelper.get_installation_message("vanilla")

        # Get class info from local
        class_info = self.vanilla_accessor.get_vanilla_class(ui_item)

        # Class not found
        if not class_info:
            available_items = self.vanilla_accessor.list_vanilla_classes()
            return InstallationHelper.get_not_found_message(
                "vanilla", ui_item, available_items
            )

        # Format output
        return self._format_class_info(class_info, include_source)

    def list_vanilla_ui(self) -> str:
        """List all available vanilla UI components

        Returns:
            Formatted UI component list or error message
        """
        # Check if vanilla is available
        if not self.vanilla_accessor.is_available():
            return InstallationHelper.get_installation_message("vanilla")

        # Get all classes
        classes = self.vanilla_accessor.list_vanilla_classes()

        if not classes:
            return """
⚠️  No vanilla UI components found

Possible reasons:
• Vanilla installation is incomplete
• __init__.py file is corrupted

Suggestion: Reinstall vanilla via Glyphs Plugin Manager
"""

        # Format list
        return self._format_class_list(classes)

    def _format_search_results(
        self, results: list, query: str
    ) -> str:
        """Format search results

        Args:
            results: Search results list
            query: Search query

        Returns:
            Formatted search results
        """
        output = [f"🔍 Vanilla UI Search Results: '{query}'"]
        output.append(f"Found {len(results)} related components\n")

        for i, result in enumerate(results, 1):
            class_name = result["class_name"]
            docstring = result["docstring"]
            score = result["score"]

            # Show relevance indicator
            relevance = "🎯" if score >= 0.8 else "✓"

            output.append(f"{relevance} {i}. {class_name}")

            # Show doc summary (limit length)
            if docstring:
                doc_preview = docstring.split('\n')[0][:100]
                output.append(f"   {doc_preview}")

            output.append("")

        output.append("💡 Use api_get_vanilla_ui to view complete information")

        return "\n".join(output)

    def _format_class_info(
        self, class_info: dict, include_source: bool = True
    ) -> str:
        """Format class information

        Args:
            class_info: Class information dictionary
            include_source: Whether to include complete source code

        Returns:
            Formatted class information
        """
        class_name = class_info["class_name"]
        docstring = class_info["docstring"]
        methods = class_info["methods"]
        source = class_info["source"]
        file_path = class_info["file_path"]

        output = [f"📦 Vanilla UI Component: {class_name}"]
        output.append("=" * 50)

        # Docstring
        if docstring:
            output.append("\n📝 Description:")
            output.append(docstring)

        # Methods list
        if methods:
            output.append(f"\n🔧 Methods ({len(methods)}):")
            for method in methods:
                method_name = method["name"]
                params = method["parameters"]

                # Format parameters
                param_str = ", ".join(
                    f"{p['name']}" +
                    (f"={p['default']}" if p.get('default') else "")
                    for p in params
                )

                output.append(f"  • {method_name}({param_str})")

                # Method doc
                if method["docstring"]:
                    doc_lines = method["docstring"].split('\n')
                    output.append(f"    → {doc_lines[0]}")

        # File path
        output.append("\n📍 File Location:")
        output.append(f"  {file_path}")

        # Complete source code
        if include_source:
            output.append("\n💻 Complete Source Code:")
            output.append("```python")
            output.append(source)
            output.append("```")

        return "\n".join(output)

    def _format_class_list(self, classes: list) -> str:
        """Format class list

        Args:
            classes: Class name list

        Returns:
            Formatted list
        """
        output = [f"📋 Vanilla UI Component List ({len(classes)} total)"]
        output.append("=" * 50)
        output.append("")

        # Group by category (simple classification)
        widgets = []
        windows = []
        others = []

        for class_name in classes:
            if "Window" in class_name or "Sheet" in class_name:
                windows.append(class_name)
            elif any(
                w in class_name
                for w in ["Button", "Box", "Text", "Edit", "List", "Slider"]
            ):
                widgets.append(class_name)
            else:
                others.append(class_name)

        # Output groups
        if windows:
            output.append("🪟 Window Classes:")
            for name in sorted(windows):
                output.append(f"  • {name}")
            output.append("")

        if widgets:
            output.append("🎛️ UI Controls:")
            for name in sorted(widgets):
                output.append(f"  • {name}")
            output.append("")

        if others:
            output.append("📦 Other Components:")
            for name in sorted(others):
                output.append(f"  • {name}")

        output.append("")
        output.append("💡 Use api_search_vanilla_ui to search specific components")
        output.append("💡 Use api_get_vanilla_ui to view complete information")

        return "\n".join(output)
