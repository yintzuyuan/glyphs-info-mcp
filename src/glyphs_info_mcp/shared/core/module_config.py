"""Module Configuration Data Models

Provides Pydantic data models for validating and parsing modules_config.yaml configuration files.
"""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ModuleConfig(BaseModel):
    """Configuration model for a single module"""

    # Basic info
    name: str = Field(..., description="Module name (e.g., 'handbook', 'api')")
    enabled: bool = Field(default=True, description="Whether to enable this module")

    # Module path configuration
    module_path: str = Field(..., description="Module directory relative path")
    python_file: str = Field(..., description="Python file relative path")
    class_name: str = Field(..., description="Module class name")

    # Optional configuration
    description: str = Field(default="", description="Module description")
    internal_service: bool = Field(default=False, description="Whether it's an internal service")
    register_to_search_engine: bool = Field(
        default=False, description="Whether to register to search engine"
    )
    search_types: list[str] = Field(default_factory=list, description="Search type labels")

    # Dependency configuration (future extension)
    dependencies: list[str] = Field(default_factory=list, description="Dependent modules")

    @field_validator("module_path", "python_file")
    @classmethod
    def validate_paths(cls, v: str) -> str:
        """Validate path format (must be relative path)"""
        if Path(v).is_absolute():
            raise ValueError(f"Path must be relative: {v}")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate module name (only letters, numbers, underscores, hyphens allowed)"""
        if not v or not v.replace("-", "_").replace("_", "").isalnum():
            raise ValueError(f"Invalid module name format: {v}")
        return v


class SearchEngineConfig(BaseModel):
    """Search engine configuration"""

    enabled: bool = Field(default=True, description="Whether to enable search engine")
    default_strategy: Literal["hybrid", "sequential", "parallel"] = Field(
        default="hybrid", description="Default search strategy"
    )
    max_results: int = Field(default=20, ge=1, le=100, description="Maximum search results")


class FeaturesConfig(BaseModel):
    """Feature toggle configuration"""

    plugin_templates: bool = Field(default=True, description="Plugin Templates feature")
    unified_prompts: bool = Field(default=True, description="Unified Prompts feature")
    character_limit: int = Field(
        default=25000,
        ge=1000,
        le=100000,
        description="CHARACTER_LIMIT character limit",
    )


class ServerConfig(BaseModel):
    """Complete server configuration"""

    modules: list[ModuleConfig] = Field(..., description="Module list")
    search_engine: SearchEngineConfig = Field(
        default_factory=SearchEngineConfig, description="Search engine configuration"
    )
    features: FeaturesConfig = Field(
        default_factory=FeaturesConfig, description="Feature toggle configuration"
    )

    # Server metadata
    server_name: str = Field(
        default="Glyphs info MCP - Modular Architecture", description="Server name"
    )
    server_description: str = Field(
        default="Unified MCP server", description="Server description"
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO", description="Log level"
    )

    @field_validator("modules")
    @classmethod
    def validate_unique_names(cls, modules: list[ModuleConfig]) -> list[ModuleConfig]:
        """Validate module name uniqueness"""
        names = [m.name for m in modules]
        if len(names) != len(set(names)):
            raise ValueError("Module names must be unique")
        return modules

    def get_enabled_modules(self) -> list[ModuleConfig]:
        """Get enabled modules

        Returns:
            List of enabled modules
        """
        return [m for m in self.modules if m.enabled]

    def get_internal_services(self) -> list[ModuleConfig]:
        """Get internal service modules

        Returns:
            List of enabled internal service modules
        """
        return [m for m in self.modules if m.internal_service and m.enabled]

    def get_public_modules(self) -> list[ModuleConfig]:
        """Get public tool modules

        Returns:
            List of enabled public modules (excluding internal services)
        """
        return [m for m in self.modules if not m.internal_service and m.enabled]
