#!/usr/bin/env python3
"""
MCP Unified Error Handling System
Provides LLM-friendly, actionable error messages
"""

import logging
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """Error category classification"""

    # Input errors
    INVALID_INPUT = "invalid_input"
    MISSING_PARAMETER = "missing_parameter"
    PARAMETER_OUT_OF_RANGE = "parameter_out_of_range"

    # Resource errors
    RESOURCE_NOT_FOUND = "resource_not_found"
    RESOURCE_UNAVAILABLE = "resource_unavailable"
    RESOURCE_EXHAUSTED = "resource_exhausted"

    # External service errors
    NETWORK_ERROR = "network_error"
    TIMEOUT_ERROR = "timeout_error"
    API_ERROR = "api_error"

    # System errors
    INITIALIZATION_ERROR = "initialization_error"
    INTERNAL_ERROR = "internal_error"
    NOT_IMPLEMENTED = "not_implemented"


class MCPError(Exception):
    """MCP standard error base class

    Provides structured error information including:
    - Error category
    - User-friendly message
    - Specific action suggestions
    - Related context
    """

    def __init__(
        self,
        message: str,
        category: ErrorCategory,
        suggestions: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ):
        """Initialize MCP error

        Args:
            message: User-friendly error message
            category: Error category
            suggestions: List of specific action suggestions
            context: Related context information (no sensitive data)
        """
        super().__init__(message)
        self.message = message
        self.category = category
        self.suggestions = suggestions or []
        self.context = context or {}

    def to_user_message(self) -> str:
        """Convert to user-friendly complete error message

        Returns:
            Formatted error message with suggestions and context
        """
        lines = [f"❌ {self.message}"]

        if self.suggestions:
            lines.append("\n💡 Suggested actions:")
            for i, suggestion in enumerate(self.suggestions, 1):
                lines.append(f"   {i}. {suggestion}")

        if self.context:
            lines.append("\n📋 Related information:")
            for key, value in self.context.items():
                lines.append(f"   - {key}: {value}")

        return "\n".join(lines)

    def __str__(self) -> str:
        return self.to_user_message()


