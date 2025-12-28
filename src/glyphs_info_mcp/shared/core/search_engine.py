#!/usr/bin/env python3
"""
Unified Search Engine - Integrates vocabulary processing, search strategy selection, and result formatting
"""

# mypy: ignore-errors

import logging
from typing import Any, Protocol

logger = logging.getLogger(__name__)


class SearchStrategy(Protocol):
    """Search strategy interface"""

    def search(
        self, query: str, sources: dict[str, Any], **kwargs
    ) -> list[dict[str, Any]]:
        """Execute search"""
        ...


class QueryProcessor(Protocol):
    """Query processor interface"""

    def preprocess_query(self, query: str) -> tuple[str, str]:
        """Preprocess query - returns (processed_query, user_language)"""
        ...

    def postprocess_output(self, content: str, user_language: str) -> str:
        """Post-process output"""
        ...


class ResultFormatter(Protocol):
    """Result formatter interface"""

    def format_results(
        self, results: list[dict[str, Any]], query: str, **kwargs
    ) -> str:
        """Format search results"""
        ...


class SearchEngine:
    """Unified search engine - Coordinates all search-related functionality"""

    def __init__(
        self,
        query_processor: QueryProcessor | None = None,
        result_formatter: ResultFormatter | None = None,
    ):
        """Initialize search engine

        Args:
            query_processor: Query processor (vocabulary conversion, etc.)
            result_formatter: Result formatter
        """
        self.query_processor = query_processor
        self.result_formatter = result_formatter
        self.strategies: dict[str, SearchStrategy] = {}
        self.source_registry: dict[str, Any] = {}
        self.source_types: dict[str, list[str]] = {}  # Source type labels

    def register_strategy(self, name: str, strategy: SearchStrategy):
        """Register search strategy

        Args:
            name: Strategy name
            strategy: Search strategy instance
        """
        self.strategies[name] = strategy
        logger.debug(f"Registered search strategy: {name}")

    def register_source(
        self, name: str, source: Any, source_types: list[str] | None = None
    ):
        """Register search source

        Args:
            name: Source name (e.g., 'handbook', 'api', 'web')
            source: Search source instance (module or service)
            source_types: Source type label list (e.g., ['python', 'api'], ['objc_headers'], ['handbook'])
        """
        self.source_registry[name] = source
        if source_types:
            self.source_types[name] = source_types
        else:
            self.source_types[name] = ["general"]  # Default type
        logger.debug(f"Registered search source: {name} (types: {self.source_types[name]})")

    def search(
        self,
        query: str,
        sources: list[str] | None = None,
        strategy: str = "hybrid",
        max_results: int = 5,
        source_types: list[str] | None = None,
        **kwargs,
    ) -> str:
        """Unified search entry point

        Args:
            query: Search query
            sources: Specified search source list, None for auto-selection
            strategy: Search strategy name
            max_results: Maximum number of results
            source_types: Limit source type list (e.g., ['python'], ['objc_headers'], ['handbook'])
            **kwargs: Other search parameters

        Returns:
            Formatted search result string
        """
        try:
            # 1. Query preprocessing (vocabulary conversion, etc.)
            processed_query, user_language = self._preprocess_query(query)

            # 2. Select search sources
            selected_sources = self._select_sources(
                processed_query, sources, source_types
            )

            # 3. Select and execute search strategy
            search_strategy = self._get_strategy(strategy)
            if not search_strategy:
                return f"Search strategy not found: {strategy}"

            # 4. Execute search
            results = search_strategy.search(
                processed_query, selected_sources, max_results=max_results, **kwargs
            )

            # 5. Format results
            formatted_results = self._format_results(results, query, **kwargs)

            # 6. Post-process output (terminology localization, etc.)
            final_output = self._postprocess_output(formatted_results, user_language)

            logger.debug(f"Search completed: '{query}' -> {len(results)} results")
            return final_output

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return f"Search failed: {str(e)}"

    def _preprocess_query(self, query: str) -> tuple[str, str]:
        """Preprocess query"""
        if self.query_processor:
            return self.query_processor.preprocess_query(query)
        return query, "en"  # Default English

    def _select_sources(
        self,
        query: str,
        sources: list[str] | None,
        source_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """Select search sources"""
        selected = {}

        if sources is None:
            # Auto-select all available sources, but can filter by type
            candidates = self.source_registry.copy()
        else:
            # Filter by specified sources
            candidates = {}
            for source_name in sources:
                if source_name in self.source_registry:
                    candidates[source_name] = self.source_registry[source_name]
                else:
                    logger.warning(f"Search source not found: {source_name}")

        # If source types specified, filter by type
        if source_types:
            for source_name, source in candidates.items():
                source_source_types = self.source_types.get(source_name, ["general"])
                # Check for intersection
                if any(stype in source_types for stype in source_source_types):
                    selected[source_name] = source
                    logger.debug(
                        f"Selected search source: {source_name} (matches types: {source_types})"
                    )
                else:
                    logger.debug(
                        f"Skipped search source: {source_name} (type mismatch: {source_source_types} vs {source_types})"
                    )
        else:
            selected = candidates

        return selected

    def _get_strategy(self, strategy_name: str) -> SearchStrategy | None:
        """Get search strategy"""
        if strategy_name not in self.strategies:
            logger.error(f"Search strategy not found: {strategy_name}")
            return None
        return self.strategies[strategy_name]

    def _format_results(
        self, results: list[dict[str, Any]], query: str, **kwargs
    ) -> str:
        """Format results"""
        if self.result_formatter:
            return self.result_formatter.format_results(results, query, **kwargs)

        # Default formatting
        if not results:
            return "No results found"

        formatted = []
        for i, result in enumerate(results[: kwargs.get("max_results", 5)], 1):
            title = result.get("title", "Untitled")
            content = result.get("content", result.get("description", ""))[:200]
            formatted.append(f"{i}. **{title}**\n{content}...")

        return "\n\n".join(formatted)

    def _postprocess_output(self, content: str, user_language: str) -> str:
        """Post-process output"""
        if self.query_processor:
            return self.query_processor.postprocess_output(content, user_language)
        return content

    def get_available_strategies(self) -> list[str]:
        """Get list of available search strategies"""
        return list(self.strategies.keys())

    def get_available_sources(self) -> list[str]:
        """Get list of available search sources"""
        return list(self.source_registry.keys())

    def health_check(self) -> dict[str, Any]:
        """Health check"""
        return {
            "query_processor": self.query_processor is not None,
            "result_formatter": self.result_formatter is not None,
            "strategies": len(self.strategies),
            "sources": len(self.source_registry),
            "available_strategies": self.get_available_strategies(),
            "available_sources": self.get_available_sources(),
            "source_types": self.source_types,
        }


class SearchEngineFactory:
    """Search engine factory class"""

    @staticmethod
    def create_default_engine(vocabulary_module=None) -> SearchEngine:
        """Create default search engine instance

        Args:
            vocabulary_module: Vocabulary module (for vocabulary conversion)

        Returns:
            SearchEngine instance
        """
        engine = SearchEngine()

        # Lazy import and setup to avoid circular dependencies
        try:
            # Set up query processor
            if vocabulary_module:
                from .query_processor import QueryProcessorImpl

                query_processor = QueryProcessorImpl(vocabulary_module)
                engine.query_processor = query_processor

            # Set up result formatter
            from .result_formatter import DefaultResultFormatter

            result_formatter = DefaultResultFormatter()
            engine.result_formatter = result_formatter

            # Register default strategies
            from .strategy.hybrid_strategy import HybridSearchStrategy
            from .strategy.vocabulary_strategy import VocabularySearchStrategy

            # Create strategy instances
            hybrid_strategy = HybridSearchStrategy(vocabulary_module)
            vocab_strategy = VocabularySearchStrategy(vocabulary_module)

            engine.register_strategy("hybrid", hybrid_strategy)
            engine.register_strategy("vocabulary", vocab_strategy)

            logger.info("Search engine initialization complete")

        except ImportError as e:
            logger.warning(f"Search engine initialization partially failed: {e}")

        return engine
