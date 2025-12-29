"""
Shared utilities for Glyphs Handbook module
"""

import re


def extract_title(content: str) -> str:
    """Extract document title from markdown content

    Prioritizes level-1 heading (#), falls back to ##, ###, then ####.
    Supports Markdown link syntax: ## [Title](#anchor) → Title

    Args:
        content: Markdown content string

    Returns:
        Extracted title or "Unnamed chapter" if no heading found
    """
    h2_title = None
    h3_title = None
    h4_title = None

    def _parse_title(line_text: str, prefix: str) -> str:
        """Extract and clean title from line"""
        title = line_text[len(prefix) :].strip()
        return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", title)

    for line in content.split("\n"):
        stripped = line.strip()

        # Prioritize level-1 heading, return immediately if found
        if stripped.startswith("# ") and not stripped.startswith("## "):
            return _parse_title(stripped, "# ")

        # Record first level-2 heading as fallback
        if (
            h2_title is None
            and stripped.startswith("## ")
            and not stripped.startswith("### ")
        ):
            h2_title = _parse_title(stripped, "## ")

        # Record first level-3 heading as secondary fallback
        if (
            h3_title is None
            and stripped.startswith("### ")
            and not stripped.startswith("#### ")
        ):
            h3_title = _parse_title(stripped, "### ")

        # Record first level-4 heading as tertiary fallback
        if (
            h4_title is None
            and stripped.startswith("#### ")
            and not stripped.startswith("##### ")
        ):
            h4_title = _parse_title(stripped, "#### ")

    return h2_title or h3_title or h4_title or "Unnamed chapter"
