#!/usr/bin/env python3
"""
Result Formatter - Formats different types of search results.
Supports layered formatting and token optimization.
"""

# mypy: ignore-errors

import logging
from abc import ABC, abstractmethod
from typing import Any

# Import the new configuration system
from .output_config import (
    DetailLevel,
    OutputConfig,
    OutputFormat,
)
from .token_monitor import TokenEstimator, TokenUsage

logger = logging.getLogger(__name__)


class ResultFormatter(ABC):
    """Base class for result formatters."""

    def __init__(self, config: OutputConfig | None = None):
        self.config = config or OutputConfig()
        self.token_budget = self.config.get_token_budget()

    @abstractmethod
    def format_results(
        self, results: list[dict[str, Any]], query: str, **kwargs
    ) -> str:
        """Format search results.

        Args:
            results: List of search results
            query: Original query string
            **kwargs: Additional formatting parameters

        Returns:
            Formatted result string
        """
        pass

    def format_with_config(
        self, results: list[dict[str, Any]], query: str, config: OutputConfig
    ) -> str:
        """Format results with specified config."""
        old_config = self.config
        self.config = config
        self.token_budget = config.get_token_budget()
        try:
            return self.format_results(results, query)
        finally:
            self.config = old_config
            self.token_budget = old_config.get_token_budget()

    def _should_include_section(self, section: str) -> bool:
        """Check if a section should be included."""
        return self.config.should_include_section(section)

    def _get_content_limit(self, limit_type: str) -> int:
        """Get content limit."""
        limits = self.config.get_content_limits()
        return limits.get(limit_type, -1)

    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to specified length."""
        if max_length <= 0 or len(text) <= max_length:
            return text
        return text[:max_length] + "..."


class DefaultResultFormatter(ResultFormatter):
    """Default result formatter - supports layered output."""

    def format_results(
        self, results: list[dict[str, Any]], query: str, **kwargs
    ) -> str:
        """Format search results to standard format.

        Args:
            results: List of search results
            query: Search query string
            **kwargs: Additional parameters

        Returns:
            Formatted result string
        """
        if not results:
            return "No results found."

        # Use config system parameters with backward compatibility
        max_results = kwargs.get("max_results", self.config.max_results)
        max_results = min(max_results, self._get_content_limit("max_api_results"))

        include_source = kwargs.get(
            "include_source", self._should_include_section("related_tools")
        )
        include_score = kwargs.get("include_score", self.config.legacy_format)
        snippet_length = kwargs.get(
            "snippet_length", self._get_content_limit("snippet_length")
        )

        formatted_results = []

        # Sort results (by relevance score or default order)
        sorted_results = self._sort_results(results)

        for i, result in enumerate(sorted_results[:max_results], 1):
            title = result.get("title", f"Result {i}")
            content = result.get("content", result.get("description", ""))
            source = result.get("source", "")
            score = result.get("score", 0.0)

            formatted_result = f"**{i}. {title}**\n"

            if content:
                if snippet_length > 0:
                    snippet = self._truncate_text(content, snippet_length)
                else:
                    snippet = content
                formatted_result += f"{snippet}"

            if include_source and source:
                formatted_result += f"\n*Source: {source}*"

            if include_score:
                formatted_result += f"\n*Relevance: {score:.2f}*"

            formatted_results.append(formatted_result)

        # Add search summary
        summary = self._create_search_summary(len(results), max_results, query)

        formatted_output = f"{summary}\n\n" + "\n\n".join(formatted_results)

        # Add additional sections based on config
        if self._should_include_section("related_tools"):
            formatted_output += self._add_related_tools_section(query)

        return formatted_output

    def _sort_results(self, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Sort search results.

        Priority:
        1. Results with scores are sorted by score
        2. Results without scores maintain original order

        Args:
            results: Original results

        Returns:
            Sorted results
        """
        # Check if any results have scores
        has_scores = any(result.get("score") is not None for result in results)

        if has_scores:
            # Sort by score (high to low)
            return sorted(results, key=lambda x: x.get("score", 0.0), reverse=True)
        else:
            # Maintain original order
            return results

    def _create_search_summary(
        self, total_results: int, displayed_results: int, query: str
    ) -> str:
        """Create search summary.

        Args:
            total_results: Total number of results
            displayed_results: Number of displayed results
            query: Search query

        Returns:
            Search summary
        """
        if self.config.output_format == OutputFormat.CONCISE:
            # Concise format
            if total_results == 0:
                return f"No results found for '{query}'"
            else:
                return f"Found {total_results} results (showing {displayed_results}):"
        else:
            # Standard format
            if total_results == 0:
                return f"Query '{query}' found no results."
            elif total_results <= displayed_results:
                return f"Query '{query}' found {total_results} results:"
            else:
                return f"Query '{query}' found {total_results} results, showing first {displayed_results}:"

    def _add_related_tools_section(self, query: str) -> str:
        """Add related tools recommendation section."""
        if self.config.detail_level == DetailLevel.MINIMAL:
            return ""  # Don't show in minimal mode

        return "\n\n## 🔗 Related Tools\n💡 Use other search tools to get more information"


