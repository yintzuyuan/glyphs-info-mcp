# src/glyphs_info_mcp/config.py
"""Path management module for Glyphs Info MCP.

This module provides centralized path management for:
- Package-internal static data (SDK, handbook cache)
- User data directories (cache, indexes)
- External data sources (Glyphs app, Repositories)
"""

import logging
import os
from functools import cache
from pathlib import Path

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


# =============================================================================
# Module Filter Configuration (Issue #29)
# =============================================================================

logger = logging.getLogger(__name__)

ENABLED_MODULES_ENV = "GLYPHS_ENABLED_MODULES"
"""Environment variable for whitelist (only enable these modules)."""

DISABLED_MODULES_ENV = "GLYPHS_DISABLED_MODULES"
"""Environment variable for blacklist (disable these modules)."""

VALID_MODULE_NAMES: set[str] = {
    "vocabulary",
    "handbook",
    "api",
    "glyphs_plugins",
    "glyphs_news",
    "glyphs_sdk",
    "light_table_api",
    "mekkablue_scripts",
}
"""All valid module names."""

# Track if we've already logged the whitelist precedence warning
_whitelist_precedence_logged = False


def parse_module_list(env_value: str) -> set[str]:
    """Parse comma-separated module list from environment variable.

    Args:
        env_value: Comma-separated module names (e.g., "handbook,api,vocabulary")

    Returns:
        Set of valid module names. Invalid names are logged as warnings and ignored.
    """
    if not env_value or not env_value.strip():
        return set()

    modules: set[str] = set()
    invalid_names: list[str] = []

    for name in env_value.split(","):
        name = name.strip()
        if not name:
            continue

        if name in VALID_MODULE_NAMES:
            modules.add(name)
        else:
            invalid_names.append(name)

    if invalid_names:
        logger.warning(
            f"Unknown module names: {', '.join(invalid_names)}. "
            f"Valid names: {', '.join(sorted(VALID_MODULE_NAMES))}"
        )

    return modules


def is_module_enabled(module_name: str) -> bool:
    """Check if a module should be enabled based on environment variables.

    Logic:
    - If whitelist is set: only modules in whitelist are enabled
    - If only blacklist is set: modules not in blacklist are enabled
    - If neither is set: all modules are enabled
    - Whitelist takes precedence over blacklist

    Args:
        module_name: The module name to check

    Returns:
        True if the module should be enabled, False otherwise
    """
    global _whitelist_precedence_logged

    # Invalid module names are always disabled
    if module_name not in VALID_MODULE_NAMES:
        return False

    whitelist_env = os.getenv(ENABLED_MODULES_ENV, "")
    blacklist_env = os.getenv(DISABLED_MODULES_ENV, "")

    whitelist = parse_module_list(whitelist_env)
    blacklist = parse_module_list(blacklist_env)

    # Case 1: Whitelist is set (takes precedence)
    if whitelist:
        if blacklist and not _whitelist_precedence_logged:
            logger.info(
                f"Both {ENABLED_MODULES_ENV} and {DISABLED_MODULES_ENV} are set. "
                f"Using whitelist (enabled modules), blacklist will be ignored."
            )
            _whitelist_precedence_logged = True
        return module_name in whitelist

    # Case 2: Only blacklist is set
    if blacklist:
        return module_name not in blacklist

    # Case 3: Neither is set - all modules enabled
    return True

