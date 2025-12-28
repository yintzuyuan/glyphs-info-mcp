"""
SDK Search Result Formatter
Responsible for formatting search results into user-friendly display format
"""
from typing import Any


class SDKResultFormatter:
    """SDK result formatter"""

    # Type icon mapping
    TYPE_ICONS = {
        "guide": "📚",
        "implementation": "🔧",
        "example": "💡",
        "template": "📋",
        "utility": "🛠️"
    }

    # Type display names
    TYPE_NAMES = {
        "guide": "Guide",
        "implementation": "Implementation",
        "example": "Example",
        "template": "Template",
        "utility": "Utility"
    }

    def format_results(self, results: list[dict[str, Any]], query: str) -> str:
        """
        Format multiple search results

        Args:
            results: Search results list
            query: Search query

        Returns:
            Formatted string
        """
        if not results:
            return f"🔍 Found 0 related SDK content:\n\nNo SDK content related to '{query}' found."

        formatted = f"🔍 Found {len(results)} related SDK content:\n\n"

        for i, result in enumerate(results, 1):
            formatted += f"**{i}. {self.format_single_result(result)}**\n\n"

        return formatted.rstrip()

    def format_single_result(self, result: dict[str, Any]) -> str:
        """
        Format a single search result

        Args:
            result: Single search result

        Returns:
            Formatted string
        """
        result_type = result["type"]
        icon = self.TYPE_ICONS.get(result_type, "📄")
        type_name = self.TYPE_NAMES.get(result_type, result_type)

        # Extract title
        title = self._extract_title(result)

        # Format basic info
        formatted = f"{icon} {type_name}: {title}\n"

        # Add content description
        content = result.get("content", "")
        if content:
            # Limit content length
            truncated_content = self._truncate_content(content, 200)
            formatted += f"📝 Description: {truncated_content}\n"

        # Add file path
        path = result["path"]
        short_path = self._shorten_path(path)
        formatted += f"📄 File: {short_path}\n"

        # Add category label
        category = result.get("category", "")
        if category:
            category_display = self._format_category(category)
            formatted += f"🏷️ Type: {category_display}"

        return formatted

    def _extract_title(self, result: dict[str, Any]) -> str:
        """Extract title from result"""
        path = result["path"]

        # Extract different titles based on type
        if result["type"] == "guide":
            # Extract guide name from path
            if "Python Templates" in path:
                parts = path.split("/")
                for i, part in enumerate(parts):
                    if part == "Python Templates" and i + 1 < len(parts):
                        return f"{parts[i + 1]} Plugin Development"
            return result["name"]

        elif result["type"] == "implementation":
            # Extract class or function name from content
            content = result.get("content", "")
            if "class " in content:
                # Extract class name
                class_match = content.split("class ")[1].split("(")[0].split(":")[0].strip()
                return class_match
            return result["name"]

        elif result["type"] == "example":
            # Extract example name from path
            parts = path.split("/")
            for part in parts:
                if "Tools" in part or "Plugin" in part:
                    return part
            return result["name"]

        elif result["type"] == "template":
            # Extract template type from path
            if "Python Templates" in path:
                parts = path.split("/")
                for i, part in enumerate(parts):
                    if part == "Python Templates" and i + 1 < len(parts):
                        return f"{parts[i + 1]} Template"
            return result["name"]

        return result["name"]

    def _truncate_content(self, content: str, max_length: int) -> str:
        """Truncate content to specified length"""
        if len(content) <= max_length:
            return content

        # Truncate at space to avoid cutting words
        truncated = content[:max_length]
        last_space = truncated.rfind(' ')

        if last_space > max_length * 0.8:  # If space position is not too far
            truncated = truncated[:last_space]

        return truncated + "..."

    def _shorten_path(self, path: str) -> str:
        """Shorten path display"""
        # Remove absolute path prefix, show only path relative to SDK
        if "GlyphsSDK/" in path:
            return path.split("GlyphsSDK/", 1)[1]

        # If path is too long, show only last few parts
        parts = path.split("/")
        if len(parts) > 4:
            return ".../" + "/".join(parts[-3:])

        return path

    def _format_category(self, category: str) -> str:
        """Format category name"""
        category_map = {
            "template_guide": "Template Guide",
            "sample_guide": "Sample Guide",
            "general_guide": "General Guide",
            "plugin_framework": "Plugin Framework",
            "drawing_tools": "Drawing Tools",
            "ui_components": "UI Components",
            "other_implementation": "Other Implementation",
            "tool_sample": "Tool Sample",
            "plugin_sample": "Plugin Sample",
            "other_sample": "Other Sample",
            "filter_template": "Filter Template",
            "reporter_template": "Reporter Template",
            "tool_template": "Tool Template",
            "palette_template": "Palette Template",
            "general_template": "General Template",
            "other_template": "Other Template"
        }

        return category_map.get(category, category)
