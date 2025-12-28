#!/usr/bin/env python3
"""
Mekkablue Scripts Accessor - Local accessor for mekkablue script collection

Uses simple text parsing to extract metadata from mekkablue script collection,
providing script search, category browsing, and full source code reading.

Design references VanillaLocalAccessor, fully localized, no network dependency.
"""

import logging
import re
from pathlib import Path
from typing import Any

from glyphs_info_mcp.shared.core.repository_scanner import RepositoryScanner

logger = logging.getLogger(__name__)


class MekkablueScriptsAccessor:
    """Mekkablue Script Collection Local Accessor - Fully relies on local source code"""

    def __init__(self, repository_scanner: RepositoryScanner):
        """Initialize Mekkablue Scripts Accessor

        Args:
            repository_scanner: Repository Scanner instance
        """
        self.scanner = repository_scanner
        self.mekkablue_path: Path | None = None
        self._categories_cache: list[str] | None = None
        self._scripts_index: dict[str, list[dict]] = (
            {}
        )  # category → script metadata list
        self._script_cache: dict[str, dict] = {}  # script_id → full script info

        # Try to find mekkablue module path
        self._locate_mekkablue()

        # Build category index
        if self.is_available():
            self._build_category_index()

    def _locate_mekkablue(self) -> None:
        """Locate mekkablue script collection path (with fallback support)"""
        # Use get_module_path() to automatically handle fallback logic
        mekkablue_root = self.scanner.get_module_path("mekkablue")
        if not mekkablue_root:
            logger.warning("mekkablue not found in any location")
            return

        # mekkablue scripts are directly in root directory
        if mekkablue_root.exists() and mekkablue_root.is_dir():
            self.mekkablue_path = mekkablue_root
        else:
            logger.warning(f"mekkablue path not accessible: {mekkablue_root}")

    def is_available(self) -> bool:
        """Check if mekkablue script collection is available

        Returns:
            True if mekkablue is installed and accessible
        """
        return self.mekkablue_path is not None and self.mekkablue_path.exists()

    def _build_category_index(self) -> None:
        """Scan and build category index

        Iterates through all subdirectories (categories) under mekkablue directory,
        extracting script metadata for each category.
        """
        if not self.mekkablue_path:
            return

        try:
            for item in self.mekkablue_path.iterdir():
                # Only process directories, exclude hidden and special directories
                if not item.is_dir():
                    continue
                if item.name.startswith(".") or item.name.startswith("__"):
                    continue

                category_name = item.name
                scripts = []

                # Scan all .py files in category directory
                for script_file in item.glob("*.py"):
                    metadata = self._extract_script_metadata(script_file, category_name)
                    if metadata:
                        scripts.append(metadata)

                if scripts:
                    self._scripts_index[category_name] = scripts

            logger.info(
                f"Built category index with {len(self._scripts_index)} categories"
            )
            logger.debug(f"Categories: {list(self._scripts_index.keys())}")

        except Exception as e:
            logger.error(f"Error building category index: {e}")
            self._scripts_index = {}

    def _extract_script_metadata(
        self, script_file: Path, category: str
    ) -> dict[str, Any] | None:
        """Extract script metadata (MenuTitle, __doc__)

        Uses simple text parsing and regex to extract metadata,
        avoiding the overhead of full AST parsing.

        Args:
            script_file: Script file path
            category: Script category

        Returns:
            Script metadata dictionary, or None if parsing fails
        """
        try:
            content = script_file.read_text(encoding="utf-8")

            # Extract MenuTitle
            menu_title = self._parse_menu_title(content)
            if not menu_title:
                # Fallback: use filename (without .py)
                menu_title = script_file.stem

            # Extract __doc__
            description = self._parse_docstring(content)

            # Build script_id: category/filename (without .py)
            script_id = f"{category}/{script_file.stem}"

            return {
                "script_id": script_id,
                "menu_title": menu_title,
                "filename": script_file.name,
                "category": category,
                "description": description,
                "file_path": str(script_file),
            }

        except Exception as e:
            logger.warning(f"Failed to extract metadata from {script_file.name}: {e}")
            return None

    def _parse_menu_title(self, content: str) -> str:
        """Parse MenuTitle comment

        Extracts "# MenuTitle: xxx" format title from script header.

        Args:
            content: Script file content

        Returns:
            MenuTitle string, or empty string if not found
        """
        # Regex match: # MenuTitle: xxx
        pattern = r"#\s*MenuTitle:\s*(.+)"
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    def _parse_docstring(self, content: str) -> str:
        """Parse docstring

        Extracts __doc__ = triple-quoted string or standalone triple-quoted docstring.

        Args:
            content: Script file content

        Returns:
            Docstring content, or empty string if not found
        """
        # Method 1: __doc__ = """...""" or __doc__ = '''...'''
        pattern1 = r'__doc__\s*=\s*["\']'  # noqa: F541
        pattern1 += r'{3}(.*?)["\']'  # noqa: F541
        pattern1 += r"{3}"
        match = re.search(pattern1, content, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Method 2: Standalone """...""" or '''...''' (usually at file start)
        # Limit search to first 20 lines
        lines = content.split("\n")[:20]
        first_lines = "\n".join(lines)

        pattern2 = r'^["\']'  # noqa: F541
        pattern2 += r'{3}(.*?)["\']'  # noqa: F541
        pattern2 += r"{3}"
        match = re.search(pattern2, first_lines, re.DOTALL | re.MULTILINE)
        if match:
            return match.group(1).strip()

        return ""

    def list_categories(self) -> list[str]:
        """List all script categories

        Returns:
            List of category names (sorted)
        """
        if not self.is_available():
            return []

        return sorted(self._scripts_index.keys())

    def get_category_scripts(self, category: str) -> list[dict]:
        """Get all script metadata for a category

        Args:
            category: Category name

        Returns:
            List of script metadata
        """
        if not self.is_available():
            return []

        return self._scripts_index.get(category, [])

    def get_script(self, script_id: str) -> dict[str, Any] | None:
        """Get complete script info (including source code)

        Args:
            script_id: Script ID (format: category/filename)

        Returns:
            Complete script info dictionary, including source code
            Returns None if script doesn't exist
        """
        if not self.is_available():
            return None

        # Check cache
        if script_id in self._script_cache:
            return self._script_cache[script_id]

        # Parse script_id
        try:
            category, filename_stem = script_id.split("/", 1)
        except ValueError:
            logger.warning(f"Invalid script_id format: {script_id}")
            return None

        # Find script metadata from index
        scripts = self._scripts_index.get(category, [])
        script_metadata = None
        for script in scripts:
            if script["script_id"] == script_id:
                script_metadata = script.copy()
                break

        if not script_metadata:
            logger.warning(f"Script not found in index: {script_id}")
            return None

        # Read complete source code
        try:
            script_path = Path(script_metadata["file_path"])
            source = script_path.read_text(encoding="utf-8")
            script_metadata["source"] = source

            # Cache result (limit to 50 max)
            if len(self._script_cache) >= 50:
                # Remove oldest one
                self._script_cache.pop(next(iter(self._script_cache)))
            self._script_cache[script_id] = script_metadata

            return script_metadata

        except Exception as e:
            logger.error(f"Error reading script source: {e}")
            return None

    def _calculate_relevance(self, script: dict, query: str) -> float:
        """Calculate relevance score between script and query - supports multi-keyword search (OR logic)

        Args:
            script: Script metadata dictionary
            query: Search query

        Returns:
            Relevance score (0.0 means not relevant, higher score = more relevant)
        """
        query_lower = query.lower()
        menu_title = script.get("menu_title", "").lower()
        description = script.get("description", "").lower()
        category = script.get("category", "").lower()

        # === 1. Full query match (priority, maintain backward compatibility) ===
        if query_lower == menu_title:
            return 10.0
        if query_lower in menu_title:
            return 5.0
        if query_lower in description:
            return 3.0
        if query_lower in category:
            return 1.0

        # === 2. Tokenized matching (supports multi-keyword) ===
        query_words = query_lower.split()
        if len(query_words) <= 1:
            return 0.0  # Single word already handled above

        # Calculate score for each word
        word_matches = 0
        total_word_score = 0.0

        for word in query_words:
            if len(word) < 2:  # Filter single characters
                continue

            # Word scoring
            word_score = 0.0
            if word in menu_title:
                word_score = 2.0
            elif word in description:
                word_score = 1.0
            elif word in category:
                word_score = 0.5

            if word_score > 0:
                word_matches += 1
                total_word_score += word_score

        # No matches
        if word_matches == 0:
            return 0.0

        # === 3. Multi-word match bonus ===
        valid_words = [w for w in query_words if len(w) >= 2]
        match_ratio = word_matches / len(valid_words) if valid_words else 0
        bonus = 1.0 * match_ratio  # Higher match ratio = higher bonus

        return total_word_score + bonus

    def search_scripts(
        self, query: str, category: str | None = None, max_results: int = 10
    ) -> list[dict[str, Any]]:
        """Search scripts

        Searches script MenuTitle and description, supports category filtering and multi-keyword search.

        Args:
            query: Search query (case-insensitive, supports space-separated keywords)
            category: Limit search to category, optional
            max_results: Maximum number of results

        Returns:
            Search result list, each result contains:
            - script_id, menu_title, category, description
            - score: Relevance score

        Examples:
            search_scripts("anchor")  # Single keyword
            search_scripts("anchor center")  # Multi-keyword (OR logic)
            search_scripts("錨點 居中")  # Chinese multi-keyword
        """
        if not self.is_available():
            return []

        results = []

        # Determine search scope
        if category:
            categories_to_search = [category] if category in self._scripts_index else []
        else:
            categories_to_search = list(self._scripts_index.keys())

        # Search all scripts
        for cat in categories_to_search:
            scripts = self._scripts_index.get(cat, [])
            for script in scripts:
                # Use new relevance calculation method
                score = self._calculate_relevance(script, query)

                if score > 0:
                    result = script.copy()
                    result["score"] = score
                    results.append(result)

        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)

        return results[:max_results]
