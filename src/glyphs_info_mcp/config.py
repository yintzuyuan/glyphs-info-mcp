# src/glyphs_info_mcp/config.py
"""Path management module for Glyphs Info MCP.

This module provides centralized path management for:
- Package-internal static data (SDK, handbook cache)
- User data directories (cache, indexes)
- External data sources (Glyphs app, Repositories)
"""

from functools import cache
from pathlib import Path
import os

import platformdirs

# =============================================================================
# Package Internal Paths (Static data bundled with the package)
# =============================================================================

PACKAGE_ROOT = Path(__file__).parent
"""Root directory of the glyphs_info_mcp package."""

PACKAGE_DATA_DIR = PACKAGE_ROOT / "data"
"""Static data directory bundled with the package."""

MODULES_DIR = PACKAGE_ROOT / "modules"
"""MCP modules directory."""

SHARED_DIR = PACKAGE_ROOT / "shared"
"""Shared utilities directory."""

MODULES_CONFIG = PACKAGE_ROOT / "modules_config.yaml"
"""Modules configuration file path."""


# =============================================================================
# User Data Directories (platformdirs-based)
# =============================================================================

APP_NAME = "glyphs-info-mcp"
"""Application name for platformdirs."""


@cache
def get_user_data_dir() -> Path:
    """Get user data directory for persistent data.

    Returns:
        Path to user data directory (e.g., ~/Library/Application Support/glyphs-info-mcp on macOS)
    """
    data_dir = Path(platformdirs.user_data_dir(APP_NAME))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


@cache
def get_cache_dir() -> Path:
    """Get cache directory for temporary data.

    Returns:
        Path to cache directory (e.g., ~/Library/Caches/glyphs-info-mcp on macOS)
    """
    cache_dir = Path(platformdirs.user_cache_dir(APP_NAME))
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


# =============================================================================
# External Data Sources (Glyphs App and Plugin Manager)
# =============================================================================

@cache
def get_glyphs_app_path() -> Path | None:
    """Get Glyphs 3 application path.

    Returns:
        Path to Glyphs 3.app or None if not found
    """
    # Allow override via environment variable
    env_path = os.getenv("GLYPHS_APP_PATH")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path

    # Default path
    default_path = Path("/Applications/Glyphs 3.app")
    if default_path.exists():
        return default_path

    return None


@cache
def get_glyphs_headers_path() -> Path | None:
    """Get Glyphs Objective-C headers path.

    Returns:
        Path to GlyphsCore.framework/Headers or None if not found
    """
    # Allow override via environment variable
    env_path = os.getenv("GLYPHS_APP_HEADERS_PATH")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path

    # Default path within Glyphs app
    app_path = get_glyphs_app_path()
    if app_path:
        headers_path = (
            app_path / "Contents" / "Frameworks" / "GlyphsCore.framework"
            / "Versions" / "A" / "Headers"
        )
        if headers_path.exists():
            return headers_path

    return None


@cache
def get_glyphs_resources_path() -> Path | None:
    """Get Glyphs app resources path (for vocabulary .strings files).

    Returns:
        Path to Glyphs 3.app/Contents/Resources or None if not found
    """
    app_path = get_glyphs_app_path()
    if app_path:
        resources_path = app_path / "Contents" / "Resources"
        if resources_path.exists():
            return resources_path

    return None


@cache
def get_repositories_path() -> Path | None:
    """Get Glyphs Repositories path (plugins, scripts installed via Plugin Manager).

    All plugins and scripts are installed here, then symlinked to Plugins/ and Scripts/.

    Returns:
        Path to ~/Library/Application Support/Glyphs 3/Repositories or None if not found
    """
    # Allow override via environment variable
    env_path = os.getenv("GLYPHS_REPOSITORIES_PATH")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path

    # Default path
    default_path = Path.home() / "Library" / "Application Support" / "Glyphs 3" / "Repositories"
    if default_path.exists():
        return default_path

    return None


@cache
def get_plugins_path() -> Path | None:
    """Get Glyphs plugins path.

    Returns:
        Path to ~/Library/Application Support/Glyphs 3/Plugins or None if not found
    """
    default_path = Path.home() / "Library" / "Application Support" / "Glyphs 3" / "Plugins"
    if default_path.exists():
        return default_path

    return None


# =============================================================================
# Package Static Data Accessors
# =============================================================================

def get_sdk_path() -> Path:
    """Get bundled GlyphsSDK path.

    Returns:
        Path to bundled GlyphsSDK directory
    """
    return PACKAGE_DATA_DIR / "official" / "GlyphsSDK"


def get_handbook_cache_path() -> Path:
    """Get bundled handbook cache path.

    Returns:
        Path to bundled handbook cache directory
    """
    return PACKAGE_DATA_DIR / "handbook-cache" / "stable"

