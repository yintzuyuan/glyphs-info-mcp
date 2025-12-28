"""
SDK Content Searcher
Responsible for searching relevant content in the index
"""
from typing import Any

from glyphs_info_mcp.shared.core.scoring_weights import FieldWeights, MultiWordWeights
from glyphs_info_mcp.shared.core.query_utils import tokenize_query, MIN_WORD_LENGTH


class SDKSearcher:
    """SDK content searcher"""

    def __init__(self, index: dict[str, list[dict[str, Any]]]):
        """
        Initialize searcher

        Args:
            index: Content index built by SDKIndexer
        """
        self.index = index

    def search(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
        """
        Search SDK content

        Args:
            query: Search keyword
            max_results: Maximum number of results

        Returns:
            List of search results with relevance scores
        """
        results = []
        query_lower = query.lower()

        # Search all categories
        for category_name, items in self.index.items():
            for item in items:
                relevance_score = self._calculate_relevance(item, query_lower)

                if relevance_score > 0:
                    result = {
                        "type": item["type"],
                        "category": item.get("category", "unknown"),
                        "path": item["path"],
                        "name": item["name"],
                        "content": item.get("content", ""),
                        "relevance_score": relevance_score
                    }
                    results.append(result)

        # Sort by relevance score
        results.sort(key=lambda x: x["relevance_score"], reverse=True)

        # Limit result count
        return results[:max_results]

    def _calculate_relevance(self, item: dict[str, Any], query: str) -> float:
        """
        Calculate relevance score between item and query
        Supports tokenized search and partial matching

        Uses shared scoring weights and tokenization tools to ensure consistency with other modules.

        Args:
            item: Index item
            query: Search query (lowercase)

        Returns:
            Relevance score (0-1.0)
        """
        score = 0.0

        # Use shared tokenization tool (automatically filters short words)
        query_words = tokenize_query(query, min_length=MIN_WORD_LENGTH)

        # Prepare search text
        content = item.get("content", "").lower()
        name = item.get("name", "").lower()
        path = item.get("path", "").lower()
        category = item.get("category", "").lower()

        # Full query match (highest score) - using shared weights
        if query in content:
            score += FieldWeights.CONTENT + FieldWeights.FULL_MATCH_BONUS  # 0.8 = 0.3 + 0.5
        elif query in name:
            score += FieldWeights.TITLE  # 0.6
        elif query in path:
            score += FieldWeights.OWNER  # 0.4

        # Tokenized matching (already filtered short words via tokenize_query)
        word_matches = 0
        for word in query_words:
            word_score: float = 0.0

            if word in content:
                word_score += FieldWeights.OWNER  # 0.4
            elif word in name:
                word_score += FieldWeights.CONTENT  # 0.3
            elif word in path:
                word_score += MultiWordWeights.PARTIAL_WORD  # 0.1
            elif word in category:
                word_score += MultiWordWeights.PARTIAL_WORD  # 0.1

            if word_score > 0:
                word_matches += 1
                score += word_score

        # Give extra score if multiple words match
        if len(query_words) > 1 and word_matches > 1:
            match_ratio = word_matches / len(query_words)
            score += MultiWordWeights.MULTI_WORD_BONUS * match_ratio  # 0.3 * ratio

        return min(score, 1.0)  # Limit max score to 1.0
