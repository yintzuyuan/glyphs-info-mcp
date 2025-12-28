#!/usr/bin/env python3
"""
Vanilla Local Accessor - Local Vanilla Module Accessor

Uses AST parsing on locally installed vanilla module,
extracting class, method, parameter, and docstring information.

Design inspired by SDKNativeAccessor, fully local, no network dependency.
"""

import ast
import logging
from pathlib import Path
from typing import Any

from glyphs_info_mcp.shared.core.repository_scanner import RepositoryScanner

logger = logging.getLogger(__name__)


class VanillaLocalAccessor:
    """Vanilla local accessor - fully depends on local source code"""

    def __init__(self, repository_scanner: RepositoryScanner):
        """Initialize Vanilla Local Accessor

        Args:
            repository_scanner: Repository Scanner instance
        """
        self.scanner = repository_scanner
        self.vanilla_path: Path | None = None
        self._classes_cache: list[str] | None = None
        self._class_info_cache: dict[str, dict[str, Any]] = {}
        self._class_to_file_map: dict[str, str] = {}  # Class name -> file name mapping

        # Try to find vanilla module path
        self._locate_vanilla()

        # Build class-to-file mapping table (from __init__.py)
        self._build_class_to_file_map()

    def _locate_vanilla(self) -> None:
        """Locate vanilla module path (with fallback support)"""
        # Use get_module_path() for automatic fallback logic
        vanilla_root = self.scanner.get_module_path("vanilla")
        if not vanilla_root:
            logger.warning("vanilla not found in any location")
            return

        # vanilla is usually in Lib/vanilla/ subdirectory
        possible_paths = [
            vanilla_root / "Lib" / "vanilla",
            vanilla_root / "vanilla",
            vanilla_root,
        ]

        for path in possible_paths:
            init_file = path / "__init__.py"
            if init_file.exists():
                self.vanilla_path = path
                return

        logger.warning(f"Vanilla __init__.py not found in {vanilla_root}")

    def _build_class_to_file_map(self) -> None:
        """Build class-to-file mapping table from __init__.py

        Parses import statements in vanilla's __init__.py,
        builds accurate class name to file name mapping.
        This correctly handles:
        - Plural filenames (Window -> vanillaWindows.py)
        - Multi-class files (vanillaWindows.py contains multiple classes)
        - Mismatched naming (ActionButton -> vanillaPopUpButton.py)
        """
        if not self.vanilla_path:
            return

        init_file = self.vanilla_path / "__init__.py"
        if not init_file.exists():
            logger.warning(
                "vanilla __init__.py not found, class-to-file mapping unavailable"
            )
            return

        try:
            content = init_file.read_text(encoding="utf-8")
            tree = ast.parse(content)

            # Parse "from vanilla.XXX import YYY" statements
            for node in tree.body:
                if isinstance(node, ast.ImportFrom):
                    # Check if it's a vanilla internal module
                    if node.module and node.module.startswith("vanilla."):
                        # 'vanilla.vanillaWindows' -> 'vanillaWindows'
                        file_name = node.module.split(".")[-1]

                        # Record all classes in this file
                        for alias in node.names:
                            class_name = alias.name
                            self._class_to_file_map[class_name] = file_name

            logger.debug(
                f"Built class-to-file map with {len(self._class_to_file_map)} classes from __init__.py"
            )

        except Exception as e:
            logger.warning(f"Failed to build class-to-file map: {e}")
            # Mapping failure doesn't affect functionality, will fallback to guessing mode

    def is_available(self) -> bool:
        """Check if vanilla is available

        Returns:
            True if vanilla is installed and accessible
        """
        return self.vanilla_path is not None and self.vanilla_path.exists()

    def list_vanilla_classes(self) -> list[str]:
        """List all Vanilla UI components

        Extracts all exported class names from __init__.py

        Returns:
            List of class names
        """
        # Use cache
        if self._classes_cache is not None:
            return self._classes_cache

        if not self.is_available():
            logger.warning("Vanilla not available")
            return []

        # Assert: is_available() already confirmed vanilla_path exists
        assert self.vanilla_path is not None

        classes = []
        init_file = self.vanilla_path / "__init__.py"

        try:
            content = init_file.read_text(encoding="utf-8")
            tree = ast.parse(content)

            # Extract __all__ list
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "__all__":
                            if isinstance(node.value, ast.List):
                                for elt in node.value.elts:
                                    if isinstance(elt, ast.Constant):
                                        classes.append(elt.value)

            # If no __all__, extract from import statements
            if not classes:
                for node in ast.walk(tree):
                    if isinstance(node, (ast.ImportFrom, ast.Import)):
                        if isinstance(node, ast.ImportFrom):
                            for alias in node.names:
                                classes.append(alias.name)

            # Cache results
            self._classes_cache = sorted(set(classes))
            logger.info(f"Found {len(self._classes_cache)} vanilla classes")

        except Exception as e:
            logger.error(f"Error parsing vanilla __init__.py: {e}")
            self._classes_cache = []

        return self._classes_cache

    def get_vanilla_class(self, class_name: str) -> dict[str, Any] | None:
        """Get complete information for specified class

        Args:
            class_name: Class name (e.g., "Button")

        Returns:
            Class info dictionary containing:
            - class_name: Class name
            - source: Complete source code
            - docstring: Class docstring
            - methods: Method list
            - file_path: File path

            Returns None if class doesn't exist
        """
        # Check cache
        if class_name in self._class_info_cache:
            return self._class_info_cache[class_name]

        if not self.is_available():
            return None

        # Find class file
        class_file = self._find_class_file(class_name)
        if not class_file:
            logger.warning(f"Class file not found for: {class_name}")
            return None

        try:
            # Read source code
            source = class_file.read_text(encoding="utf-8")

            # Parse AST
            tree = ast.parse(source)

            # Find class definition
            class_node = None
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    class_node = node
                    break

            if not class_node:
                logger.warning(f"Class definition not found: {class_name}")
                return None

            # Extract information
            class_info = {
                "class_name": class_name,
                "source": source,
                "docstring": ast.get_docstring(class_node) or "",
                "methods": self._extract_methods(class_node),
                "file_path": str(class_file),
            }

            # Cache results
            self._class_info_cache[class_name] = class_info

            return class_info

        except Exception as e:
            logger.error(f"Error parsing class {class_name}: {e}")
            return None

    def _find_class_file(self, class_name: str) -> Path | None:
        """Find the file corresponding to a class

        Uses precise mapping from __init__.py for 100% accuracy.

        Args:
            class_name: Class name

        Returns:
            File path, or None if not found
        """
        if not self.vanilla_path:
            return None

        # Only use precise mapping from __init__.py
        if class_name in self._class_to_file_map:
            file_name = self._class_to_file_map[class_name]
            file_path = self.vanilla_path / f"{file_name}.py"
            if file_path.exists():
                logger.debug(f"Found {class_name} in {file_path.name}")
                return file_path
            else:
                logger.warning(f"Mapping found but file missing: {file_path}")

        logger.warning(f"Class {class_name} not in __init__.py mapping")
        return None

    def _extract_methods(self, class_node: ast.ClassDef) -> list[dict[str, Any]]:
        """Extract method information from class node

        Args:
            class_node: AST class node

        Returns:
            Method info list
        """
        methods = []

        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                method_info = {
                    "name": node.name,
                    "docstring": ast.get_docstring(node) or "",
                    "parameters": self._extract_parameters(node),
                }
                methods.append(method_info)

        return methods

    def _extract_parameters(self, func_node: ast.FunctionDef) -> list[dict[str, Any]]:
        """Extract parameter information from function node

        Args:
            func_node: AST function node

        Returns:
            Parameter info list
        """
        parameters = []
        args = func_node.args

        # Extract regular parameters
        for i, arg in enumerate(args.args):
            param_info = {
                "name": arg.arg,
                "default": None,
            }

            # Check if has default value
            defaults_offset = len(args.args) - len(args.defaults)
            if i >= defaults_offset:
                default_index = i - defaults_offset
                default_node = args.defaults[default_index]
                param_info["default"] = ast.unparse(default_node)

            parameters.append(param_info)

        return parameters

    def search_vanilla_classes(
        self, query: str, max_results: int = 10
    ) -> list[dict[str, Any]]:
        """Search Vanilla UI components

        Searches class names and docstrings

        Args:
            query: Search query (case-insensitive)
            max_results: Maximum number of results

        Returns:
            Search result list, each result contains:
            - class_name: Class name
            - docstring: Docstring summary
            - score: Relevance score
        """
        if not self.is_available():
            return []

        query_lower = query.lower()
        results = []

        # Get all classes
        all_classes = self.list_vanilla_classes()

        for class_name in all_classes:
            score = 0.0

            # Exact name match
            if query_lower == class_name.lower():
                score = 1.0
            # Name contains query
            elif query_lower in class_name.lower():
                score = 0.8

            # Check docstring
            class_info = self.get_vanilla_class(class_name)
            if class_info and query_lower in class_info["docstring"].lower():
                score = max(score, 0.6)

            # Add to results
            if score > 0:
                results.append(
                    {
                        "class_name": class_name,
                        "docstring": (
                            class_info["docstring"][:200] if class_info else ""
                        ),
                        "score": score,
                    }
                )

        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)

        return results[:max_results]
