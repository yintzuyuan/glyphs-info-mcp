"""
Light Table API Module - Light Table Python API query and documentation management
Standalone module focused on Light Table version control plugin API reference
"""

import logging
import sys
from pathlib import Path
from typing import Any

# Add shared core module path
shared_path = str(Path(__file__).parent.parent.parent / "src" / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from glyphs_info_mcp.shared.core.base_module import BaseMCPModule
from glyphs_info_mcp.shared.core.repository_scanner import RepositoryScanner

# Add accessor path
accessor_path = str(Path(__file__).parent / "accessors")
if accessor_path not in sys.path:
    sys.path.insert(0, accessor_path)

from light_table_native_accessor import LightTableNativeAccessor

logger = logging.getLogger(__name__)


class LightTableModule(BaseMCPModule):
    """Light Table API Module - Manages Light Table Python API reference"""

    def __init__(self) -> None:
        super().__init__(name="light-table-api")
        self.description = "Light Table Python API query and documentation management"

        # Light Table Native Accessor
        self.accessor: LightTableNativeAccessor | None = None

    def initialize(self) -> bool:
        """
        Initialize module

        Returns:
            Whether initialization was successful
        """
        try:
            # Set Submodule fallback paths
            # Note: Using repo_name "Light-Table" from official plugin list as search keyword
            project_root = Path(__file__).parent.parent.parent
            fallback_paths = {
                "Light-Table": project_root / "data/official/light-table",
            }

            # Use RepositoryScanner to auto-detect Light Table path
            repo_scanner = RepositoryScanner.auto_detect()
            if not repo_scanner:
                logger.warning(f"[{self.name}] Glyphs Repositories path not found")
                # Try using fallback path directly
                repo_scanner = RepositoryScanner(
                    Path.home()
                    / "Library/Application Support/Glyphs 3/Repositories",
                    fallback_paths,
                )

            # Set fallback paths
            repo_scanner.fallback_paths = fallback_paths

            # Scan Repositories
            repo_scanner.scan_repositories()

            # Initialize Accessor
            self.accessor = LightTableNativeAccessor(repo_scanner)

            if not self.accessor.is_available():
                logger.warning(f"[{self.name}] Light Table API not found")
                return False

            # Parse API
            self.accessor.parse_api()

            # Statistics
            enums = self.accessor.get_enums()
            all_items = self.accessor.list_all()

            logger.info(
                f"[{self.name}] Initialization complete - {len(enums)} enums, {len(all_items)} API items total"
            )
            self.is_initialized = True
            return True

        except Exception as e:
            logger.error(f"[{self.name}] Initialization failed: {e}")
            return False

    def get_module_info(self) -> dict[str, Any]:
        """Get module information"""
        enum_count = 0
        total_items = 0

        if self.is_initialized and self.accessor:
            enums = self.accessor.get_enums()
            all_items = self.accessor.list_all()
            enum_count = len(enums)
            total_items = len(all_items)

        return {
            "name": self.name,
            "description": self.description,
            "version": "1.0.0",
            "status": "active" if self.is_initialized else "inactive",
            "data_source": "Light Table Python API (Submodule)",
            "statistics": {
                "total_api_items": total_items,
                "enums": enum_count,
                "classes": total_items - enum_count,
            },
        }

    def core_search(self, query: str, max_results: int = 5, **kwargs: Any) -> list[dict[str, Any]]:
        """
        Core search functionality - for unified search engine

        Args:
            query: Search query
            max_results: Maximum result count

        Returns:
            Search results list
        """
        if not self.is_initialized or not self.accessor:
            return []

        # Use accessor to search
        results = self.accessor.search(query)[:max_results]

        # Convert to unified format
        unified_results = []
        for item in results:
            unified_results.append(
                {
                    "title": item["name"],
                    "content": item.get("docstring", "No documentation"),
                    "type": "light_table_api",
                    "source": "light-table",
                    "score": 1.0,  # Default score
                    "metadata": {
                        "api_type": item["type"],
                        "values": item.get("values", {}),
                    },
                }
            )

        return unified_results

    def get_tools(self) -> dict[str, Any]:
        """
        Get MCP tool functions

        Returns:
            Tool function dictionary
        """
        return {
            "lighttable_search_api": self._search_api_tool,
            "lighttable_get_enum": self._get_enum_tool,
            "lighttable_list_enums": self._list_enums_tool,
            "lighttable_list_all": self._list_all_tool,
        }

    def _search_api_tool(self, query: str, max_results: int = 10) -> str:
        """
        [LIGHT TABLE API] Search Light Table Python API

        Purpose: Query API definitions for Light Table version control plugin
        Data source: Light Table official Python API

        Complementary tools:
          - Use `api_get_python_class` to understand GSFont/GSGlyph/GSLayer base API
          - Use `scripts_search` to view actual usage examples

        When to use:
        - Need to understand version control features provided by Light Table
        - Querying enum values (DocumentState, ObjectStatus, etc.)
        - Understanding version restore operation APIs

        Args:
          query: Search keyword (e.g., "DocumentState", "restore", "commit")
          max_results: Maximum number of results (default: 10)

        Returns:
            Formatted API search results
        """
        if not self.is_initialized or not self.accessor:
            return "❌ Light Table module not initialized"

        try:
            results = self.accessor.search(query)[:max_results]

            if not results:
                return f"No API found related to '{query}'"

            # Format results
            output = f"## Light Table API Search Results: {query}\n\n"
            output += f"Found {len(results)} related items:\n\n"

            for idx, item in enumerate(results, 1):
                output += f"### {idx}. {item['name']} ({item['type']})\n"

                if item.get("docstring"):
                    output += f"**Description**: {item['docstring']}\n"

                if item["type"] == "enum" and item.get("values"):
                    output += f"**Enum Values**: {list(item['values'].keys())}\n"

                output += "\n"

            return output

        except Exception as e:
            logger.error(f"Failed to search API: {e}")
            return f"❌ Search failed: {e}"

    def _get_enum_tool(self, enum_name: str) -> str:
        """
        [LIGHT TABLE API] Get enum detailed information

        Purpose: Queries complete definition and values of Light Table enum types

        Args:
          enum_name: Enum name (e.g., "DocumentState", "ObjectStatus", "ComponentIntegrationStrategy")

        Returns:
            Complete enum definition and description
        """
        if not self.is_initialized or not self.accessor:
            return "❌ Light Table module not initialized"

        try:
            enum_info = self.accessor.get_enum_details(enum_name)

            if not enum_info:
                return f"❌ Enum not found: {enum_name}"

            # Format output
            output = f"## {enum_name} Enum\n\n"

            if enum_info.get("docstring"):
                output += f"**Description**: {enum_info['docstring']}\n\n"

            output += "**Enum Values**:\n\n"
            for name, value in enum_info["values"].items():
                output += f"- `{name}` = {value}\n"

            return output

        except Exception as e:
            logger.error(f"Failed to get enum: {e}")
            return f"❌ Get failed: {e}"

    def _list_enums_tool(self) -> str:
        """
        [LIGHT TABLE API] List all enum types

        Purpose: Lists all available enums in Light Table API

        Returns:
            List of all enums
        """
        if not self.is_initialized or not self.accessor:
            return "❌ Light Table module not initialized"

        try:
            enums = self.accessor.get_enums()

            if not enums:
                return "❌ No enums found"

            output = f"## Light Table API Enum List\n\n"
            output += f"Total {len(enums)} enums:\n\n"

            for name, info in enums.items():
                output += f"### {name}\n"
                if info.get("docstring"):
                    output += f"{info['docstring']}\n"
                output += f"Enum Values: {list(info['values'].keys())}\n\n"

            return output

        except Exception as e:
            logger.error(f"Failed to list enums: {e}")
            return f"❌ List failed: {e}"

    def _list_all_tool(self) -> str:
        """
        [LIGHT TABLE API] List all API items

        Purpose: Views complete content overview of Light Table API

        Returns:
            List of all API items (enums, classes, etc.)
        """
        if not self.is_initialized or not self.accessor:
            return "❌ Light Table module not initialized"

        try:
            all_items = self.accessor.list_all()

            if not all_items:
                return "❌ No API items found"

            # Group by type
            by_type: dict[str, list[str]] = {}
            for item in all_items:
                item_type = item["type"]
                if item_type not in by_type:
                    by_type[item_type] = []
                by_type[item_type].append(item["name"])

            output = f"## Light Table API Complete List\n\n"
            output += f"Total {len(all_items)} API items:\n\n"

            for item_type, names in by_type.items():
                output += f"### {item_type.upper()} ({len(names)})\n"
                output += ", ".join(sorted(names)) + "\n\n"

            return output

        except Exception as e:
            logger.error(f"Failed to list API items: {e}")
            return f"❌ List failed: {e}"
