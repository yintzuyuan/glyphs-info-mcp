#!/usr/bin/env python3
"""
Hybrid Search Strategy - Smart search strategy combining multiple search methods
"""

# mypy: ignore-errors

import logging
from typing import Any

logger = logging.getLogger(__name__)


class HybridSearchStrategy:
    """Hybrid Search Strategy - Combines vocabulary matching, content search, semantic understanding"""

    def __init__(self, vocabulary_module=None):
        """Initialize hybrid search strategy

        Args:
            vocabulary_module: Vocabulary module (provides translation services)
        """
        self.vocabulary_module = vocabulary_module

        # Import sub-strategies
        from .vocabulary_strategy import VocabularySearchStrategy

        self.vocabulary_strategy = VocabularySearchStrategy(vocabulary_module)

    def search(
        self, query: str, sources: dict[str, Any], **kwargs
    ) -> list[dict[str, Any]]:
        """Execute hybrid search

        Args:
            query: Search query (already preprocessed)
            sources: Available search sources
            **kwargs: Other search parameters
                - max_results: Maximum number of results
                - strategy_weights: Weights for each strategy
                - min_score: Minimum relevance score threshold

        Returns:
            List of search results
        """
        max_results = kwargs.get("max_results", 10)
        strategy_weights = kwargs.get(
            "strategy_weights",
            {"vocabulary": 0.4, "content": 0.3, "semantic": 0.2, "popularity": 0.1},
        )
        min_score = kwargs.get("min_score", 0.1)

        all_results = []

        # 1. Execute multiple search strategies
        search_strategies = [
            ("vocabulary", self._vocabulary_search),
            ("content", self._content_search),
            ("semantic", self._semantic_search),
        ]

        for strategy_name, search_func in search_strategies:
            try:
                strategy_results = search_func(query, sources, **kwargs)

                # Add strategy info and weight to results
                weight = strategy_weights.get(strategy_name, 0.25)
                for result in strategy_results:
                    result["search_strategy"] = strategy_name
                    result["strategy_weight"] = weight
                    # Adjust score
                    original_score = result.get("score", 0.5)
                    result["weighted_score"] = original_score * weight

                all_results.extend(strategy_results)
                logger.debug(
                    f"Hybrid search - {strategy_name} strategy found {len(strategy_results)} results"
                )

            except Exception as e:
                logger.error(f"Hybrid search - {strategy_name} strategy failed: {e}")
                continue

        # 2. Merge and sort results
        merged_results = self._merge_results(all_results)

        # 3. Rescore results
        rescored_results = self._rescore_results(
            merged_results, query, strategy_weights
        )

        # 4. Filter low-score results
        filtered_results = [
            r for r in rescored_results if r.get("final_score", 0) >= min_score
        ]

        # 5. Final sorting
        final_results = sorted(
            filtered_results, key=lambda x: x.get("final_score", 0), reverse=True
        )

        logger.info(f"Hybrid search '{query}' completed: found {len(final_results)} results")
        return final_results[:max_results]

    def _vocabulary_search(
        self, query: str, sources: dict[str, Any], **kwargs
    ) -> list[dict[str, Any]]:
        """Vocabulary search"""
        return self.vocabulary_strategy.search(query, sources, **kwargs)

    def _content_search(
        self, query: str, sources: dict[str, Any], **kwargs
    ) -> list[dict[str, Any]]:
        """Content search - Full-text search in document content"""
        results = []

        for source_name, source in sources.items():
            try:
                source_results = self._content_search_in_source(
                    source, source_name, query, **kwargs
                )

                for result in source_results:
                    result["source"] = source_name
                    result["strategy"] = "content"

                results.extend(source_results)

            except Exception as e:
                logger.debug(f"Content search failed - source {source_name}: {e}")
                continue

        return results

    def _content_search_in_source(
        self, source: Any, source_name: str, query: str, **kwargs
    ) -> list[dict[str, Any]]:
        """Execute content search in a specific source"""
        results = []

        if source_name == "handbook":
            results = self._content_search_handbook(source, query, **kwargs)
        elif source_name == "api":
            results = self._content_search_api(source, query, **kwargs)
        # Can add more source types

        return results

    def _content_search_handbook(
        self, handbook_source: Any, query: str, **kwargs
    ) -> list[dict[str, Any]]:
        """Handbook content search"""
        results = []

        try:
            # Assume handbook has content search functionality
            if hasattr(handbook_source, "search_content"):
                content_results = handbook_source.search_content(query)
                if isinstance(content_results, list):
                    for result in content_results:
                        results.append(
                            {
                                "title": result.get("title", "Handbook Content"),
                                "content": result.get("content", ""),
                                "chapter": result.get("chapter", ""),
                                "score": self._calculate_content_score(
                                    query, result.get("content", "")
                                ),
                            }
                        )
            elif hasattr(handbook_source, "_unified_search"):
                # Use existing search method
                search_result = handbook_source._unified_search(
                    query, kwargs.get("max_results", 5)
                )
                if isinstance(search_result, str) and search_result.strip():
                    results.append(
                        {
                            "title": f"Handbook Content: {query}",
                            "content": search_result,
                            "score": self._calculate_content_score(
                                query, search_result
                            ),
                        }
                    )
        except Exception as e:
            logger.debug(f"Handbook content search failed: {e}")

        return results

    def _content_search_api(
        self, api_source: Any, query: str, **kwargs
    ) -> list[dict[str, Any]]:
        """API content search"""
        results = []

        try:
            # Use API source's core_search method
            if hasattr(api_source, "core_search"):
                max_results = kwargs.get("max_results", 10)
                scope = kwargs.get("scope", "auto")
                core_results = api_source.core_search(
                    query, max_results=max_results, scope=scope
                )

                # Ensure results contain required fields
                for result in core_results:
                    if not isinstance(result, dict):
                        continue

                    # Calculate content relevance score
                    content = result.get("content", "")
                    score = self._calculate_content_score(query, content)

                    # Add to results
                    result["score"] = max(result.get("score", 0.5), score)
                    results.append(result)

            # Fallback: try using basic search method
            elif hasattr(api_source, "python_api") and hasattr(
                api_source.python_api, "search"
            ):
                search_result = api_source.python_api.search(query)
                if search_result and "found" in search_result.lower():
                    results.append(
                        {
                            "title": f"API Search: {query}",
                            "content": search_result,
                            "type": "general",
                            "source": "api",
                            "score": 0.6,
                        }
                    )

        except Exception as e:
            logger.debug(f"API content search failed: {e}")

        return results

    def _semantic_search(
        self, query: str, sources: dict[str, Any], **kwargs
    ) -> list[dict[str, Any]]:
        """Semantic search - Search based on concepts and semantic relationships"""
        results = []

        # 1. Analyze query semantics
        semantic_concepts = self._extract_semantic_concepts(query)

        # 2. Perform expanded search for each concept
        for concept in semantic_concepts:
            for source_name, source in sources.items():
                try:
                    concept_results = self._semantic_search_in_source(
                        source, source_name, concept, **kwargs
                    )

                    for result in concept_results:
                        result["source"] = source_name
                        result["strategy"] = "semantic"
                        result["semantic_concept"] = concept

                    results.extend(concept_results)

                except Exception as e:
                    logger.debug(
                        f"Semantic search failed - source {source_name}, concept {concept}: {e}"
                    )
                    continue

        return results

    def _extract_semantic_concepts(self, query: str) -> list[str]:
        """Extract semantic concepts from query"""
        concepts = [query]  # Original query

        # Basic concept expansion
        words = query.lower().split()

        # Glyphs professional concept mapping
        concept_mappings = {
            "font": ["typeface", "family", "style"],
            "glyph": ["character", "letter", "symbol"],
            "layer": ["outline", "shape", "path"],
            "master": ["style", "weight", "instance"],
            "anchor": ["attachment", "point", "position"],
            "component": ["reference", "composite", "element"],
            "kerning": ["spacing", "letter-spacing", "metrics"],
            "feature": ["opentype", "substitution", "positioning"],
            "export": ["generate", "output", "build"],
            "script": ["automation", "python", "macro"],
        }

        for word in words:
            if word in concept_mappings:
                concepts.extend(concept_mappings[word])

        # Add vocabulary translated concepts (if vocabulary module available)
        if self.vocabulary_module and self.vocabulary_module.is_initialized:
            try:
                translated = self.vocabulary_module.translate_to_english(query)
                if translated != query:
                    concepts.append(translated)

                translated_zh = self.vocabulary_module.translate_to_chinese(query)
                if translated_zh != query:
                    concepts.append(translated_zh)
            except Exception as e:
                logger.debug(f"Semantic concept translation failed: {e}")

        # Deduplicate
        unique_concepts = list(dict.fromkeys(concepts))
        logger.debug(f"Semantic concepts: {unique_concepts}")
        return unique_concepts

    def _semantic_search_in_source(
        self, source: Any, source_name: str, concept: str, **kwargs
    ) -> list[dict[str, Any]]:
        """Execute semantic search in a specific source"""
        results = []

        # More complex semantic search logic can be implemented here
        # Currently using simplified version
        try:
            if hasattr(source, "_unified_search"):
                search_result = source._unified_search(concept, 3)  # Limit results per concept
                if isinstance(search_result, str) and search_result.strip():
                    results.append(
                        {
                            "title": f"Semantic Search: {concept}",
                            "content": search_result,
                            "score": self._calculate_semantic_score(
                                concept, search_result
                            ),
                        }
                    )
        except Exception as e:
            logger.debug(f"Semantic search failed: {e}")

        return results

    def _calculate_content_score(self, query: str, content: str) -> float:
        """Calculate content relevance score"""
        if not content:
            return 0.0

        query_lower = query.lower()
        content_lower = content.lower()

        # Exact match
        if query_lower in content_lower:
            return 0.9

        # Word match
        query_words = set(query_lower.split())
        content_words = set(content_lower.split())

        if query_words:
            matches = query_words & content_words
            match_ratio = len(matches) / len(query_words)
            return max(0.1, match_ratio * 0.8)

        return 0.1

    def _calculate_semantic_score(self, concept: str, content: str) -> float:
        """Calculate semantic relevance score"""
        # Simplified semantic scoring
        content_score = self._calculate_content_score(concept, content)
        # Semantic search results score slightly lower due to potential imprecision
        return content_score * 0.7

    def _merge_results(self, all_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Merge results from different strategies"""
        merged = {}

        for result in all_results:
            # Use title and source as merge key
            title = result.get("title", "")
            source = result.get("source", "unknown")
            key = f"{source}:{title}".lower().strip()

            if key in merged:
                # Merge results, keep highest score
                existing = merged[key]
                if result.get("weighted_score", 0) > existing.get("weighted_score", 0):
                    # Preserve strategy info
                    existing["search_strategies"] = existing.get(
                        "search_strategies", []
                    )
                    existing["search_strategies"].append(
                        result.get("search_strategy", "unknown")
                    )
                    existing.update(result)
                else:
                    existing["search_strategies"] = existing.get(
                        "search_strategies", []
                    )
                    existing["search_strategies"].append(
                        result.get("search_strategy", "unknown")
                    )
            else:
                result["search_strategies"] = [result.get("search_strategy", "unknown")]
                merged[key] = result

        return list(merged.values())

    def _rescore_results(
        self,
        results: list[dict[str, Any]],
        query: str,
        strategy_weights: dict[str, float],
    ) -> list[dict[str, Any]]:
        """Rescore results"""
        for result in results:
            scores = []
            strategies = result.get("search_strategies", [])

            # Base score
            base_score = result.get("score", 0.5)

            # Multi-strategy bonus
            strategy_bonus = len(set(strategies)) * 0.1

            # Source weights
            source_weights = {"handbook": 1.0, "api": 0.9, "news": 0.7}
            source_weight = source_weights.get(result.get("source", ""), 0.8)

            # Calculate final score
            final_score = (base_score + strategy_bonus) * source_weight
            result["final_score"] = min(1.0, final_score)

        return results