class HandbookResultFormatter(ResultFormatter):
    """Handbook-specific result formatter - supports layered output."""

    def format_results(
        self, results: list[dict[str, Any]], query: str, **kwargs
    ) -> str:
        """Format handbook search results."""
        if not results:
            if self.config.detail_level == DetailLevel.MINIMAL:
                return f"No content found for '{query}' in handbook"
            else:
                return f"No content found for '{query}' in handbook.\n\n💡 Suggestions:\n- Try searching with English terms\n- Check spelling\n- Use more specific keywords"

        max_results = kwargs.get("max_results", self.config.max_results)
        max_results = min(max_results, self._get_content_limit("max_api_results"))
        formatted_results = []

        for i, result in enumerate(results[:max_results], 1):
            chapter = result.get("chapter", "Unknown chapter")
            title = result.get("title", result.get("name", f"Item {i}"))
            content = result.get("content", result.get("description", ""))

            formatted_result = f"📖 **{i}. {chapter}: {title}**\n"

            if content:
                snippet_length = self._get_content_limit("snippet_length")
                if snippet_length > 0:
                    snippet = self._truncate_text(content, snippet_length)
                else:
                    snippet = content
                formatted_result += f"{snippet}"

            formatted_results.append(formatted_result)

        total = len(results)

        if self.config.output_format == OutputFormat.CONCISE:
            summary = f"📚 Found {total} chapters (showing {min(max_results, total)}):"
        else:
            summary = f"📚 Handbook search '{query}' found {total} chapters, showing first {min(max_results, total)}:"

        formatted_output = f"{summary}\n\n" + "\n\n".join(formatted_results)

        # Add additional info based on config
        if (
            self._should_include_section("learning_resources")
            and self.config.detail_level != DetailLevel.MINIMAL
        ):
            formatted_output += (
                "\n\n💡 More resources: Use `handbook_get_content` to get full chapter content"
            )

        return formatted_output


class APIResultFormatter(ResultFormatter):
    """API-specific result formatter - supports layered output and architecture awareness."""

    def format_results(
        self, results: list[dict[str, Any]], query: str, **kwargs
    ) -> str:
        """Format API search results."""
        if not results:
            return f"No content found for '{query}' in API documentation."

        max_results = kwargs.get("max_results", self.config.max_results)
        max_results = min(max_results, self._get_content_limit("max_api_results"))
        formatted_results = []

        for i, result in enumerate(results[:max_results], 1):
            name = result.get("name", f"API {i}")
            api_type = result.get("type", "unknown")
            description = result.get("description", "")

            # Select icon based on API type
            icon = self._get_api_icon(api_type)
            formatted_name = f"{icon} {name}"

            formatted_result = f"**{i}. {formatted_name}**\n"

            if description:
                desc_length = self._get_content_limit("description_length")
                if desc_length > 0:
                    snippet = self._truncate_text(description, desc_length)
                else:
                    snippet = description
                formatted_result += f"{snippet}"

            formatted_results.append(formatted_result)

        total = len(results)

        if self.config.output_format == OutputFormat.CONCISE:
            summary = f"🐍 Found {total} APIs (showing {min(max_results, total)}):"
        else:
            summary = f"🐍 API search '{query}' found {total} items, showing first {min(max_results, total)}:"

        formatted_output = f"{summary}\n\n" + "\n\n".join(formatted_results)

        # Add architecture awareness hints based on config
        if self._should_include_section(
            "architecture"
        ) and self.config.detail_level not in [
            DetailLevel.MINIMAL,
            DetailLevel.COMPACT,
        ]:
            formatted_output += (
                "\n\n## 🏗️ Architecture Hints\n💡 See Glyphs object model architecture for correct usage patterns"
            )

        # Add related tools recommendation
        if (
            self._should_include_section("related_tools")
            and self.config.detail_level == DetailLevel.FULL
        ):
            formatted_output += "\n\n## 🔗 Related Resources\n💡 Use `api_get_python_class` to view detailed class info"

        return formatted_output

    def _get_api_icon(self, api_type: str) -> str:
        """Return icon based on API type."""
        icons = {
            "property": "⚙️",
            "method": "🔧",
            "class": "📦",
            "function": "⚡",
            "constant": "🔢",
            "unknown": "❓",
        }
        return icons.get(api_type.lower(), "❓")


