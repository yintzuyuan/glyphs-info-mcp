#!/usr/bin/env python3
"""
Vocabulary Search Strategy - Search strategy based on vocabulary translation
"""

# mypy: ignore-errors

import logging
from typing import Any

logger = logging.getLogger(__name__)


class VocabularySearchStrategy:
    """Vocabulary Search Strategy - Focuses on vocabulary translation and term matching"""

    def __init__(self, vocabulary_module=None):
        """Initialize vocabulary search strategy

        Args:
            vocabulary_module: Vocabulary module (provides translation services)
        """
        self.vocabulary_module = vocabulary_module

    def search(
        self, query: str, sources: dict[str, Any], **kwargs
    ) -> list[dict[str, Any]]:
        """Execute vocabulary-based search

        Args:
            query: Search query (already preprocessed)
            sources: Available search sources
            **kwargs: Other search parameters
                - max_results: Maximum number of results
                - exact_match: Whether to use exact matching
                - include_synonyms: Whether to include synonyms

        Returns:
            List of search results
        """
        max_results = kwargs.get("max_results", 10)
        exact_match = kwargs.get("exact_match", False)
        include_synonyms = kwargs.get("include_synonyms", True)

        all_results = []

        # 1. Prepare search terms
        search_terms = self._prepare_search_terms(query, include_synonyms)

        # 2. Execute vocabulary search on each source
        for source_name, source in sources.items():
            try:
                source_results = self._search_in_source(
                    source, source_name, search_terms, exact_match, **kwargs
                )

                # Add source info
                for result in source_results:
                    result["source"] = source_name
                    result["strategy"] = "vocabulary"

                all_results.extend(source_results)

            except Exception as e:
                logger.error(f"Vocabulary search failed - source {source_name}: {e}")
                continue

        # 3. Sort and deduplicate
        deduplicated_results = self._deduplicate_results(all_results)
        ranked_results = self._rank_results(deduplicated_results, query, search_terms)

        return ranked_results[:max_results]

    def _prepare_search_terms(self, query: str, include_synonyms: bool) -> list[str]:
        """Prepare search terms

        Args:
            query: Original query
            include_synonyms: Whether to include synonyms

        Returns:
            List of search terms
        """
        terms = [query]

        # Tokenize
        words = query.split()
        if len(words) > 1:
            terms.extend(words)

        # Add synonyms (if vocabulary module available)
        if include_synonyms and self.vocabulary_module:
            synonyms = self._get_synonyms(query)
            terms.extend(synonyms)

        # Deduplicate while preserving order
        unique_terms = []
        seen = set()
        for term in terms:
            term_lower = term.lower().strip()
            if term_lower and term_lower not in seen:
                unique_terms.append(term)
                seen.add(term_lower)

        logger.debug(f"Prepared search terms: {unique_terms}")
        return unique_terms

    def _get_synonyms(self, query: str) -> list[str]:
        """Get synonyms

        Args:
            query: Query term

        Returns:
            List of synonyms
        """
        synonyms = []

        if not self.vocabulary_module or not self.vocabulary_module.is_initialized:
            return synonyms

        try:
            # If Chinese, translate to English first
            english_term = self.vocabulary_module.translate_to_english(query)
            if english_term != query:
                synonyms.append(english_term)

            # If English, translate to Chinese
            chinese_term = self.vocabulary_module.translate_to_chinese(query)
            if chinese_term != query:
                synonyms.append(chinese_term)

            # More synonym logic can be added here

        except Exception as e:
            logger.debug(f"Failed to get synonyms: {e}")

        return synonyms

    def _search_in_source(
        self,
        source: Any,
        source_name: str,
        search_terms: list[str],
        exact_match: bool,
        **kwargs,
    ) -> list[dict[str, Any]]:
        """Search in a specific source

        Args:
            source: Search source instance
            source_name: Source name
            search_terms: List of search terms
            exact_match: Whether to use exact matching
            **kwargs: Other parameters

        Returns:
            List of search results
        """
        results = []

        # Select search method based on source type
        if source_name == "handbook":
            results = self._search_handbook(source, search_terms, exact_match, **kwargs)
        elif source_name == "api":
            results = self._search_api(source, search_terms, exact_match, **kwargs)
        elif source_name == "news":
            results = self._search_news(source, search_terms, exact_match, **kwargs)
        else:
            # Generic search method
            results = self._generic_search(source, search_terms, exact_match, **kwargs)

        return results

    def _search_handbook(
        self, handbook_source: Any, search_terms: list[str], exact_match: bool, **kwargs
    ) -> list[dict[str, Any]]:
        """Search in handbook"""
        results = []

        try:
            # Use handbook module's internal search method
            if hasattr(handbook_source, "_unified_search"):
                for term in search_terms:
                    term_results = handbook_source._unified_search(
                        term, kwargs.get("max_results", 5)
                    )
                    # Convert string results to structured results
                    if isinstance(term_results, str) and term_results.strip():
                        results.append(
                            {
                                "title": f"Handbook Search: {term}",
                                "content": term_results,
                                "term": term,
                                "score": self._calculate_term_score(
                                    term, search_terms[0]
                                ),
                            }
                        )
        except Exception as e:
            logger.debug(f"Handbook vocabulary search failed: {e}")

        return results

    def _search_api(
        self, api_source: Any, search_terms: list[str], exact_match: bool, **kwargs
    ) -> list[dict[str, Any]]:
        """Search in API documentation"""
        results = []

        try:
            # Use API module's search method
            if hasattr(api_source, "python_api") and hasattr(
                api_source.python_api, "search"
            ):
                for term in search_terms:
                    term_results = api_source.python_api.search(
                        term, exact_match=exact_match
                    )
                    # Convert results to unified format
                    if isinstance(term_results, list):
                        for result in term_results:
                            results.append(
                                {
                                    "title": result.get("name", f"API: {term}"),
                                    "content": result.get("description", ""),
                                    "type": result.get("type", "unknown"),
                                    "class_name": result.get("class_name", ""),
                                    "term": term,
                                    "score": self._calculate_term_score(
                                        term, search_terms[0]
                                    ),
                                }
                            )
        except Exception as e:
            logger.debug(f"API vocabulary search failed: {e}")

        return results

    def _search_news(
        self, news_source: Any, search_terms: list[str], exact_match: bool, **kwargs
    ) -> list[dict[str, Any]]:
        """Search in news/forum"""
        results = []

        # News search usually requires network connection, returning empty results for now
        # Network search logic can be added in future implementation
        logger.debug("News vocabulary search not yet implemented")

        return results

    def _generic_search(
        self, source: Any, search_terms: list[str], exact_match: bool, **kwargs
    ) -> list[dict[str, Any]]:
        """Generic search method"""
        results = []

        # Try calling source's generic search method
        try:
            if hasattr(source, "search"):
                for term in search_terms:
                    term_results = source.search(term)
                    if isinstance(term_results, str) and term_results.strip():
                        results.append(
                            {
                                "title": f"Search: {term}",
                                "content": term_results,
                                "term": term,
                                "score": self._calculate_term_score(
                                    term, search_terms[0]
                                ),
                            }
                        )
        except Exception as e:
            logger.debug(f"Generic vocabulary search failed: {e}")

        return results

    def _calculate_term_score(self, term: str, original_query: str) -> float:
        """Calculate term relevance score

        Args:
            term: Search term
            original_query: Original query

        Returns:
            Relevance score (0.0-1.0)
        """
        if term.lower() == original_query.lower():
            return 1.0  # Exact match

        if (
            term.lower() in original_query.lower()
            or original_query.lower() in term.lower()
        ):
            return 0.8  # Partial match

        # Simple text similarity (can be replaced with more complex algorithms)
        common_chars = set(term.lower()) & set(original_query.lower())
        if common_chars:
            similarity = len(common_chars) / max(
                len(set(term.lower())), len(set(original_query.lower()))
            )
            return max(0.3, similarity)

        return 0.3  # Default score (for synonyms, etc.)

    def _deduplicate_results(
        self, results: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Deduplicate results

        Args:
            results: Original results list

        Returns:
            Deduplicated results list
        """
        seen = set()
        unique_results = []

        for result in results:
            # Use title and first 50 characters of content as dedup key
            title = result.get("title", "")
            content = result.get("content", "")[:50]
            key = f"{title}:{content}".lower().strip()

            if key not in seen:
                unique_results.append(result)
                seen.add(key)

        return unique_results

    def _rank_results(
        self,
        results: list[dict[str, Any]],
        original_query: str,
        search_terms: list[str],
    ) -> list[dict[str, Any]]:
        """Rank results

        Args:
            results: Results list
            original_query: Original query
            search_terms: Search terms list

        Returns:
            Ranked results list
        """

        # Sort by score (if no score, use term order)
        def sort_key(result):
            score = result.get("score", 0.5)
            # Prioritize original query results
            if result.get("term", "").lower() == original_query.lower():
                score += 0.2
            return score

        return sorted(results, key=sort_key, reverse=True)
