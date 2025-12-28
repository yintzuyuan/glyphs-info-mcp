#!/usr/bin/env python3
"""
Response utilities for MCP tools
Provides character limit enforcement, response truncation, and format conversion
"""

import json
import logging
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

# MCP standard character limit (follows MCP best practices)
CHARACTER_LIMIT = 25000

# MCP standard pagination defaults
DEFAULT_LIMIT = 20  # Default items per page
MAX_LIMIT = 100  # Maximum items per page


class ResponseFormat(str, Enum):
    """Response format enum."""

    JSON = "json"
    MARKDOWN = "markdown"


class PaginationInfo:
    """Pagination info class.

    Encapsulates pagination-related metadata.
    """

    def __init__(
        self,
        total_count: int,
        offset: int,
        limit: int,
        current_count: int,
    ):
        """Initialize pagination info.

        Args:
            total_count: Total number of items
            offset: Current start position
            limit: Items per page
            current_count: Actual number of items on current page
        """
        self.total_count = total_count
        self.offset = offset
        self.limit = limit
        self.current_count = current_count

    @property
    def has_more(self) -> bool:
        """Whether there are more results."""
        return self.offset + self.current_count < self.total_count

    @property
    def next_offset(self) -> int | None:
        """Start position of next page."""
        if self.has_more:
            return self.offset + self.current_count
        return None

    @property
    def previous_offset(self) -> int | None:
        """Start position of previous page."""
        if self.offset > 0:
            return max(0, self.offset - self.limit)
        return None

    @property
    def total_pages(self) -> int:
        """Total number of pages."""
        return (self.total_count + self.limit - 1) // self.limit

    @property
    def current_page(self) -> int:
        """Current page number (1-based)."""
        return (self.offset // self.limit) + 1

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary (for JSON response).

        Returns:
            Dictionary containing pagination info
        """
        data: dict[str, Any] = {
            "total_count": self.total_count,
            "offset": self.offset,
            "limit": self.limit,
            "count": self.current_count,
            "has_more": self.has_more,
        }

        if self.next_offset is not None:
            data["next_offset"] = self.next_offset

        if self.previous_offset is not None:
            data["previous_offset"] = self.previous_offset

        data["total_pages"] = self.total_pages
        data["current_page"] = self.current_page

        return data

    def to_markdown_summary(self) -> str:
        """Convert to Markdown summary.

        Returns:
            Pagination info in Markdown format
        """
        lines = []

        # Basic info
        lines.append(
            f"**Showing**: {self.offset + 1}-{self.offset + self.current_count} / {self.total_count} items"
        )
        lines.append(f"**Page**: {self.current_page}/{self.total_pages}")

        # Navigation hints
        if self.has_more:
            lines.append(f"**Next page**: Use `offset={self.next_offset}` to see more results")

        if self.previous_offset is not None:
            lines.append(f"**Previous page**: Use `offset={self.previous_offset}` to go back")

        return "\n".join(lines)


# ============================================================================
# Pagination Helper Functions
# ============================================================================


def paginate_results(
    all_items: list[Any],
    offset: int = 0,
    limit: int = DEFAULT_LIMIT,
) -> tuple[list[Any], PaginationInfo]:
    """
    Paginate a list of items.

    Args:
        all_items: Complete list of items
        offset: Start position (default 0)
        limit: Items per page (default 20)

    Returns:
        Tuple of (current page items, pagination info)
    """
    # Validate and normalize parameters
    offset = max(0, offset)  # Cannot be negative
    limit = min(max(1, limit), MAX_LIMIT)  # 1 <= limit <= MAX_LIMIT

    # Calculate total count
    total_count = len(all_items)

    # Extract current page
    page_items = all_items[offset : offset + limit]

    # Create pagination info
    pagination = PaginationInfo(
        total_count=total_count,
        offset=offset,
        limit=limit,
        current_count=len(page_items),
    )

    return page_items, pagination


def validate_pagination_params(offset: int, limit: int) -> tuple[int, int, str | None]:
    """
    Validate pagination parameters.

    Args:
        offset: Start position
        limit: Items per page

    Returns:
        Tuple of (normalized offset, normalized limit, error message or None)
    """
    error_msg = None

    # Validate offset
    if offset < 0:
        error_msg = f"offset must be >= 0, got: {offset}"
        offset = 0

    # Validate limit
    if limit < 1:
        error_msg = f"limit must be >= 1, got: {limit}"
        limit = DEFAULT_LIMIT
    elif limit > MAX_LIMIT:
        error_msg = f"limit cannot exceed {MAX_LIMIT}, got: {limit}. Adjusted to {MAX_LIMIT}"
        limit = MAX_LIMIT

    return offset, limit, error_msg


def truncate_response(
    response: str, query: str = "", limit: int = CHARACTER_LIMIT
) -> str:
    """
    Smart truncate long responses with guidance.

    Args:
        response: Original response string
        query: Original query (for suggestions)
        limit: Character limit (default 25000)

    Returns:
        Truncated response (if needed) or original response
    """
    if len(response) <= limit:
        return response

    # Calculate truncation point (80% for content, 20% for truncation message)
    truncate_to = int(limit * 0.8)

    # Generate truncation message
    truncation_msg = _generate_truncation_message(
        original_length=len(response),
        truncated_length=truncate_to,
        query=query,
        limit=limit,
    )

    # Truncate and add message
    truncated = response[:truncate_to]
    return truncated + "\n\n" + truncation_msg


def truncate_list_response(
    items: list[Any], response_text: str, query: str = "", limit: int = CHARACTER_LIMIT
) -> str:
    """
    Smart truncate list-type responses with more precise suggestions.

    When response consists of multiple items, calculate how many items to keep.

    Args:
        items: Original list of items
        response_text: Formatted response text
        query: Original query
        limit: Character limit

    Returns:
        Truncated response or original response
    """
    if len(response_text) <= limit:
        return response_text

    # Calculate average length per item
    total_items = len(items)
    avg_length = (
        len(response_text) / total_items if total_items > 0 else len(response_text)
    )

    # Calculate how many items to keep (reserve 80% space)
    keep_items = max(1, int((limit * 0.8) / avg_length))

    # Generate list-specific truncation message
    truncation_msg = _generate_list_truncation_message(
        total_items=total_items,
        kept_items=keep_items,
        original_length=len(response_text),
        query=query,
        limit=limit,
    )

    # Re-format truncated content
    # Note: This needs to be handled by caller, here only returns message
    return response_text[: int(limit * 0.8)] + "\n\n" + truncation_msg


def _generate_truncation_message(
    original_length: int, truncated_length: int, query: str, limit: int
) -> str:
    """Generate generic truncation message."""
    removed_chars = original_length - truncated_length

    msg = "=" * 60 + "\n"
    msg += "⚠️ **Response Truncated**\n\n"
    msg += (
        f"**Reason**: Response length ({original_length:,} chars) exceeds limit ({limit:,} chars)\n\n"
    )
    msg += "**Statistics**:\n"
    msg += f"- Original length: {original_length:,} chars\n"
    msg += f"- Displayed: {truncated_length:,} chars\n"
    msg += f"- Truncated: {removed_chars:,} chars ({removed_chars * 100 / original_length:.1f}%)\n\n"
    msg += "**Suggested Actions**:\n"

    if query:
        msg += f"1. Use more specific search terms instead of '{query}'\n"
    else:
        msg += "1. Use more specific search terms to narrow scope\n"

    msg += "2. Use `limit` parameter to reduce result count\n"
    msg += "3. Use pagination parameter (`offset`) to view page by page\n"
    msg += "4. Use `response_format='json'` for more compact output\n"
    msg += "=" * 60

    return msg


def _generate_list_truncation_message(
    total_items: int, kept_items: int, original_length: int, query: str, limit: int
) -> str:
    """Generate list-specific truncation message."""
    removed_items = total_items - kept_items

    msg = "=" * 60 + "\n"
    msg += "⚠️ **Response Truncated (List Too Long)**\n\n"
    msg += (
        f"**Reason**: Response length ({original_length:,} chars) exceeds limit ({limit:,} chars)\n\n"
    )
    msg += "**Statistics**:\n"
    msg += f"- Total results: {total_items:,} items\n"
    msg += f"- Displayed: {kept_items:,} items\n"
    msg += (
        f"- Truncated: {removed_items:,} items ({removed_items * 100 / total_items:.1f}%)\n"
    )
    msg += f"- Average length: {original_length // total_items:,} chars/item\n\n"
    msg += "**Suggested Actions**:\n"

    if query:
        msg += f"1. Use more specific search terms instead of '{query}'\n"
    else:
        msg += "1. Use more specific search terms\n"

    msg += f"2. Set `limit={kept_items}` or smaller value\n"
    msg += f"3. Use pagination: set `offset={kept_items}` to view remaining results\n"
    msg += "4. Use `response_format='json'` for more compact output\n"
    msg += "5. Use more precise filters to narrow scope\n"
    msg += "=" * 60

    return msg


def check_response_length(response: str, tool_name: str = "unknown") -> None:
    """
    Check response length and log warnings (for monitoring).

    Args:
        response: Response string
        tool_name: Tool name (for logging)
    """
    length = len(response)

    if length > CHARACTER_LIMIT:
        logger.warning(
            f"Tool '{tool_name}' returned oversized response: "
            f"{length:,} chars (limit: {CHARACTER_LIMIT:,})"
        )
    elif length > CHARACTER_LIMIT * 0.8:
        logger.info(
            f"Tool '{tool_name}' approaching limit: "
            f"{length:,} chars ({length * 100 / CHARACTER_LIMIT:.1f}%)"
        )


# ============================================================================
# Response Format Conversion
# ============================================================================


def format_response(
    data: dict[str, Any] | list[dict[str, Any]],
    response_format: ResponseFormat | str = ResponseFormat.MARKDOWN,
) -> str:
    """
    Convert data to specified format.

    Args:
        data: Data to format (dictionary or list of dictionaries)
        response_format: Output format ("json" or "markdown")

    Returns:
        Formatted string
    """
    # Normalize format parameter
    if isinstance(response_format, str):
        response_format = ResponseFormat(response_format.lower())

    if response_format == ResponseFormat.JSON:
        return format_as_json(data)
    else:  # MARKDOWN (default)
        return format_as_markdown(data)


def format_as_json(data: dict[str, Any] | list[dict[str, Any]]) -> str:
    """
    Format data as JSON.

    Args:
        data: Data to format

    Returns:
        JSON string (with indentation, readable)
    """
    return json.dumps(data, ensure_ascii=False, indent=2)


def format_as_markdown(data: dict[str, Any] | list[dict[str, Any]]) -> str:
    """
    Format data as Markdown.

    Args:
        data: Data to format (dictionary or list of dictionaries)

    Returns:
        Markdown format string
    """
    if isinstance(data, list):
        return _format_list_as_markdown(data)
    else:
        return _format_dict_as_markdown(data)


def _format_dict_as_markdown(data: dict[str, Any], level: int = 1) -> str:
    """
    Format a single dictionary as Markdown.

    Args:
        data: Dictionary data
        level: Header level

    Returns:
        Markdown string
    """
    lines = []

    # Handle special fields
    if "title" in data:
        header = "#" * level
        lines.append(f"{header} {data['title']}\n")

    for key, value in data.items():
        # Skip already processed fields
        if key == "title":
            continue

        # Format key (convert to human readable)
        display_key = key.replace("_", " ").title()

        if isinstance(value, dict):
            # Nested dictionary
            lines.append(f"\n**{display_key}**:")
            lines.append(_format_dict_as_markdown(value, level + 1))
        elif isinstance(value, list):
            # List
            lines.append(f"\n**{display_key}**:")
            if value and isinstance(value[0], dict):
                # List of dictionaries
                for item in value:
                    lines.append(_format_dict_as_markdown(item, level + 1))
            else:
                # Simple list
                for item in value:
                    lines.append(f"- {item}")
        elif value is None:
            # Null value
            lines.append(f"**{display_key}**: N/A")
        elif isinstance(value, bool):
            # Boolean value
            lines.append(f"**{display_key}**: {'Yes' if value else 'No'}")
        else:
            # Simple value
            lines.append(f"**{display_key}**: {value}")

    return "\n".join(lines)


def _format_list_as_markdown(items: list[dict[str, Any]]) -> str:
    """
    Format a list of dictionaries as Markdown.

    Args:
        items: List of dictionaries

    Returns:
        Markdown string
    """
    if not items:
        return "No results"

    lines = [f"## Search Results ({len(items)} items)\n"]

    for i, item in enumerate(items, 1):
        # Add item number
        lines.append(f"### {i}. {item.get('title', item.get('name', 'Item'))}\n")

        # Format item content
        lines.append(_format_dict_as_markdown(item, level=4))
        lines.append("\n---\n")  # Item separator

    return "\n".join(lines)


def format_search_results(
    results: list[dict[str, Any]],
    query: str = "",
    response_format: ResponseFormat | str = ResponseFormat.MARKDOWN,
    metadata: dict[str, Any] | None = None,
) -> str:
    """
    Format search results (supports dual format).

    Args:
        results: List of search results
        query: Search query
        response_format: Response format
        metadata: Additional metadata (e.g., total_count, has_more)

    Returns:
        Formatted string
    """
    # Normalize format parameter
    if isinstance(response_format, str):
        response_format = ResponseFormat(response_format.lower())

    # Prepare complete data structure
    data: dict[str, Any] = {
        "query": query,
        "count": len(results),
        "results": results,
    }

    # Add metadata
    if metadata:
        data.update(metadata)

    # Format
    if response_format == ResponseFormat.JSON:
        return format_as_json(data)
    else:  # MARKDOWN
        return _format_search_results_markdown(results, query, metadata or {})


def _format_search_results_markdown(
    results: list[dict[str, Any]],
    query: str,
    metadata: dict[str, Any],
) -> str:
    """
    Format search results as Markdown.

    Args:
        results: List of results
        query: Search query
        metadata: Metadata

    Returns:
        Markdown string
    """
    lines = []

    # Title
    if query:
        lines.append(f'# Search Results: "{query}"\n')
    else:
        lines.append("# Search Results\n")

    # Statistics
    lines.append(f"**Found**: {len(results)} items")

    # Metadata
    if "total_count" in metadata:
        lines.append(f"**Total**: {metadata['total_count']} items")
    if "has_more" in metadata and metadata["has_more"]:
        lines.append("**Hint**: More results available, use pagination parameters to view")

    lines.append("\n---\n")

    # Result items
    if not results:
        lines.append("*No matching results found*")
    else:
        for i, result in enumerate(results, 1):
            lines.append(f"## {i}. {result.get('title', result.get('name', 'Item'))}\n")

            # Content
            if "content" in result:
                content = result["content"]
                # Truncate long content
                if len(content) > 500:
                    content = content[:500] + "..."
                lines.append(f"{content}\n")

            # Other fields
            for key, value in result.items():
                if key in ("title", "name", "content"):
                    continue
                display_key = key.replace("_", " ").title()
                lines.append(f"**{display_key}**: {value}")

            lines.append("\n---\n")

    return "\n".join(lines)
