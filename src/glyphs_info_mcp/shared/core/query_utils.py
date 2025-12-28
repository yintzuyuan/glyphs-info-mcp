"""
Query Processing Utilities Module

Provides unified query preprocessing functionality:
- Tokenization and short word filtering
- Text normalization (case, hyphens, underscores)
- Match score calculation (with case priority)
- Keyword highlighting
"""

import re
from typing import Final

from glyphs_info_mcp.shared.core.scoring_weights import MatchTypeWeights


# Short word filter threshold (for English search)
MIN_WORD_LENGTH: Final[int] = 2


def tokenize_query(query: str, min_length: int = MIN_WORD_LENGTH) -> list[str]:
    """Tokenize and filter short words

    Args:
        query: Original query string
        min_length: Minimum word length (default 2)

    Returns:
        Filtered word list (lowercased)
    """
    words = query.lower().split()
    return [w for w in words if len(w) >= min_length]


def normalize_for_matching(text: str) -> str:
    """Normalize text for matching

    - Convert to lowercase
    - Remove hyphens and underscores

    Args:
        text: Original text

    Returns:
        Normalized text
    """
    return text.lower().replace("-", "").replace("_", "")


def case_insensitive_contains(text: str, query: str) -> bool:
    """Case-insensitive contains check

    Args:
        text: Target text
        query: Query string

    Returns:
        Whether contains (case-insensitive)
    """
    return query.lower() in text.lower()


def calculate_match_score(query: str, target: str) -> float:
    """Calculate match score (with case priority)

    Uses MatchTypeWeights constants for consistency with other modules.

    Scoring rules:
    - Exact match (including case): MatchTypeWeights.EXACT (1.0)
    - Case-insensitive exact match: MatchTypeWeights.CASE_INSENSITIVE_EXACT (0.95)
    - Contains match: MatchTypeWeights.CONTAINS_MATCH (0.6)
    - No match: 0.0

    Args:
        query: Query string
        target: Target string

    Returns:
        Match score (0.0-1.0)
    """
    if query == target:
        return MatchTypeWeights.EXACT  # Exact match (including case)

    if query.lower() == target.lower():
        return MatchTypeWeights.CASE_INSENSITIVE_EXACT  # Case-insensitive exact match

    if query.lower() in target.lower():
        return MatchTypeWeights.CONTAINS_MATCH  # Contains match

    return 0.0  # No match


def highlight_keyword(text: str, keyword: str) -> str:
    """Highlight keyword while preserving original case

    Uses Markdown bold syntax (**) to wrap matching keywords,
    while preserving the original text's case.

    Args:
        text: Original text
        keyword: Keyword to highlight

    Returns:
        Text with highlighted keyword

    Example:
        >>> highlight_keyword("The Anchor is special.", "anchor")
        'The **Anchor** is special.'
    """
    if not keyword:
        return text
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    return pattern.sub(lambda m: f"**{m.group(0)}**", text)