class ErrorHandler:
    """Unified error handler

    Provides standardized handling methods for common error scenarios
    """

    @staticmethod
    def handle_not_found(
        resource_type: str,
        resource_id: str,
        available_alternatives: list[str] | None = None,
        search_tool: str | None = None,
    ) -> MCPError:
        """Handle resource not found error

        Args:
            resource_type: Resource type (e.g., "class", "method", "script")
            resource_id: Resource identifier
            available_alternatives: Available alternative options
            search_tool: Suggested search tool name

        Returns:
            Formatted MCPError
        """
        message = f"{resource_type} not found: '{resource_id}'"

        suggestions = []

        # Suggest search tool
        if search_tool:
            suggestions.append(f"Use {search_tool} to search for related {resource_type}")

        # Suggest checking spelling
        suggestions.append(f"Check if '{resource_id}' spelling is correct")

        # Provide alternative options
        if available_alternatives:
            suggestions.append(
                f"See similar options: {', '.join(available_alternatives[:5])}"
            )

        context: dict[str, Any] = {
            "resource_type": resource_type,
            "searched_id": resource_id,
        }

        if available_alternatives:
            context["alternatives_count"] = len(available_alternatives)

        return MCPError(
            message=message,
            category=ErrorCategory.RESOURCE_NOT_FOUND,
            suggestions=suggestions,
            context=context,
        )

    @staticmethod
    def handle_invalid_parameter(
        parameter_name: str,
        provided_value: Any,
        valid_range: str | None = None,
        valid_options: list[str] | None = None,
    ) -> MCPError:
        """Handle invalid parameter error

        Args:
            parameter_name: Parameter name
            provided_value: Provided invalid value
            valid_range: Valid range description
            valid_options: Valid option list

        Returns:
            Formatted MCPError
        """
        message = f"Invalid value for parameter '{parameter_name}': '{provided_value}'"

        suggestions = []

        if valid_range:
            suggestions.append(f"Please use a value within {valid_range}")

        if valid_options:
            if len(valid_options) <= 5:
                suggestions.append(f"Valid options: {', '.join(valid_options)}")
            else:
                suggestions.append(
                    f"Valid options include: {', '.join(valid_options[:5])} and {len(valid_options)} more"
                )

        context: dict[str, Any] = {
            "parameter": parameter_name,
            "provided_value": str(provided_value),
        }

        if valid_range:
            context["valid_range"] = valid_range
        if valid_options:
            context["valid_options_count"] = len(valid_options)

        return MCPError(
            message=message,
            category=ErrorCategory.INVALID_INPUT,
            suggestions=suggestions,
            context=context,
        )

    @staticmethod
    def handle_too_many_results(
        result_count: int,
        limit: int,
        filter_suggestions: list[str] | None = None,
    ) -> MCPError:
        """Handle too many results error

        Args:
            result_count: Actual result count
            limit: Character or item limit
            filter_suggestions: Filter suggestion list

        Returns:
            Formatted MCPError
        """
        message = f"Too many search results ({result_count}), exceeds limit ({limit})"

        suggestions = [
            "Use more specific search keywords to narrow scope",
            "Process results in batches, fewer items at a time",
        ]

        if filter_suggestions:
            suggestions.extend(filter_suggestions)

        context = {
            "result_count": result_count,
            "limit": limit,
            "overflow_percentage": f"{(result_count / limit - 1) * 100:.1f}%",
        }

        return MCPError(
            message=message,
            category=ErrorCategory.RESOURCE_EXHAUSTED,
            suggestions=suggestions,
            context=context,
        )

    @staticmethod
    def handle_network_error(
        operation: str,
        url: str | None = None,
        error_details: str | None = None,
    ) -> MCPError:
        """Handle network error

        Args:
            operation: Operation description
            url: Target URL (optional)
            error_details: Error details (optional, no sensitive info)

        Returns:
            Formatted MCPError
        """
        message = f"Network request failed: {operation}"

        suggestions = [
            "Check if network connection is working",
            "Try again later",
            "If problem persists, try using local data source",
        ]

        context = {"operation": operation}

        if url:
            # Only show domain, not full URL (may contain sensitive info)
            from urllib.parse import urlparse

            parsed = urlparse(url)
            context["domain"] = parsed.netloc

        if error_details:
            # Clean sensitive info
            safe_details = error_details.replace(url or "", "[URL]")
            context["error_type"] = safe_details[:100]  # Limit length

        return MCPError(
            message=message,
            category=ErrorCategory.NETWORK_ERROR,
            suggestions=suggestions,
            context=context,
        )

    @staticmethod
    def handle_initialization_error(
        module_name: str, reason: str, fix_suggestions: list[str] | None = None
    ) -> MCPError:
        """Handle initialization error

        Args:
            module_name: Module name
            reason: Failure reason
            fix_suggestions: Fix suggestions

        Returns:
            Formatted MCPError
        """
        message = f"Module '{module_name}' initialization failed: {reason}"

        suggestions = fix_suggestions or [
            "Check if required data files exist",
            "Confirm module dependencies are properly installed",
            "Check logs for more details",
        ]

        context = {
            "module": module_name,
            "reason": reason,
        }

        return MCPError(
            message=message,
            category=ErrorCategory.INITIALIZATION_ERROR,
            suggestions=suggestions,
            context=context,
        )

    @staticmethod
    def handle_timeout(
        operation: str, timeout_seconds: int, reduce_scope_tips: list[str] | None = None
    ) -> MCPError:
        """Handle timeout error

        Args:
            operation: Operation being performed
            timeout_seconds: Timeout in seconds
            reduce_scope_tips: Tips for reducing scope

        Returns:
            Formatted MCPError
        """
        message = f"Operation timed out: {operation} (exceeded {timeout_seconds} seconds)"

        suggestions = [
            "Narrow search scope or reduce requested data volume",
            "Check network connection speed",
            "Try again later",
        ]

        if reduce_scope_tips:
            suggestions.extend(reduce_scope_tips)

        context = {
            "operation": operation,
            "timeout_seconds": timeout_seconds,
        }

        return MCPError(
            message=message,
            category=ErrorCategory.TIMEOUT_ERROR,
            suggestions=suggestions,
            context=context,
        )


def safe_error_message(error: Exception, operation: str = "operation") -> str:
    """Convert any exception to a safe user message

    Args:
        error: Original exception
        operation: Operation description

    Returns:
        Safe error message (no internal details leaked)
    """
    if isinstance(error, MCPError):
        return error.to_user_message()

    # For non-MCPError, provide generic error message
    error_type = type(error).__name__
    logger.error(f"{operation} failed: {error_type}: {str(error)}")

    # Don't leak full exception message to user
    return f"❌ Error occurred during {operation}\n\n💡 Suggested actions:\n   1. Check if input parameters are correct\n   2. Try again later\n   3. If problem persists, check logs for detailed information"


# Common error shortcut methods
def not_found_error(resource_type: str, resource_id: str, **kwargs: Any) -> MCPError:
    """Shortcut method: Resource not found"""
    return ErrorHandler.handle_not_found(resource_type, resource_id, **kwargs)


def invalid_param_error(param_name: str, value: Any, **kwargs: Any) -> MCPError:
    """Shortcut method: Invalid parameter"""
    return ErrorHandler.handle_invalid_parameter(param_name, value, **kwargs)


def too_many_results_error(count: int, limit: int, **kwargs: Any) -> MCPError:
    """Shortcut method: Too many results"""
    return ErrorHandler.handle_too_many_results(count, limit, **kwargs)


def network_error(operation: str, **kwargs: Any) -> MCPError:
    """Shortcut method: Network error"""
    return ErrorHandler.handle_network_error(operation, **kwargs)


def init_error(module_name: str, reason: str, **kwargs: Any) -> MCPError:
    """Shortcut method: Initialization error"""
    return ErrorHandler.handle_initialization_error(module_name, reason, **kwargs)


def timeout_error(operation: str, seconds: int, **kwargs: Any) -> MCPError:
    """Shortcut method: Timeout error"""
    return ErrorHandler.handle_timeout(operation, seconds, **kwargs)
