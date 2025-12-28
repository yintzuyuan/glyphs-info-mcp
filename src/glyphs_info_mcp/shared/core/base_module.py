#!/usr/bin/env python3
"""
Shared Base Module Class - Unified foundation for all MCP modules
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from glyphs_info_mcp.shared.core.search_engine import SearchEngine

logger = logging.getLogger(__name__)


class BaseMCPModule(ABC):
    """MCP Module Base Class - Common interface for all modules

    Refactored base class supports:
    1. Unified search engine injection
    2. Standardized core search functionality
    3. Backward compatible tool interface
    """

    def __init__(self, name: str, data_path: Path | None = None) -> None:
        self.name = name
        self.data_path = data_path or Path(__file__).parent.parent / "data"
        self.tools: list[dict[str, Any]] = []
        self.is_initialized = False
        self.search_engine: "SearchEngine | None" = None

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize module and load data"""
        pass

    @abstractmethod
    def get_tools(self) -> dict[str, Any]:
        """Get tools provided by module"""
        pass

    def set_search_engine(self, search_engine: "SearchEngine") -> None:
        """Set unified search engine (called by server.py)

        Args:
            search_engine: Unified search engine instance
        """
        self.search_engine = search_engine
        logger.debug(f"Unified search engine injected into {self.name} module")

    def core_search(
        self, query: str, max_results: int = 5, **kwargs: Any
    ) -> list[dict[str, Any]]:
        """Core search functionality - Standardized search interface

        All modules should implement this method, providing structured search results for unified search engine

        Args:
            query: Search query (preprocessed)
            max_results: Maximum number of results
            **kwargs: Other search parameters

        Returns:
            List of structured search results, each containing:
            - title: Title
            - content: Content
            - source: Source module name
            - score: Relevance score (0.0-1.0)
            - type: Result type (optional)
            - Other module-specific fields
        """
        # Default implementation: return empty results
        logger.warning(f"Module {self.name} has not implemented core_search method")
        return []

    @abstractmethod
    def get_module_info(self) -> dict[str, Any]:
        """Get module info"""
        pass

    def validate_data_path(self) -> bool:
        """Validate data path exists"""
        if not self.data_path.exists():
            logger.error(f"Data path does not exist: {self.data_path}")
            return False
        return True

    def get_data_file(self, filename: str) -> Path:
        """Get data file path"""
        return self.data_path / filename

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"