class NewsResultFormatter(ResultFormatter):
    """News/forum-specific result formatter - supports layered output."""

    def format_results(
        self, results: list[dict[str, Any]], query: str, **kwargs
    ) -> str:
        """Format news/forum search results."""
        if not results:
            return f"No news or discussions found for '{query}'."

        max_results = kwargs.get("max_results", self.config.max_results)
        max_results = min(max_results, self._get_content_limit("max_api_results"))
        formatted_results = []

        for i, result in enumerate(results[:max_results], 1):
            title = result.get("title", f"Item {i}")
            content = result.get("content", result.get("description", ""))
            author = result.get("author", "")
            date = result.get("date", "")
            url = result.get("url", "")

            formatted_result = f"🗞️ **{i}. {title}**\n"

            # Add meta information
            meta_info = []
            if author:
                meta_info.append(f"Author: {author}")
            if date:
                meta_info.append(f"Date: {date}")
            if url:
                meta_info.append(f"Link: {url}")

            if meta_info:
                formatted_result += f"*{' | '.join(meta_info)}*\n\n"

            if content:
                snippet_length = self._get_content_limit("snippet_length")
                if snippet_length > 0:
                    snippet = self._truncate_text(content, snippet_length)
                else:
                    snippet = content
                formatted_result += snippet

            formatted_results.append(formatted_result)

        total = len(results)

        if self.config.output_format == OutputFormat.CONCISE:
            summary = f"🗞️ Found {total} items (showing {min(max_results, total)}):"
        else:
            summary = f"🗞️ News search '{query}' found {total} items, showing first {min(max_results, total)}:"

        return f"{summary}\n\n" + "\n\n".join(formatted_results)


class FormatterFactory:
    """Result formatter factory - supports config injection."""

    _formatters = {
        "default": DefaultResultFormatter,
        "handbook": HandbookResultFormatter,
        "api": APIResultFormatter,
        "news": NewsResultFormatter,
    }

    @classmethod
    def create(
        cls, formatter_type: str = "default", config: OutputConfig | None = None
    ) -> ResultFormatter:
        """Create formatter of specified type.

        Args:
            formatter_type: Formatter type
            config: Output config

        Returns:
            ResultFormatter instance
        """
        formatter_class = cls._formatters.get(formatter_type, DefaultResultFormatter)
        return formatter_class(config)

    @classmethod
    def create_with_legacy_params(
        cls, formatter_type: str = "default", **kwargs
    ) -> ResultFormatter:
        """Create formatter with legacy params (backward compatible).

        Args:
            formatter_type: Formatter type
            **kwargs: Legacy parameters

        Returns:
            ResultFormatter instance
        """
        from .output_config import parse_legacy_params

        config = parse_legacy_params(**kwargs)
        return cls.create(formatter_type, config)

    @classmethod
    def register(cls, name: str, formatter_class):
        """Register a new formatter type."""
        cls._formatters[name] = formatter_class

    @classmethod
    def get_available_types(cls) -> list[str]:
        """Get available formatter types."""
        return list(cls._formatters.keys())

    @classmethod
    def estimate_token_usage(
        cls, formatter_type: str, results: list[dict[str, Any]], config: OutputConfig
    ) -> TokenUsage:
        """Estimate token usage for given config."""
        return TokenEstimator.estimate_structured_output(results, config)
