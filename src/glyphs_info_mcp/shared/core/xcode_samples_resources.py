#!/usr/bin/env python3
"""
Xcode Samples Resource Manager
Manages Glyphs SDK Xcode Samples as MCP resources (Issue #37)
"""
import re
from pathlib import Path
from typing import Any

from glyphs_info_mcp.shared.core.sdk_native_accessor import SDKNativeAccessor


class XcodeSamplesResourceManager:
    """Xcode Samples Resource Manager

    Manages Xcode plugin samples as MCP resources.
    Reuses SDKNativeAccessor for sample scanning and parsing.
    """

    def __init__(self, sdk_path: Path | None = None):
        """Initialize resource manager

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
        self._samples_cache: dict[str, dict[str, Any]] | None = None

    def scan_xcode_samples(self) -> dict[str, dict[str, Any]]:
        """Scan all Xcode plugin samples

        Reuses SDKNativeAccessor.list_xcode_samples() - no need to reimplement scanning.

        Returns:
            Sample dictionary, key is sample ID, value is sample info
        """
        samples = {}
        xcode_samples = self.native_accessor.list_xcode_samples()

        for sample in xcode_samples:
            sample_id = self._generate_sample_id(sample["name"])
            samples[sample_id] = {
                "id": sample_id,
                "name": sample["name"],
                "path": sample["path"],
                "has_xcode_project": sample["has_xcode_project"],
                "readme": sample.get("readme", ""),
                "source_files": sample["source_files"],
                "source_file_count": sample["source_file_count"],
            }

        return samples

    def _generate_sample_id(self, sample_name: str) -> str:
        """Generate sample ID from sample name

        Converts CamelCase to snake_case

        Examples:
        - "InspectorDemo" → "inspector_demo"
        - "CustomParameterUI" → "custom_parameter_u_i"
        - "Plugin With Window" → "plugin_with_window"

        Args:
            sample_name: Sample name

        Returns:
            Sample ID
        """
        # First, convert CamelCase to snake_case
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", sample_name)
        s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
        # Then replace spaces with underscores and lowercase
        result = s2.lower().replace(" ", "_")
        # Remove consecutive underscores
        while "__" in result:
            result = result.replace("__", "_")
        return result

    def get_samples(self) -> dict[str, dict[str, Any]]:
        """Get all samples (with caching)

        Returns:
            Dictionary of all samples
        """
        if self._samples_cache is None:
            self._samples_cache = self.scan_xcode_samples()
        return self._samples_cache

    def get_sample_by_id(self, sample_id: str) -> dict[str, Any] | None:
        """Get specific sample by ID (with full source code)

        Uses native_accessor.get_xcode_sample() to fetch complete content.

        Args:
            sample_id: Sample ID

        Returns:
            Sample info with full source code or None
        """
        samples = self.get_samples()
        sample_meta = samples.get(sample_id)

        if not sample_meta:
            return None

        # Get full sample (with source code)
        full_sample = self.native_accessor.get_xcode_sample(sample_meta["name"])

        if full_sample:
            return {**sample_meta, **full_sample}

        return sample_meta

    def get_resource_list(self) -> list[dict[str, str]]:
        """Get MCP resource list format

        Returns:
            List suitable for MCP resource registration
        """
        samples = self.get_samples()
        resources = []

        for sample_id, info in samples.items():
            # Extract first 100 chars of README as description
            description = info.get("readme", "Xcode plugin sample")[:100]
            if len(info.get("readme", "")) > 100:
                description += "..."

            resources.append(
                {
                    "uri": f"glyphs://xcode-sample/{sample_id}",
                    "name": f"Xcode Sample: {info['name']}",
                    "description": description,
                    "mimeType": "text/x-objective-c",
                }
            )

        return resources
