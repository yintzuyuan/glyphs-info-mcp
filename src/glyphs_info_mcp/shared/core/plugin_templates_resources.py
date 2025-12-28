#!/usr/bin/env python3
"""
Plugin Templates Resource Manager
Manages Glyphs SDK Python Templates as MCP resources
"""
from pathlib import Path
from typing import Any


class PluginTemplatesResourceManager:
    """Plugin Templates Resource Manager"""

    def __init__(self, sdk_path: Path | None = None):
        """
        Initialize resource manager

        Args:
            sdk_path: GlyphsSDK root directory path
        """
        if sdk_path is None:
            # Default path: read from project root's data/official/
            current_dir = Path(__file__).parent
            sdk_path = (
                current_dir.parent.parent.parent / "data" / "official" / "GlyphsSDK"
            )

        self.sdk_path = Path(sdk_path)
        self.templates_path = self.sdk_path / "Python Templates"
        self._templates_cache: dict[str, dict[str, Any]] | None = None

    def scan_plugin_templates(self) -> dict[str, dict[str, Any]]:
        """
        Scan all plugin.py templates

        Returns:
            Template dictionary, key is template ID, value is template info
        """
        if not self.templates_path.exists():
            return {}

        templates = {}

        # Scan all plugin.py files
        for plugin_file in self.templates_path.rglob("plugin.py"):
            # Parse path structure to determine template type
            relative_path = plugin_file.relative_to(self.templates_path)
            template_info = self._parse_template_path(plugin_file, relative_path)

            if template_info:
                template_id = self._generate_template_id(relative_path)
                templates[template_id] = template_info

        return templates

    def _parse_template_path(
        self, plugin_file: Path, relative_path: Path
    ) -> dict[str, Any] | None:
        """
        Parse template path and extract info

        Args:
            plugin_file: Full path to plugin.py file
            relative_path: Path relative to Python Templates

        Returns:
            Template info dictionary
        """
        try:
            # Read file content (first 500 chars for description)
            content = plugin_file.read_text(encoding="utf-8")

            # Extract type and description info
            path_parts = relative_path.parts
            template_type = "unknown"
            template_subtype = "default"
            template_name = "Plugin Template"

            # Determine template type based on path structure
            if len(path_parts) >= 2:
                template_type = path_parts[0].lower()  # Filter, Reporter, etc.
                if len(path_parts) >= 3:
                    template_subtype = path_parts[
                        1
                    ]  # "without dialog", "with xib", etc.

            # Extract template name from file content
            lines = content.split("\n")
            for line in lines[:20]:  # Check first 20 lines
                if "Filter" in line and (
                    "plugin" in line.lower() or "plug-in" in line.lower()
                ):
                    template_name = line.strip().replace("#", "").strip()
                    break
                elif "class ____PluginClassName____" in line:
                    # Check parent class to determine type
                    if "(" in line and ")" in line:
                        parent_class = line.split("(")[1].split(")")[0].strip()
                        template_name = f"{parent_class} Template"
                    break

            return {
                "id": self._generate_template_id(relative_path),
                "name": template_name,
                "type": template_type,
                "subtype": template_subtype,
                "path": str(plugin_file),
                "relative_path": str(relative_path),
                "content": content,
                "size": len(content),
                "description": self._extract_description(content),
                "usage": self._extract_usage_info(content, template_type),
            }
        except Exception as e:
            print(f"Failed to parse template {plugin_file}: {e}")
            return None

    def _generate_template_id(self, relative_path: Path) -> str:
        """
        Generate template ID

        Args:
            relative_path: Relative path

        Returns:
            Template ID
        """
        # Generate concise ID using path structure
        parts = relative_path.parts[:-1]  # Remove plugin.py
        return "_".join(part.lower().replace(" ", "_") for part in parts)

    def _extract_description(self, content: str) -> str:
        """Extract description from file content"""
        lines = content.split("\n")
        descriptions = []

        for line in lines[:15]:
            line = line.strip()
            if line.startswith("#") and not line.startswith("###"):
                # Remove # symbol and clean up
                desc = line.lstrip("#").strip()
                if desc and "encoding" not in desc and len(desc) > 3:
                    descriptions.append(desc)

        return " ".join(descriptions[:2])  # Take first two valid descriptions

    def _extract_usage_info(self, content: str, template_type: str) -> dict[str, Any]:
        """Extract usage info"""
        info: dict[str, Any] = {
            "plugin_type": template_type,
            "base_class": "Unknown",
            "requirements": [],
        }

        # Extract base class
        for line in content.split("\n"):
            if "class ____PluginClassName____" in line and "(" in line:
                base_class = line.split("(")[1].split(")")[0].strip()
                info["base_class"] = base_class
                break

        # Extract import info
        imports = []
        for line in content.split("\n"):
            if line.strip().startswith("from ") or line.strip().startswith("import "):
                imports.append(line.strip())
        info["requirements"] = imports[:5]  # Take first 5 imports

        return info

    def get_templates(self) -> dict[str, dict[str, Any]]:
        """
        Get all templates (with caching)

        Returns:
            Dictionary of all templates
        """
        if self._templates_cache is None:
            self._templates_cache = self.scan_plugin_templates()
        return self._templates_cache

    def get_template_by_id(self, template_id: str) -> dict[str, Any] | None:
        """
        Get specific template by ID

        Args:
            template_id: Template ID

        Returns:
            Template info or None
        """
        templates = self.get_templates()
        return templates.get(template_id)

    def get_templates_by_type(self, template_type: str) -> dict[str, dict[str, Any]]:
        """
        Get templates by type

        Args:
            template_type: Template type (e.g., "filter", "reporter")

        Returns:
            Dictionary of matching templates
        """
        templates = self.get_templates()
        return {
            tid: info
            for tid, info in templates.items()
            if info["type"].lower() == template_type.lower()
        }

    def get_template_types(self) -> list[str]:
        """
        Get all available template types

        Returns:
            List of template types
        """
        templates = self.get_templates()
        types = set(info["type"] for info in templates.values())
        return sorted(list(types))

    def get_resource_list(self) -> list[dict[str, str]]:
        """
        Get MCP resource list format

        Returns:
            List suitable for MCP resource registration
        """
        templates = self.get_templates()
        resources = []

        for template_id, info in templates.items():
            resources.append(
                {
                    "uri": f"glyphs://plugin-template/{template_id}",
                    "name": f"Plugin Template: {info['name']}",
                    "description": f"{info['description']} ({info['type']} - {info['subtype']})",
                    "mimeType": "text/x-python",
                }
            )

        return resources
