#!/usr/bin/env python3
"""
Python API Native Accessor - Minimalist three-layer segmented read architecture.

Reads Python API documentation directly from __init__.py without JSON intermediate layer.

Core strategy:
1. Index layer: Read __all__ list to extract symbol names (62 lines, < 10KB)
2. Locate layer: Use grep for fast symbol location (< 10ms)
3. Read layer: On-demand read + LRU cache (< 50ms first time, < 1ms cache hit)

Memory usage: < 4MB (vs full file ~1.5MB or JSON 322KB)
"""

import logging
import re
import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class PythonAPINativeAccessor:
    """Python API Native Accessor - Minimalist segmented read implementation."""

    # Class constants
    _MAX_CLASS_BLOCK_SEARCH_LINES = 5000  # Max lines to search for class block

    def __init__(self, init_file: Path):
        """Initialize Native Accessor.

        Args:
            init_file: Path to __init__.py file
        """
        self.init_file = init_file
        self.symbols: dict[str, list[str]] = {}

        # Build symbol index
        self._load_symbol_index()
        logger.info(
            f"Python API Native Accessor initialized: "
            f"{len(self.symbols['classes'])} classes, "
            f"{len(self.symbols['functions'])} functions, "
            f"{len(self.symbols['constants'])} constants"
        )

    # ========== Layer 1: Index Layer ==========

    def _load_symbol_index(self) -> None:
        """Read __all__ to extract symbol names (only 62 lines)."""
        try:
            with open(self.init_file, encoding="utf-8") as f:
                lines = f.readlines()
                all_section = "".join(lines[98:160])  # Lines 99-160 (0-based)

            # Extract symbols
            self.symbols = {
                "classes": re.findall(r'"(GS\w+)"', all_section),
                "functions": re.findall(r'"([a-z][a-zA-Z]+)"', all_section),
                "constants": re.findall(r'"([A-Z][A-Z_]+)"', all_section),
            }

            logger.debug(
                f"Symbol index loaded: {len(self.symbols['classes'])} classes, "
                f"{len(self.symbols['functions'])} functions, "
                f"{len(self.symbols['constants'])} constants"
            )

        except Exception as e:
            logger.error(f"Failed to load symbol index: {e}")
            self.symbols = {"classes": [], "functions": [], "constants": []}

    # ========== Layer 2: Locate Layer (grep search) ==========

    def _grep_line(self, pattern: str) -> list[int]:
        """Generic grep search, returns list of line numbers (safe version).

        Args:
            pattern: grep search pattern (fixed string, not regex)

        Returns:
            List of matching line numbers
        """
        # Input validation: prevent command injection
        if not pattern or len(pattern) > 200:
            logger.warning("Invalid grep pattern: pattern too long or empty")
            return []

        # Filter dangerous characters
        dangerous_chars = [";", "|", "&", "$", "`", "\n", "\r"]
        if any(char in pattern for char in dangerous_chars):
            logger.warning("Invalid grep pattern: contains dangerous characters")
            return []

        try:
            # Use -F fixed string mode (no regex parsing) for safety
            result = subprocess.run(
                ["grep", "-n", "-F", pattern, str(self.init_file)],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if not result.stdout:
                return []

            lines = []
            for line in result.stdout.strip().split("\n"):
                if ":" in line:
                    try:
                        lines.append(int(line.split(":")[0]))
                    except (ValueError, IndexError):
                        # Ignore lines that cannot be parsed
                        continue

            return lines

        except Exception as e:
            logger.warning(f"grep failed for pattern '{pattern}': {e}")
            return []

    def _find_class_block(self, class_name: str) -> int | None:
        """Find the starting line of a class documentation block.

        Supports two definition patterns:
        - def ____ClassName____: most classes
        - class ____ClassName____: special cases like GSAnchor
        """
        # Try def ____ pattern first (most classes)
        lines = self._grep_line(f"def ____{class_name}____")
        if lines:
            return lines[0]

        # Try class ____ pattern (special cases like GSAnchor)
        lines = self._grep_line(f"class ____{class_name}____")
        return lines[0] if lines else None

    def _find_class_block_range(self, class_name: str) -> tuple[int, int] | None:
        """Find the line number range of a class documentation block.

        Args:
            class_name: Class name

        Returns:
            (start_line, end_line) or None
        """
        start_line = self._find_class_block(class_name)
        if not start_line:
            return None

        # Search for next class definition as end boundary
        # Use incremental search to find next def ____ or class ____
        try:
            with open(self.init_file, encoding="utf-8") as f:
                # Skip to start line
                for _ in range(start_line):
                    f.readline()

                # Search for next class definition
                for i in range(self._MAX_CLASS_BLOCK_SEARCH_LINES):
                    line = f.readline()
                    if not line:  # EOF
                        return (start_line, start_line + i)

                    # Check if this is the next class definition
                    if "def ____" in line or "class ____" in line:
                        return (start_line, start_line + i)

                # No next class found, return to end of file
                return (start_line, start_line + self._MAX_CLASS_BLOCK_SEARCH_LINES)

        except Exception as e:
            logger.warning(f"Failed to find class block range: {e}")
            return None

    def _find_property_assignment(self, class_name: str, prop_name: str) -> int | None:
        """Find property assignment line."""
        lines = self._grep_line(f"{class_name}.{prop_name} =")
        return lines[0] if lines else None

    def _find_property_doc(self, prop_name: str) -> list[int]:
        """Find property documentation lines (may have multiple properties with same name)."""
        return self._grep_line(f".. attribute:: {prop_name}")

    def _find_method_doc(self, method_name: str) -> list[int]:
        """Find method documentation lines."""
        return self._grep_line(f".. function:: {method_name}")

    def _find_function_def(self, func_name: str) -> int | None:
        """Find function definition line."""
        lines = self._grep_line(f"def {func_name}")
        return lines[0] if lines else None

    def _find_constant_assignment(self, const_name: str) -> int | None:
        """Find constant assignment line."""
        lines = self._grep_line(f"^{const_name} =")
        return lines[0] if lines else None

    def _find_constant_doc(self, const_name: str) -> int | None:
        """Find constant documentation line."""
        lines = self._grep_line(f".. data:: {const_name}")
        return lines[0] if lines else None

    # ========== Layer 3: On-demand Read + Simple Parse ==========

    @lru_cache(maxsize=20)
    def get_class(self, class_name: str) -> dict:
        """Read class overview (using goal-oriented search, optimized I/O).

        Args:
            class_name: Class name (e.g., GSFont)

        Returns:
            Class info dictionary containing name, description, properties, methods
        """
        start_line = self._find_class_block(class_name)
        if not start_line:
            logger.warning(f"Class block not found: {class_name}")
            return {"name": class_name, "error": "Not found"}

        # Step 1: Read first docstring (for description extraction)
        first_doc = self._read_first_docstring(start_line)
        if not first_doc:
            logger.warning(f"No docstring found for class: {class_name}")
            return {"name": class_name, "error": "No docstring"}

        # Extract description (first paragraph)
        desc_match = re.search(
            r"={3,}.*?\n+(.*?)(?=Properties|Functions|\Z)", first_doc, re.DOTALL
        )
        description = desc_match.group(1).strip() if desc_match else ""
        description = self._clean_rst_markup(description)

        # Step 2: Goal-oriented search for all autosummary blocks (incremental + early termination)
        autosummary_lines = self._find_autosummary_blocks(start_line, max_search=200)

        properties: list[str] = []
        methods: list[str] = []

        # Step 3: Read and categorize each autosummary block
        for autosummary_line in autosummary_lines:
            # Read preceding lines to determine block type (Properties or Functions)
            context = self._read_lines(max(1, autosummary_line - 5), autosummary_line)

            # Read autosummary content
            members = self._read_autosummary_block(autosummary_line)

            # Categorize members based on context
            if "Properties" in context or ("Functions" not in context and not methods):
                # Properties block or first block (assume Properties)
                properties.extend(members)
            elif "Functions" in context:
                # Functions block
                methods.extend(members)

        # Deduplicate (some classes may have duplicate autosummary)
        properties = list(dict.fromkeys(properties))
        methods = list(dict.fromkeys(methods))

        logger.debug(
            f"Loaded class {class_name}: {len(properties)} properties, {len(methods)} methods "
            f"(found {len(autosummary_lines)} autosummary blocks)"
        )

        return {
            "name": class_name,
            "description": description,
            "properties": properties,
            "methods": methods,
        }

    @lru_cache(maxsize=100)
    def get_property(self, class_name: str, prop_name: str) -> dict:
        """Read class property details.

        Args:
            class_name: Class name
            prop_name: Property name

        Returns:
            Property details dictionary
        """
        result: dict[str, Any] = {
            "class": class_name,
            "name": prop_name,
            "assignment": None,
            "type": None,
            "description": "",
            "examples": [],
        }

        # 0. First find class block range, used to filter correct property documentation
        class_range = self._find_class_block_range(class_name)

        # 1. Read assignment definition
        assignment_line = self._find_property_assignment(class_name, prop_name)
        if assignment_line:
            assignment_content = self._read_lines(assignment_line, assignment_line + 5)
            result["assignment"] = assignment_content.strip()

        # 2. Read documentation
        doc_lines = self._find_property_doc(prop_name)
        if doc_lines:
            # Filter matches within class range
            doc_start = None
            if class_range:
                for line_num in doc_lines:
                    if class_range[0] <= line_num <= class_range[1]:
                        doc_start = line_num
                        break

            # If not found within class range, fallback to first match
            if doc_start is None:
                doc_start = doc_lines[0]
            # Dynamic detection, until encountering closing ''' marker
            doc_content = self._read_until_marker(
                doc_start, marker="'''", max_lines=100
            )

            # Extract description and type
            attr_match = re.search(
                r"\.\. attribute:: \w+\s+(.*?)(?=:type:|.. code-block::|\.\. attribute::|\Z)",
                doc_content,
                re.DOTALL,
            )
            if attr_match:
                result["description"] = self._clean_rst_markup(
                    attr_match.group(1).strip()
                )

            # Extract type
            type_match = re.search(r":type:\s*(.+)", doc_content)
            if type_match:
                result["type"] = type_match.group(1).strip()

            # Extract example code
            example_match = re.search(
                r".. code-block:: python\s+(.*?)(?=\.\. |\Z)", doc_content, re.DOTALL
            )
            if example_match:
                result["examples"] = [example_match.group(1).strip()]

        logger.debug(f"Loaded property {class_name}.{prop_name}")
        return result

    @lru_cache(maxsize=100)
    def get_method(self, class_name: str, method_name: str) -> dict:
        """Read class method details.

        Args:
            class_name: Class name
            method_name: Method name

        Returns:
            Method details dictionary
        """
        result = {
            "class": class_name,
            "name": method_name,
            "signature": "",
            "parameters": [],
            "return_type": None,
            "description": "",
            "examples": [],
        }

        # Search method documentation
        doc_lines = self._find_method_doc(method_name)
        if not doc_lines:
            logger.warning(
                f"Method documentation not found: {class_name}.{method_name}"
            )
            return result

        # Read first matching documentation (dynamic detection, until closing ''' marker)
        doc_start = doc_lines[0]
        doc_content = self._read_until_marker(doc_start, marker="'''", max_lines=100)

        # Extract method signature
        sig_match = re.search(r"\.\. function:: (\w+)\((.*?)\)", doc_content)
        if sig_match:
            result["signature"] = f"{sig_match.group(1)}({sig_match.group(2)})"
            result["parameters"] = [
                p.strip() for p in sig_match.group(2).split(",") if p.strip()
            ]

        # Extract description
        desc_match = re.search(
            r"\.\. function:: .*?\n\s+(.*?)(?=:param|:type|:returns?|\.\. code-block::|\Z)",
            doc_content,
            re.DOTALL,
        )
        if desc_match:
            result["description"] = self._clean_rst_markup(desc_match.group(1).strip())

        # Extract return type
        return_match = re.search(r":returns?:\s*(.+)", doc_content)
        if return_match:
            result["return_type"] = return_match.group(1).strip()

        # Extract examples
        example_match = re.search(
            r".. code-block:: python\s+(.*?)(?=\.\. |\Z)", doc_content, re.DOTALL
        )
        if example_match:
            result["examples"] = [example_match.group(1).strip()]

        logger.debug(f"Loaded method {class_name}.{method_name}")
        return result

    @lru_cache(maxsize=20)
    def get_function(self, func_name: str) -> dict:
        """Read global function details.

        Args:
            func_name: Function name

        Returns:
            Function details dictionary
        """
        line_num = self._find_function_def(func_name)
        if not line_num:
            logger.warning(f"Function definition not found: {func_name}")
            return {"name": func_name, "error": "Not found"}

        content = self._read_lines(line_num, line_num + 30)

        # Extract signature
        sig_match = re.search(r"def\s+\w+\((.*?)\):", content)
        signature = sig_match.group(1) if sig_match else ""

        # Extract docstring
        doc_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
        description = (
            self._clean_rst_markup(doc_match.group(1).strip()) if doc_match else ""
        )

        logger.debug(f"Loaded function {func_name}")

        return {"name": func_name, "signature": signature, "description": description}

    @lru_cache(maxsize=50)
    def get_constant(self, const_name: str) -> dict:
        """Read constant details.

        Args:
            const_name: Constant name

        Returns:
            Constant details dictionary
        """
        result = {"name": const_name, "value": None, "description": ""}

        # Read assignment
        assignment_line = self._find_constant_assignment(const_name)
        if assignment_line:
            line_content = self._read_lines(assignment_line, assignment_line + 1)
            value_match = re.search(r"=\s*(.+)", line_content)
            result["value"] = value_match.group(1).strip() if value_match else ""

        # Read documentation (using indent-aware reading, until same-indent next block)
        doc_line = self._find_constant_doc(const_name)
        if doc_line:
            # Dynamic detection, read from .. data:: until next same-indent block
            doc_content = self._read_until_same_indent(
                doc_line, base_indent=None, max_lines=50
            )

            # Extract description (first paragraph after .. data::)
            lines = doc_content.split("\n")[1:]  # Skip .. data:: line
            description = []
            started = False  # Flag for whether description collection has started

            for line in lines:
                stripped = line.strip()

                # Skip leading empty lines
                if not stripped and not started:
                    continue

                # If empty line encountered after starting, stop
                if not stripped and started:
                    break

                # If new RST marker encountered, stop
                if stripped.startswith("..") or stripped.startswith(":"):
                    break

                # Collect description
                description.append(stripped)
                started = True

            result["description"] = self._clean_rst_markup(" ".join(description))

        logger.debug(f"Loaded constant {const_name}")
        return result

    # ========== Helper Methods ==========

    def _read_lines(self, start: int, end: int) -> str:
        """Read specified line range.

        Args:
            start: Start line number (1-based)
            end: End line number (exclusive)

        Returns:
            Read content
        """
        try:
            with open(self.init_file, encoding="utf-8") as f:
                # Skip to start line
                for _ in range(start - 1):
                    f.readline()

                # Read target lines
                lines = [f.readline() for _ in range(end - start)]

            return "".join(lines)

        except Exception as e:
            logger.error(f"Failed to read lines {start}-{end}: {e}")
            return ""

    def _find_next_marker(
        self, start_line: int, marker: str = "'''", max_search: int = 20
    ) -> int | None:
        """Find the first marker line starting from a given line.

        Args:
            start_line: Start line number (1-based)
            marker: Marker to find
            max_search: Maximum lines to search

        Returns:
            Line number of found marker (1-based), None if not found
        """
        try:
            with open(self.init_file, encoding="utf-8") as f:
                # Skip to start line
                for _ in range(start_line - 1):
                    f.readline()

                for i in range(max_search):
                    line = f.readline()
                    if not line:  # EOF
                        return None

                    # Check if it's a marker (single line, may have leading whitespace)
                    if line.strip() == marker:
                        return start_line + i

                return None

        except Exception as e:
            logger.error(f"Failed to find next marker: {e}")
            return None

    def _read_until_marker(
        self, start_line: int, marker: str = "'''", max_lines: int = 5000
    ) -> str:
        """Read from start line until encountering the second marker (single line).

        Used for reading comment blocks enclosed by '''.
        Reads from first ''' until encountering second '''.

        Args:
            start_line: Start line number (should be first marker line, 1-based)
            marker: End marker (default ''')
            max_lines: Maximum lines to read (safety limit)

        Returns:
            Read content (including start and end markers)
        """
        try:
            with open(self.init_file, encoding="utf-8") as f:
                # Skip to start line
                for _ in range(start_line - 1):
                    f.readline()

                lines = []
                found_first_marker = False

                for _ in range(max_lines):
                    line = f.readline()
                    if not line:  # EOF
                        break

                    lines.append(line)

                    # Check if it's a marker (single line, may have leading whitespace)
                    if line.strip() == marker:
                        if not found_first_marker:
                            # First marker found, mark as found, continue reading
                            found_first_marker = True
                        else:
                            # Second marker found, stop reading
                            break

                return "".join(lines)

        except Exception as e:
            logger.error(f"Failed to read until marker: {e}")
            return ""

    def _read_until_same_indent(
        self, start_line: int, base_indent: int | None = None, max_lines: int = 1000
    ) -> str:
        """Read from start line until encountering next block with same indentation.

        Used for reading constant comment blocks (starting from `.. data::`)

        Args:
            start_line: Start line number (1-based)
            base_indent: Base indentation level (None for auto-detection)
            max_lines: Maximum lines to read (safety limit)

        Returns:
            Read content
        """
        try:
            with open(self.init_file, encoding="utf-8") as f:
                # Skip to start line
                for _ in range(start_line - 1):
                    f.readline()

                lines = []
                first_line = True

                for _ in range(max_lines):
                    line = f.readline()
                    if not line:  # EOF
                        break

                    # First line, determine base indentation
                    if first_line:
                        if base_indent is None:
                            # Auto-detect: calculate position of first non-whitespace character
                            stripped = line.lstrip()
                            if stripped:
                                base_indent = len(line) - len(stripped)
                            else:
                                base_indent = 0
                        lines.append(line)
                        first_line = False
                        continue

                    # Empty line: continue reading
                    if not line.strip():
                        lines.append(line)
                        continue

                    # Calculate current line indentation
                    stripped = line.lstrip()
                    current_indent = len(line) - len(stripped)

                    # If same or smaller indentation encountered, and line has content
                    if (
                        base_indent is not None
                        and current_indent <= base_indent
                        and stripped
                    ):
                        # Check if it's next `.. data::` block
                        if stripped.startswith(".. data::"):
                            break
                        # Or other same-level block marker
                        if current_indent == base_indent:
                            break

                    lines.append(line)

                return "".join(lines)

        except Exception as e:
            logger.error(f"Failed to read until same indent: {e}")
            return ""

    def _find_autosummary_blocks(
        self, start_line: int, max_search: int = 200
    ) -> list[int]:
        """Search for all autosummary markers starting from a line (incremental + early termination).

        Args:
            start_line: Start line number (1-based)
            max_search: Maximum lines to search (default 200)

        Returns:
            List of all found autosummary marker line numbers
        """
        autosummary_lines = []
        chunk_size = 50  # Read 50 lines at a time

        try:
            for offset in range(0, max_search, chunk_size):
                chunk = self._read_lines(
                    start_line + offset, start_line + offset + chunk_size
                )

                # Find all autosummary markers
                for i, line in enumerate(chunk.split("\n")):
                    if ".. autosummary::" in line:
                        autosummary_lines.append(start_line + offset + i)

                # Early termination: encountered next class definition
                if "def ____" in chunk and offset > 0:
                    logger.debug(
                        "Found next class definition, stopping autosummary search"
                    )
                    break

        except Exception as e:
            logger.warning(f"Failed to find autosummary blocks: {e}")

        logger.debug(f"Found {len(autosummary_lines)} autosummary blocks")
        return autosummary_lines

    def _read_autosummary_block(
        self, autosummary_line: int, max_lines: int = 100
    ) -> list[str]:
        """Read autosummary block content (only member list).

        Starting from `.. autosummary::` line, read indented content until other block marker.

        Args:
            autosummary_line: autosummary marker line number (1-based)
            max_lines: Maximum lines to read (default 100, enough for most autosummary blocks)

        Returns:
            List of member names
        """
        try:
            content = self._read_lines(autosummary_line, autosummary_line + max_lines)
            lines = content.split("\n")[1:]  # Skip autosummary marker line

            members = []
            found_content = False  # Flag for whether content has been found

            for line in lines:
                stripped = line.strip()

                # Skip leading empty lines
                if not stripped and not found_content:
                    continue

                # If other RST marker or ** starting paragraph encountered, stop
                if stripped.startswith("..") or stripped.startswith("**"):
                    break

                # If empty line and content found, may be block end (but continue to avoid missing)
                if not stripped and found_content:
                    # Check if really ended (no more indented content after)
                    continue

                # Extract member name
                if stripped:
                    member = stripped.replace("()", "")  # Remove method parentheses
                    # Filter out section headers (Properties, Functions, etc.)
                    if member and member not in ["Properties", "Functions"]:
                        members.append(member)
                        found_content = True

            return members

        except Exception as e:
            logger.warning(f"Failed to read autosummary block: {e}")
            return []

    def _read_first_docstring(self, start_line: int, max_lines: int = 200) -> str:
        """Read first docstring (for class description extraction).

        Starting from def ____ line, find first ''' marker, then read until end marker.

        Args:
            start_line: Start line number (1-based, def ____ClassName____ line)
            max_lines: Maximum lines to read (default 200, enough for complete docstring)

        Returns:
            First docstring content
        """
        try:
            # Find first ''' marker position
            first_marker = self._find_next_marker(
                start_line, marker="'''", max_search=10
            )
            if not first_marker:
                return ""

            # Read from first marker to second marker (complete docstring)
            content = self._read_until_marker(
                first_marker, marker="'''", max_lines=max_lines
            )

            # Extract content (remove markers)
            doc_match = re.search(r"'''(.*?)'''", content, re.DOTALL)
            if doc_match:
                return doc_match.group(1)
            return ""
        except Exception as e:
            logger.warning(f"Failed to read first docstring: {e}")
            return ""

    def _clean_rst_markup(self, text: str) -> str:
        """Clean RST inline markup.

        Args:
            text: Text containing RST markup

        Returns:
            Cleaned text
        """
        # Replace :class:`NAME` with NAME
        text = re.sub(r":class:`([^`]+)`", r"\1", text)
        # Replace :meth:`NAME` with NAME
        text = re.sub(r":meth:`([^`]+)`", r"\1", text)
        # Replace :const:`NAME` with NAME
        text = re.sub(r":const:`([^`]+)`", r"\1", text)
        # Replace other similar RST inline directives
        text = re.sub(r":[a-z]+:`([^`]+)`", r"\1", text)

        return text

    # ========== Search Functionality ==========

    def search(self, query: str, symbol_type: str = "all") -> list:
        """Search function - returns index info only (lightweight).

        Searches symbol index (classes, functions, constants).
        For class member search, use PythonAPIManager.search(),
        which implements layered search strategy.

        Args:
            query: Search keyword
            symbol_type: 'all' | 'classes' | 'functions' | 'constants'

        Returns:
            Search result list (only name, type, score, no details)
        """
        results = []
        query_lower = query.lower()

        # 1. Search classes
        if symbol_type in ["all", "classes"]:
            for name in self.symbols["classes"]:
                # Class name matching
                if query_lower in name.lower():
                    results.append(
                        {
                            "type": "class",
                            "name": name,
                            "score": 1.0 if query_lower == name.lower() else 0.7,
                        }
                    )

        # 2. Search global functions
        if symbol_type in ["all", "functions"]:
            for name in self.symbols["functions"]:
                if query_lower in name.lower():
                    results.append(
                        {
                            "type": "function",
                            "name": name,
                            "score": 1.0 if query_lower == name.lower() else 0.7,
                        }
                    )

        # 3. Search constants
        if symbol_type in ["all", "constants"]:
            for name in self.symbols["constants"]:
                if query_lower in name.lower():
                    results.append(
                        {
                            "type": "constant",
                            "name": name,
                            "score": 1.0 if query_lower == name.lower() else 0.7,
                        }
                    )

        # Sort (by score descending)
        results.sort(key=lambda x: x["score"], reverse=True)  # type: ignore[arg-type, return-value]

        logger.debug(f"Search '{query}' found {len(results)} results")
        return results

    def get_detail(
        self, name: str, symbol_type: str | None = None, class_name: str | None = None
    ) -> dict:
        """Get detailed information.

        Args:
            name: Symbol name
            symbol_type: 'class' | 'property' | 'method' | 'function' | 'constant'
            class_name: Class name (required when symbol_type is property/method)

        Returns:
            Detailed information dictionary
        """
        if symbol_type == "class" or (
            not symbol_type and name in self.symbols["classes"]
        ):
            return self.get_class(name)

        elif symbol_type == "property" and class_name:
            return self.get_property(class_name, name)

        elif symbol_type == "method" and class_name:
            return self.get_method(class_name, name)

        elif symbol_type == "function" or (
            not symbol_type and name in self.symbols["functions"]
        ):
            return self.get_function(name)

        elif symbol_type == "constant" or (
            not symbol_type and name in self.symbols["constants"]
        ):
            return self.get_constant(name)

        else:
            logger.warning(f"Unknown symbol type or not found: {name}")
            return {"name": name, "error": "Unknown symbol type or not found"}
