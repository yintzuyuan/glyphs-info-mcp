"""
TOC Parser - Parse Handbook table of contents from single-page version

Issue #17: Add TOC structure parser for hierarchical chapter navigation

This module parses the Handbook's single-page version to extract the complete
table of contents with hierarchical relationships. The single-page content is
discarded after parsing; only the TOC structure is retained.

Key insight: Single-page headings match paginated file first lines because
the single-page version is a concatenation of all individual pages.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class TocEntry:
    """Table of contents entry with hierarchical support

    Attributes:
        title: Chapter title (without markdown # prefix)
        level: Heading level (2=##, 3=###, 4=####)
        file: Corresponding cache filename, or None if not found
        children: List of child entries (sub-chapters)
    """

    title: str
    level: int
    file: str | None
    children: list[TocEntry] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "title": self.title,
            "level": self.level,
            "file": self.file,
            "children": [child.to_dict() for child in self.children],
        }


def parse_headings(content: str) -> list[tuple[str, int]]:
    """Parse Markdown headings from content

    Args:
        content: Markdown content string

    Returns:
        List of (raw_heading_line, level) tuples

    Note:
        - Only parses ## (level 2) and deeper headings
        - # (level 1) is skipped as it's typically the document title
    """
    if not content.strip():
        return []

    headings: list[tuple[str, int]] = []

    for line in content.split("\n"):
        # Must start with ## (skip # document title)
        if line.startswith("##"):
            # Count the number of # characters
            level = len(line) - len(line.lstrip("#"))
            headings.append((line, level))

    return headings


def build_title_file_mapping(cache_dir: Path) -> dict[str, str]:
    """Build mapping from first-line titles to filenames

    Args:
        cache_dir: Path to cache directory containing .md files

    Returns:
        Dictionary mapping first-line title to filename

    Note:
        The first line of each paginated file matches its heading
        in the single-page version, allowing title-based matching.
    """
    mapping: dict[str, str] = {}

    for md_file in cache_dir.glob("*.md"):
        try:
            first_line = md_file.read_text(encoding="utf-8").split("\n")[0]
            mapping[first_line] = md_file.name
        except Exception as e:
            logger.warning(f"Failed to read {md_file}: {e}")

    return mapping


def build_toc_tree(
    headings: list[tuple[str, int]],
    mapping: dict[str, str],
    include_all: bool = False,
) -> list[TocEntry]:
    """Build hierarchical TOC tree from headings

    Args:
        headings: List of (raw_heading_line, level) tuples
        mapping: Dictionary mapping title to filename
        include_all: If True, include all entries; if False (default),
                     only include entries with corresponding files

    Returns:
        List of top-level TocEntry objects with nested children

    Algorithm:
        Uses a stack to track parent entries at each level.
        When a heading is encountered:
        - If same or higher level than stack top: pop until finding parent
        - Add entry as child of stack top (or root if stack empty)
        - Push entry onto stack for potential future children

    Note:
        When include_all=False, entries without files are skipped.
        This reduces TOC from ~460 to ~124 entries, saving context tokens.
        Sub-section content is still accessible via the parent file.
    """
    if not headings:
        return []

    root: list[TocEntry] = []
    # Stack of (level, entry) for tracking parent hierarchy
    stack: list[tuple[int, TocEntry]] = []

    for raw_line, level in headings:
        # Extract title from raw line (remove # prefix)
        title = raw_line.lstrip("#").strip()

        # Look up file from mapping
        file = mapping.get(raw_line)

        # Skip entries without files unless include_all is True
        if not include_all and file is None:
            continue

        entry = TocEntry(title=title, level=level, file=file, children=[])

        # Pop stack until we find the parent level
        while stack and stack[-1][0] >= level:
            stack.pop()

        if stack:
            # Add as child of the last entry on stack
            stack[-1][1].children.append(entry)
        else:
            # No parent, add to root
            root.append(entry)

        # Push this entry onto stack
        stack.append((level, entry))

    return root
