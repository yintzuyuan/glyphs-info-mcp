#!/usr/bin/env python3
"""
Xcode Templates Resource Manager
Manages Glyphs SDK Xcode Templates as MCP resources
"""
from pathlib import Path
from typing import Any

from glyphs_info_mcp.shared.core.sdk_native_accessor import SDKNativeAccessor


class XcodeTemplatesResourceManager:
    """Xcode Templates Resource Manager

    Manages Xcode plugin templates (.xctemplate) as MCP resources.
    Provides simplified access compared to Python templates - no AST parsing needed,
    just direct file reading for .h, .m, .plist files.
    """

    def __init__(self, sdk_path: Path | None = None):
        """
        Initialize resource manager

        Args:
            sdk_path: GlyphsSDK root directory path

        Raises:
            FileNotFoundError: If SDK path does not exist
            ValueError: If SDK path is not a directory
        """
        if sdk_path is None:
            # Default path: read from project root's data/official/
            current_dir = Path(__file__).parent
            sdk_path = (
                current_dir.parent.parent.parent / "data" / "official" / "GlyphsSDK"
            )

        self.sdk_path = Path(sdk_path)

        # Validate SDK path exists and is a directory
        if not self.sdk_path.exists():
            raise FileNotFoundError(f"SDK path does not exist: {self.sdk_path}")
        if not self.sdk_path.is_dir():
            raise ValueError(f"SDK path is not a directory: {self.sdk_path}")

        self.native_accessor = SDKNativeAccessor(self.sdk_path)
        self._templates_cache: dict[str, dict[str, Any]] | None = None

    def scan_xcode_templates(self) -> dict[str, dict[str, Any]]:
        """
        Scan all Xcode plugin templates

        Reuses SDKNativeAccessor.list_xcode_templates() - no need to reimplement scanning.

        Returns:
            Template dictionary, key is template ID, value is template info
        """
        templates = {}
        xcode_templates = self.native_accessor.list_xcode_templates()

        for template in xcode_templates:
            template_id = self._generate_template_id(template["name"])
            templates[template_id] = {
                "id": template_id,
                "name": template["name"],
                "type": template["type"],
                "path": template["path"],
                "file_count": template["file_count"],
                "description": template.get("description", ""),
                "files": template["files"],
            }

        return templates

    def _generate_template_id(self, template_name: str) -> str:
        """
        Generate template ID from template name

        Examples:
        - "Glyphs Reporter" → "reporter"
        - "Glyphs Filter Plugin" → "filter"
        - "Glyphs Plugin Base" → "plugin_base"

        Args:
            template_name: Template name

        Returns:
            Template ID
        """
        # Remove "Glyphs" and "Plugin" keywords, lowercase, convert spaces to underscores
        id_str = template_name.replace("Glyphs ", "").replace(" Plugin", "")
        return id_str.lower().replace(" ", "_")

    def get_templates(self) -> dict[str, dict[str, Any]]:
        """
        Get all templates (with caching)

        Returns:
            Dictionary of all templates
        """
        if self._templates_cache is None:
            self._templates_cache = self.scan_xcode_templates()
        return self._templates_cache

    def get_template_by_id(self, template_id: str) -> dict[str, Any] | None:
        """
        Get specific template by ID (with full source code)

        Uses native_accessor.get_xcode_template() to fetch complete content.

        Args:
            template_id: Template ID

        Returns:
            Template info with full source code or None
        """
        templates = self.get_templates()
        template_meta = templates.get(template_id)

        if not template_meta:
            return None

        # Get full template (with source code)
        full_template = self.native_accessor.get_xcode_template(template_meta["name"])

        if full_template:
            return {**template_meta, **full_template}

        return template_meta

    def get_templates_by_type(self, template_type: str) -> dict[str, dict[str, Any]]:
        """
        Get templates by type

        Args:
            template_type: Template type (e.g., "reporter", "filter")

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
                    "uri": f"glyphs://xcode-template/{template_id}",
                    "name": f"Xcode Template: {info['name']}",
                    "description": f"{info['description']} ({info['type']} - {info['file_count']} files)",
                    "mimeType": "text/x-objective-c",
                }
            )

        return resources
