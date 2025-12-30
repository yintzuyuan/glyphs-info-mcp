#!/usr/bin/env python3
# encoding: utf-8
"""
Glyphs MCP Server - Modular Architecture
Combines all three independent modules: vocabulary, handbook, and api

Supports two modes:
- Legacy mode (UNIFIED_TOOLS=false): Exposes all 60 individual tools
- Unified mode (UNIFIED_TOOLS=true): Exposes 8 unified entry points (default)
"""

import os
import sys
import asyncio
import logging
import yaml
from pathlib import Path
from typing import Any

from glyphs_info_mcp.shared.core.base_module import BaseMCPModule
from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

from glyphs_info_mcp.config import MODULES_CONFIG, MODULES_DIR

# Configuration: Use unified tools by default (reduces context token cost by ~85%)
USE_UNIFIED_TOOLS = os.environ.get("UNIFIED_TOOLS", "true").lower() == "true"

# Setup logger - Must output to stderr because MCP stdio transport uses stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stderr  # Critical: MCP protocol requires stdout to only contain JSON
)
logger = logging.getLogger(__name__)

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as e:
    print(f"❌ Failed to import FastMCP: {e}", file=sys.stderr)
    sys.exit(1)

# Dynamic module loading
def load_module_configs() -> list[tuple[Path, str]]:
    """Load module configuration from modules_config.yaml

    Returns:
        List of (module_path, module_name) tuples
    """
    try:
        with open(MODULES_CONFIG, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        module_configs = []

        for module in config['modules']:
            # Check if module is enabled (defaults to True)
            if not module.get('enabled', True):
                logger.info(f"⏭️  Skipping disabled module: {module['name']}")
                continue

            module_path = MODULES_DIR / module['directory']
            module_configs.append((module_path, module['name']))

        logger.info(f"✅ Loaded {len(module_configs)} module configs from YAML")
        return module_configs

    except Exception as e:
        logger.error(f"❌ Failed to load modules_config.yaml: {e}")
        logger.warning("⚠️  Falling back to hardcoded module list")
        # Fallback to original hardcoded list
        return [
            (MODULES_DIR / "glyphs_vocabulary", "vocabulary"),
            (MODULES_DIR / "glyphs_handbook", "handbook"),
            (MODULES_DIR / "glyphs_api", "api")
        ]

def import_module(module_path: Path, module_name: str) -> BaseMCPModule | None:
    """Dynamically import a module

    Supports two module structures:
    1. Legacy: glyphs-vocabulary/src/vocabulary_module.py
    2. New: glyphs_plugins/glyphs_plugins_module.py

    Args:
        module_path: Module directory path
        module_name: Module name

    Returns:
        Module instance or None
    """
    paths_to_add: list[str] = []
    try:
        # Add module path to sys.path
        src_path = str(module_path / "src")
        module_root = str(module_path)
        if (module_path / "src").exists():
            paths_to_add.append(src_path)
        paths_to_add.append(module_root)

        for path in paths_to_add:
            if path not in sys.path:
                sys.path.insert(0, path)

        # Dynamically import module
        module_instance: BaseMCPModule | None = None

        # Use absolute imports to load modules from package
        if module_name == "vocabulary":
            from glyphs_info_mcp.modules.glyphs_vocabulary.vocabulary.vocabulary_module import VocabularyModule
            module_instance = VocabularyModule()
        elif module_name == "handbook":
            from glyphs_info_mcp.modules.glyphs_handbook.handbook.unified_handbook_module import UnifiedHandbookModule
            module_instance = UnifiedHandbookModule()
        elif module_name == "api":
            from glyphs_info_mcp.modules.glyphs_api.unified_api_module import UnifiedAPIModule
            module_instance = UnifiedAPIModule()
        elif module_name == "glyphs_plugins":
            from glyphs_info_mcp.modules.glyphs_plugins.glyphs_plugins_module import GlyphsPluginsModule
            module_instance = GlyphsPluginsModule()
        elif module_name == "glyphs_news":
            from glyphs_info_mcp.modules.glyphs_news.glyphs_news.glyphs_news_module import GlyphsNewsModule
            module_instance = GlyphsNewsModule()
        elif module_name == "glyphs_sdk":
            from glyphs_info_mcp.modules.glyphs_sdk.glyphs_sdk_module import GlyphsSDKModule
            module_instance = GlyphsSDKModule()
        elif module_name == "light_table_api":
            from glyphs_info_mcp.modules.light_table_api.light_table_module import LightTableModule
            module_instance = LightTableModule()
        elif module_name == "mekkablue_scripts":
            from glyphs_info_mcp.modules.mekkablue_scripts.mekkablue_scripts_module import MekkablueScriptsModule
            module_instance = MekkablueScriptsModule()
        else:
            # Attempt auto-discovery for unknown modules
            logger.warning(f"⚠️  Unknown module: {module_name}, attempting auto-discovery")
            module_file = module_path / f"{module_name}_module.py"
            if module_file.exists():
                import importlib.util
                spec = importlib.util.spec_from_file_location(f"{module_name}_module", module_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    # Try to find module class
                    class_name = ''.join(word.capitalize() for word in module_name.split('_')) + 'Module'
                    if hasattr(module, class_name):
                        module_instance = getattr(module, class_name)()

        if module_instance is None:
            logger.error(f"❌ Failed to instantiate {module_name} module")

        return module_instance

    except ImportError as e:
        logger.error(f"❌ Failed to import {module_name} module: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        # Clean up sys.path
        for path in paths_to_add:
            if path in sys.path:
                sys.path.remove(path)

# Create FastMCP instance
mcp = FastMCP("Glyphs MCP - Modular Architecture")

# Global variables for modules
_modules: dict[str, BaseMCPModule] = {}


def main() -> None:
    """Initialize and start the unified MCP server"""
    try:
        # Load module configurations from YAML
        module_configs = load_module_configs()

        # Initialize all modules
        modules = {}
        total_tools = 0

        # Create unified tools router if using unified mode
        router = UnifiedToolsRouter() if USE_UNIFIED_TOOLS else None

        for module_path, module_name in module_configs:
            if not module_path.exists():
                logger.error(f"Module directory not found: {module_path}")
                continue

            module = import_module(module_path, module_name)
            if module is None:
                logger.error(f"Failed to load {module_name} module")
                continue

            # Initialize the module
            if not module.initialize():
                logger.error(f"Failed to initialize {module_name} module")
                continue

            modules[module_name] = module
            # Update global modules for resource access
            _modules[module_name] = module

            # Register module with router if using unified mode
            if router is not None:
                router.set_module(module_name, module)

            # In legacy mode, register individual tools
            if not USE_UNIFIED_TOOLS:
                for tool_name, tool_func in module.get_tools().items():
                    mcp.tool(name=tool_name)(tool_func)
                    total_tools += 1

            logger.info(f"✅ {module_name.title()} module loaded successfully")

        if not modules:
            logger.error("No modules loaded successfully")
            sys.exit(1)

        # In unified mode, register unified entry points
        if USE_UNIFIED_TOOLS and router is not None:
            for tool_name, tool_func in router.get_tools().items():
                mcp.tool(name=tool_name)(tool_func)
                total_tools += 1
            logger.info(f"✅ Unified tools mode: 8 entry points registered (60 tools consolidated)")

        mode_str = "unified" if USE_UNIFIED_TOOLS else "legacy"
        logger.info(f"✅ Glyphs MCP Server initialized ({mode_str} mode) with {len(modules)} modules and {total_tools} tools")

        # Start the FastMCP server with STDIO transport (for Claude Desktop)
        mcp.run(transport="stdio")

    except Exception as e:
        logger.error(f"❌ Failed to initialize Unified MCP Server: {e}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

# This allows the module to be used as a script or imported
if __name__ == "__main__":
    main()