#!/usr/bin/env python3
"""
Shared Interface Definitions - Unified standard interfaces for modules and tools
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


class ModuleInterface(ABC):
    """Module interface standard"""

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize module"""
        pass

    @abstractmethod
    def get_tools(self) -> dict[str, Any]:
        """Get module tools"""
        pass


@dataclass
class ToolInterface:
    """Tool interface standardized definition"""

    name: str
    description: str
    function: Callable
    parameters: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "name": self.name,
            "description": self.description,
            "function": self.function,
            "parameters": self.parameters or {},
        }


class ResourceInterface(ABC):
    """MCP resource interface"""

    @abstractmethod
    def get_resources(self) -> dict[str, Callable]:
        """Get MCP resources provided by module"""
        pass
