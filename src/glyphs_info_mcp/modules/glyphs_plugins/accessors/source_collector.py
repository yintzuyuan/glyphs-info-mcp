"""
SourceCollector - Source code collector

Used to collect all source code files in plugin directory, grouped by type
"""

import logging
from pathlib import Path

from glyphs_info_mcp.modules.glyphs_plugins.accessors.file_classifier import FileClassifier

logger = logging.getLogger(__name__)


class SourceCollector:
    """Source code collector"""

    def __init__(
        self,
        classifier: FileClassifier,
        max_file_size: int = 100_000,  # 100KB per file
        max_total_size: int = 500_000,  # 500KB total
        include_ui_files: bool = True,
    ):
        """
        Initialize source code collector

        Args:
            classifier: File classifier instance
            max_file_size: Single file size limit (bytes)
            max_total_size: Total size limit (bytes)
            include_ui_files: Whether to include UI files (.xib)
        """
        self.classifier = classifier
        self.max_file_size = max_file_size
        self.max_total_size = max_total_size
        self.include_ui_files = include_ui_files

    def collect_source_files(self, plugin_path: Path) -> dict[str, list[Path]]:
        """
        Collect all source code files in plugin directory

        Return format:
        {
            "python_source": [Path, Path, ...],
            "objc_header": [Path, ...],
            "objc_impl": [Path, ...],
            "ui_xib": [Path, ...],
            "resource": [Path, ...],
            "binary_stub": [Path, ...],
            "compiled": [Path, ...],
        }

        Args:
            plugin_path: Plugin directory path

        Returns:
            Dictionary of file paths grouped by type
        """
        if not plugin_path.exists() or not plugin_path.is_dir():
            return {}

        result: dict[str, list[Path]] = {}
        total_size = 0

        try:
            # Recursively scan all files
            all_files = []
            for item in plugin_path.rglob("*"):
                # Exclude hidden files and directories
                if any(part.startswith(".") for part in item.parts):
                    continue

                # Exclude __pycache__
                if "__pycache__" in item.parts:
                    continue

                if item.is_file():
                    all_files.append(item)

            # Sort by filename (ensure predictable results)
            all_files.sort()

            # Classify and filter files
            for file_path in all_files:
                # Check file size
                try:
                    file_size = file_path.stat().st_size
                except OSError:
                    continue

                # Single file size limit
                if file_size > self.max_file_size:
                    logger.debug(f"Skipping large file {file_path.name} ({file_size} bytes)")
                    continue

                # Total size limit
                if total_size + file_size > self.max_total_size:
                    logger.debug(
                        f"Reached total size limit ({self.max_total_size} bytes), stopping collection"
                    )
                    break

                # Get file category
                category = self.classifier.get_file_category(file_path)

                # Exclude UI files (if set to False)
                if not self.include_ui_files and category == "ui_xib":
                    continue

                # Exclude unknown types
                if category == "unknown":
                    continue

                # Add to corresponding category
                if category not in result:
                    result[category] = []

                result[category].append(file_path)
                total_size += file_size

        except Exception as e:
            logger.error(f"Error collecting source code: {e}")
            return {}

        return result
