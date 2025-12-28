#!/usr/bin/env python3
"""
Light Table Native Accessor - Directly parses Light Table Python API

Uses AST parsing to extract API definitions from Light Table plugin's Python API file,
providing search and detailed info query functionality for enums, classes, and methods.
"""

import ast
import logging
from pathlib import Path
from typing import Any

from glyphs_info_mcp.shared.core.repository_scanner import RepositoryScanner

logger = logging.getLogger(__name__)


class LightTableNativeAccessor:
    """Light Table Python API native accessor - fully relies on AST parsing"""

    def __init__(self, repository_scanner: RepositoryScanner):
        """Initialize Light Table Native Accessor

        Args:
            repository_scanner: Repository Scanner instance
        """
        self.scanner = repository_scanner
        self.api_path: Path | None = None
        self._enums: dict[str, dict] = {}  # enum_name → enum_info
        self._classes: dict[str, dict] = {}  # class_name → class_info
        self._extensions: dict[str, list[dict]] = {}  # base_class → extension_methods
        self._parsed = False

        # Try to locate Light Table API path
        self._locate_lighttable_api()

    def _locate_lighttable_api(self) -> None:
        """Locate Light Table Python API path (with fallback support)

        Priority order:
        1. Local installed plugin: ~/Library/Application Support/Glyphs 3/Plugins/
        2. Environment variable: $LIGHTTABLE_PATH
        3. Git Submodule fallback: data/official/light-table/
        """
        # Use get_module_path() to automatically handle fallback logic
        # Use repo_name "Light-Table" from official plugin list as search keyword
        light_table_root = self.scanner.get_module_path("Light-Table")
        if not light_table_root:
            logger.warning("Light-Table not found in any location")
            return

        # Try multiple possible path structures
        possible_paths = [
            light_table_root / "Python API" / "lighttable" / "__init__.py",  # Submodule
            light_table_root / "Contents" / "Resources" / "Python API" / "lighttable" / "__init__.py",  # Plugin
        ]

        for path in possible_paths:
            if path.exists() and path.is_file():
                self.api_path = path
                logger.info(f"[light-table] Found API at: {path}")
                return

        logger.warning(f"light-table API __init__.py not found in: {light_table_root}")

    def is_available(self) -> bool:
        """Check if Light Table API is available

        Returns:
            True if Light Table API is located and accessible
        """
        return self.api_path is not None and self.api_path.exists()

    def parse_api(self) -> None:
        """Parse Light Table API file (using AST)

        Extracts:
        - Enum class definitions
        - Dataclass definitions
        - GSFont/GSGlyph/GSLayer extension methods
        """
        if not self.is_available():
            logger.warning("Light Table API not available, cannot parse")
            return

        if self._parsed:
            return  # Avoid duplicate parsing

        try:
            # Read API file
            if self.api_path is None:
                logger.warning("Light Table API path is None, cannot parse")
                return
            api_code = self.api_path.read_text(encoding="utf-8")

            # Parse using AST
            tree = ast.parse(api_code, filename=str(self.api_path))

            # Only traverse top-level nodes (avoid nested class issues)
            for node in tree.body:
                # Parse Enum classes
                if isinstance(node, ast.ClassDef):
                    self._parse_class(node)

            self._parsed = True
            logger.info(
                f"[light-table] Parsed {len(self._enums)} enums, "
                f"{len(self._classes)} classes"
            )

        except Exception as e:
            logger.error(f"Failed to parse Light Table API: {e}")

    def _parse_class(self, node: ast.ClassDef) -> None:
        """Parse class definition (Enum or Dataclass)

        Args:
            node: AST ClassDef node
        """
        try:
            class_name = node.name

            # Check if it's an Enum
            is_enum = any(
                isinstance(base, ast.Name) and hasattr(base, "id") and base.id == "Enum"
                for base in node.bases
            )

            if is_enum:
                # Parse Enum
                enum_values = {}
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and hasattr(target, "id"):
                                value_name = target.id
                                # Try to extract value
                                if isinstance(item.value, ast.Constant):
                                    enum_values[value_name] = item.value.value

                self._enums[class_name] = {
                    "name": class_name,
                    "type": "enum",
                    "values": enum_values,
                    "docstring": ast.get_docstring(node),
                }
            else:
                # Parse regular class or Dataclass
                self._classes[class_name] = {
                    "name": class_name,
                    "type": "class",
                    "docstring": ast.get_docstring(node),
                }
        except AttributeError as e:
            logger.warning(f"Skipping class node due to unexpected structure: {e}")

    def get_enums(self) -> dict[str, dict]:
        """Get all parsed enums

        Returns:
            Enum dictionary {enum_name: enum_info}
        """
        if not self._parsed:
            self.parse_api()
        return self._enums

    def get_enum_details(self, enum_name: str) -> dict[str, Any] | None:
        """Get detailed information for a specific enum

        Args:
            enum_name: Enum name

        Returns:
            Enum details, or None if not found
        """
        if not self._parsed:
            self.parse_api()
        return self._enums.get(enum_name)

    def search(self, query: str) -> list[dict]:
        """Search API items (enums, classes)

        Args:
            query: Search keyword (case-insensitive)

        Returns:
            List of matching API items
        """
        if not self._parsed:
            self.parse_api()

        query_lower = query.lower()
        results = []

        # Search enums
        for enum_name, enum_info in self._enums.items():
            if query_lower in enum_name.lower():
                results.append(enum_info)

        # Search classes
        for class_name, class_info in self._classes.items():
            if query_lower in class_name.lower():
                results.append(class_info)

        return results

    def list_all(self) -> list[dict]:
        """List all API items

        Returns:
            List of all API items (enums + classes)
        """
        if not self._parsed:
            self.parse_api()

        all_items: list[dict[str, Any]] = []
        all_items.extend(self._enums.values())
        all_items.extend(self._classes.values())
        return all_items
