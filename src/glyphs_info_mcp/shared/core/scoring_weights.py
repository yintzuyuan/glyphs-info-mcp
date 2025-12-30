"""
Unified Scoring Weights Constants Module

Provides cross-module consistent search relevance scoring weights, ensuring different
search sources (plugins, SDK, handbook, API, etc.) have comparable scoring standards.

Score range: 0.0 - 1.0
"""

from typing import Final


class MatchTypeWeights:
    """Match type weight constants"""

    # Exact match (query equals target exactly)
    EXACT: Final[float] = 1.0

    # Prefix match (target starts with query)
    PREFIX: Final[float] = 0.95

    # Case-insensitive exact match (for query_utils.calculate_match_score)
    CASE_INSENSITIVE_EXACT: Final[float] = 0.95

    # Contains match (target contains query)
    CONTAINS: Final[float] = 0.85

    # Simple contains match (for query_utils.calculate_match_score)
    CONTAINS_MATCH: Final[float] = 0.6


class FieldWeights:
    """Search field weight constants"""

    # Primary identifier fields
    TITLE: Final[float] = 0.6
    NAME: Final[float] = 0.5

    # Secondary identifier fields
    OWNER: Final[float] = 0.4
    AUTHOR: Final[float] = 0.4
    CATEGORY: Final[float] = 0.35

    # Content fields
    DESCRIPTION: Final[float] = 0.3
    CONTENT: Final[float] = 0.3
    DOCSTRING: Final[float] = 0.25
    COMMENT: Final[float] = 0.2

    # Path fields
    PATH: Final[float] = 0.3
    FILE_NAME: Final[float] = 0.4

    # Full match bonus
    FULL_MATCH_BONUS: Final[float] = 0.5  # Extra points for complete content match


class CodeStructureWeights:
    """Code structure weight constants (API/SDK specific)"""

    # Class/Interface
    CLASS_EXACT: Final[float] = 0.9
    CLASS_CONTAINS: Final[float] = 0.7
    INTERFACE_EXACT: Final[float] = 0.9
    INTERFACE_CONTAINS: Final[float] = 0.7

    # Method
    METHOD_EXACT: Final[float] = 0.85
    METHOD_CONTAINS: Final[float] = 0.6

    # Property
    PROPERTY_EXACT: Final[float] = 0.8
    PROPERTY_CONTAINS: Final[float] = 0.55

    # Protocol
    PROTOCOL_EXACT: Final[float] = 0.85
    PROTOCOL_CONTAINS: Final[float] = 0.65


class MultiWordWeights:
    """Multi-word search weight constants"""

    # Match thresholds
    HIGH_MATCH_THRESHOLD: Final[float] = 0.8  # 80%+ is high match
    MEDIUM_MATCH_THRESHOLD: Final[float] = 0.6  # 60%+ is medium match

    # Base scores
    HIGH_MATCH_BASE: Final[float] = 0.75
    MEDIUM_MATCH_BASE: Final[float] = 0.65

    # Bonus limits
    QUALITY_BONUS_MAX: Final[float] = 0.1
    DENSITY_BONUS_MAX: Final[float] = 0.05

    # Tokenized match weights
    MULTI_WORD_BONUS: Final[float] = 0.3  # Extra points for multi-word match
    PARTIAL_WORD: Final[float] = 0.1  # Single word partial match


class SearchLimits:
    """Search result limit constants

    Controls the maximum number of results and excerpts returned.
    Used to optimize context token usage in LLM conversations.
    """

    # Maximum number of search results to display
    DEFAULT_MAX_RESULTS: Final[int] = 5

    # Maximum number of excerpts per result
    MAX_EXCERPTS_PER_RESULT: Final[int] = 3


# === Backward compatibility aliases ===
# Maintain compatibility with existing OfficialRegistry constants

SCORE_EXACT_MATCH: Final[float] = MatchTypeWeights.EXACT
SCORE_TITLE_MATCH: Final[float] = FieldWeights.TITLE
SCORE_NAME_MATCH: Final[float] = FieldWeights.NAME
SCORE_OWNER_MATCH: Final[float] = FieldWeights.OWNER
SCORE_DESC_MATCH: Final[float] = FieldWeights.DESCRIPTION


# === Helper functions ===


def calculate_weighted_score(
    base_score: float,
    field_weight: float,
    match_type_weight: float = MatchTypeWeights.CONTAINS,
) -> float:
    """Calculate weighted score

    Args:
        base_score: Base score (0.0-1.0)
        field_weight: Field weight
        match_type_weight: Match type weight

    Returns:
        Weighted score, capped at 1.0
    """
    return min(1.0, base_score * field_weight * match_type_weight)


def normalize_score(
    score: float, min_val: float = 0.0, max_val: float = 1.0
) -> float:
    """Normalize score to specified range

    Args:
        score: Original score
        min_val: Minimum value
        max_val: Maximum value

    Returns:
        Normalized score
    """
    return max(min_val, min(max_val, score))
