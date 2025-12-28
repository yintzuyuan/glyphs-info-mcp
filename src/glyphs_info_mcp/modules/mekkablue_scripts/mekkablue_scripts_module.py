"""
Mekkablue Scripts Module - mekkablue script collection code template management
Standalone module focused on searching and managing mekkablue production scripts
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
from glyphs_info_mcp.shared.core.mekkablue_scripts_accessor import MekkablueScriptsAccessor
from glyphs_info_mcp.shared.core.repository_scanner import RepositoryScanner

logger = logging.getLogger(__name__)


class MekkablueScriptsModule(BaseMCPModule):
    """Mekkablue Scripts Module - Manages mekkablue script collection code templates"""

    def __init__(self) -> None:
        super().__init__(name="mekkablue-scripts")
        self.description = "mekkablue script collection code template search and management"

        # Mekkablue Scripts Accessor
        self.accessor: MekkablueScriptsAccessor | None = None

    def initialize(self) -> bool:
        """
        Initialize the module

        Returns:
            Whether initialization was successful
        """
        try:
            # Set up Submodule fallback paths
            project_root = Path(__file__).parent.parent.parent
            fallback_paths = {
                "mekkablue": project_root / "data/official/mekkablue-scripts",
            }

            # Use RepositoryScanner to auto-detect mekkablue path
            repo_scanner = RepositoryScanner.auto_detect()
            if not repo_scanner:
                logger.warning(f"[{self.name}] Glyphs Repositories path not found")
                return False

            # Set fallback paths
            repo_scanner.fallback_paths = fallback_paths

            # Scan Repositories
            repo_scanner.scan_repositories()

            # Initialize Accessor
            self.accessor = MekkablueScriptsAccessor(repo_scanner)

            if not self.accessor.is_available():
                logger.warning(f"[{self.name}] mekkablue script collection not installed")
                return False

            # Statistics
            categories = self.accessor.list_categories()
            total_scripts = sum(
                len(self.accessor.get_category_scripts(cat)) for cat in categories
            )

            logger.info(
                f"[{self.name}] Initialization complete - {len(categories)} categories, {total_scripts} scripts"
            )
            self.is_initialized = True
            return True

        except Exception as e:
            logger.error(f"[{self.name}] Initialization failed: {e}")
            return False

    def core_search(self, query: str, max_results: int = 5, **kwargs: Any) -> list[dict[str, Any]]:
        """
        Core search function - For use by unified search engine

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of search results
        """
        if not self.is_initialized or not self.accessor:
            return []

        # Search using accessor
        results = self.accessor.search_scripts(query, max_results=max_results)

        # Convert to unified format
        unified_results = []
        for script in results:
            unified_results.append(
                {
                    "title": script["menu_title"],
                    "content": script["description"],
                    "type": "mekkablue_script",
                    "source": "mekkablue",
                    "score": script["score"],
                    "metadata": {
                        "script_id": script["script_id"],
                        "category": script["category"],
                        "filename": script["filename"],
                    },
                }
            )

        return unified_results

    def get_tools(self) -> dict[str, Any]:
        """
        Get MCP tool functions

        Returns:
            Dictionary of tool functions
        """
        return {
            "scripts_search": self._search_scripts_tool,
            "scripts_get": self._get_script_tool,
            "scripts_list_categories": self._list_categories_tool,
            "scripts_list": self._list_scripts_tool,
        }

    def _search_scripts_tool(
        self, query: str, category: str | None = None, max_results: int = 10
    ) -> str:
        """
        [MEKKABLUE SCRIPTS] Search mekkablue script collection code samples

        Purpose: Search for related code examples among 358 production scripts
        Data source: mekkablue Glyphs-Scripts official repository

        Complementary tools:
          - Use `snippets_search` for quick code snippet insertion
          - Use `api_get_python_class` to understand API specifications
          - Use `sdk_get_plugin_template` to get plugin architecture

        When to use:
        - Need complete feature implementation examples (e.g., batch anchor processing)
        - Learn best practices for specific features
        - Solve complex font design problems
        - Reference expert-level code patterns

        Args:
            query: Search keyword (e.g., "anchor", "kerning", "interpolation")
            category: Category filter (e.g., 'Anchors', 'Kerning'), optional
            max_results: Maximum number of results (default: 10)

        Returns:
            Formatted script search results
        """
        if not self.is_initialized or not self.accessor:
            return self._get_installation_message()

        if not query:
            return "Please provide a search keyword"

        # Execute search
        results = self.accessor.search_scripts(query, category, max_results)

        if not results:
            categories_hint = ""
            if not category:
                all_categories = self.accessor.list_categories()
                categories_hint = f"\n\nAvailable categories: {', '.join(all_categories[:10])}"
            return f"No scripts found matching '{query}'{categories_hint}"

        # Format results
        output = [f"## mekkablue Script Search Results: '{query}' ({len(results)} results)\n"]

        if category:
            output.append(f"**Category filter**: {category}\n")

        for i, script in enumerate(results, 1):
            relevance = "🎯" if script["score"] >= 0.8 else "✓"
            output.append(
                f"{relevance} **{i}. {script['menu_title']}** (`{script['script_id']}`)"
            )
            output.append(f"  **Category**: {script['category']}")

            # Show description (if available)
            if script["description"]:
                desc_preview = script["description"][:150]
                if len(script["description"]) > 150:
                    desc_preview += "..."
                output.append(f"  **Description**: {desc_preview}")

            output.append("")

        # Add related tool recommendations
        output.append("\n## 💡 Usage Tips")
        output.append(
            f"- Use `scripts_get('{results[0]['script_id']}')` to view complete code"
        )
        output.append("- Use `scripts_list_categories` to browse all categories")
        if not category:
            output.append(
                f"- Try searching within a category: `scripts_search(query='{query}', category='Anchors')`"
            )

        output.append("\n## 🔗 Complementary Tools")
        output.append("- `snippets_search` - Quick code snippets")
        output.append("- `api_get_python_class` - API documentation")
        output.append("- `sdk_get_plugin_template` - Plugin templates")

        return "\n".join(output)

    def _get_script_tool(self, script_id: str, include_source: bool = True) -> str:
        """
        [MEKKABLUE SCRIPTS] Get complete code and description of a specific script

        Features: Reads complete source code and documentation of mekkablue scripts
        Purpose: Deep learning of complete implementation, reference best practices

        Args:
            script_id: Script ID (format: category/filename, e.g., 'Anchors/Anchor Mover')
            include_source: Whether to include complete source code (default: True)

        Returns:
            Complete script information (MenuTitle, category, description, file path, source code)
        """
        if not self.is_initialized or not self.accessor:
            return self._get_installation_message()

        # Get script info
        script_info = self.accessor.get_script(script_id)

        if not script_info:
            # Provide suggestions
            all_categories = self.accessor.list_categories()
            return f"""
❌ Script not found: {script_id}

Script ID format: category/filename (without .py)
Example: Anchors/Anchor Mover

Available categories:
{', '.join(all_categories)}

Use `scripts_list_categories` to view all categories
Use `scripts_list(category='Anchors')` to list scripts in a specific category
"""

        # Format output
        output = [f"# {script_info['menu_title']}\n"]
        output.append(f"**Script ID**: `{script_info['script_id']}`")
        output.append(f"**Category**: {script_info['category']}")
        output.append(f"**Filename**: {script_info['filename']}")
        output.append(f"**Path**: `{script_info['file_path']}`\n")

        # Description
        if script_info["description"]:
            output.append("## 📝 Description\n")
            output.append(script_info["description"])
            output.append("")

        # Complete source code
        if include_source and "source" in script_info:
            source = script_info["source"]
            output.append("## 💻 Complete Source Code\n")
            output.append("```python")
            output.append(source)
            output.append("```")
        elif not include_source:
            output.append(
                "**Tip**: Use `scripts_get('{script_id}', include_source=True)` to view complete source code"
            )

        # Usage tips
        output.append("\n## 💡 Usage Tips")
        output.append("- This script can be executed directly from Glyphs' Script menu")
        output.append("- Copy the code snippets you need into your project")
        output.append(
            f"- View other scripts in the same category: `scripts_list(category='{script_info['category']}')`"
        )

        return "\n".join(output)

    def _list_categories_tool(self) -> str:
        """
        [MEKKABLUE SCRIPTS] List all script categories

        Features: Displays all 20 script categories with their script counts
        Purpose: Browse available script types, understand feature scope

        Returns:
            Formatted category list
        """
        if not self.is_initialized or not self.accessor:
            return self._get_installation_message()

        # Get categories
        categories = self.accessor.list_categories()

        if not categories:
            return "⚠️ No script categories found"

        # Category descriptions (main categories)
        category_descriptions = {
            "Anchors": "Anchor management - Batch processing, alignment, moving anchors",
            "Kerning": "Kerning adjustment - Auto kerning, grouping, anomaly detection",
            "Interpolation": "Interpolation - Instance generation, compatibility check",
            "Paths": "Path editing - Node operations, path conversion, outline processing",
            "Spacing": "Spacing settings - Auto spacing, sidebearing settings",
            "Components": "Component management - Component alignment, sync, conversion",
            "Font Info": "Font info - Metadata editing, parameter settings",
            "Build Glyphs": "Glyph building - Batch generation of variant glyphs",
            "Features": "OpenType features - Feature code generation and management",
            "Hinting": "Font hinting - TrueType hinting tools",
        }

        # Format output
        total_scripts = sum(
            len(self.accessor.get_category_scripts(cat)) for cat in categories
        )

        output = [
            f"## mekkablue Script Categories ({len(categories)} categories, {total_scripts} scripts total)\n"
        ]

        for cat in categories:
            scripts = self.accessor.get_category_scripts(cat)
            script_count = len(scripts)

            # Category header
            desc = category_descriptions.get(cat, "Other utility tools")
            output.append(f"### 📁 {cat} ({script_count} scripts)")
            output.append(f"**Description**: {desc}\n")

            # List first 3 scripts as examples
            for script in scripts[:3]:
                output.append(f"- **{script['menu_title']}** (`{script['script_id']}`)")

            if script_count > 3:
                output.append(f"  ... and {script_count - 3} more scripts\n")
            else:
                output.append("")

        # Usage instructions
        output.append("\n## 💡 How to Use")
        output.append("```python")
        output.append("# List all scripts in a specific category")
        output.append('scripts_list(category="Anchors")')
        output.append("")
        output.append("# Search scripts within a specific category")
        output.append('scripts_search(query="align", category="Anchors")')
        output.append("```")

        return "\n".join(output)

    def _list_scripts_tool(self, category: str | None = None) -> str:
        """
        [MEKKABLUE SCRIPTS] List scripts in a specified category

        Features: Lists all scripts in a specific category (or all categories)
        Purpose: Browse all available scripts in a specific category

        Args:
            category: Category name (e.g., 'Interpolation'), optional

        Returns:
            Formatted script list
        """
        if not self.is_initialized or not self.accessor:
            return self._get_installation_message()

        # Determine which categories to list
        if category:
            categories_to_list = (
                [category] if category in self.accessor.list_categories() else []
            )
            if not categories_to_list:
                all_categories = self.accessor.list_categories()
                return f"""
❌ Category not found: {category}

Available categories:
{', '.join(all_categories)}

Use `scripts_list_categories` to view all category details
"""
        else:
            categories_to_list = self.accessor.list_categories()

        # Format output
        output = []

        if category:
            output.append(f"## Scripts in {category} Category\n")
        else:
            total_scripts = sum(
                len(self.accessor.get_category_scripts(cat))
                for cat in categories_to_list
            )
            output.append(f"## All mekkablue Scripts ({total_scripts} scripts)\n")

        for cat in categories_to_list:
            scripts = self.accessor.get_category_scripts(cat)

            if not category:  # Show category header when listing all categories
                output.append(f"### 📁 {cat} ({len(scripts)} scripts)\n")

            for i, script in enumerate(scripts, 1):
                output.append(
                    f"{i}. **{script['menu_title']}** (`{script['script_id']}`)"
                )

                # Show brief description (if available)
                if script["description"]:
                    desc_preview = script["description"][:80]
                    if len(script["description"]) > 80:
                        desc_preview += "..."
                    output.append(f"   {desc_preview}")

                output.append("")

        # Next steps
        output.append("\n## 💡 Next Steps")
        if scripts:
            first_script_id = scripts[0]["script_id"]
            output.append(f"- View script details: `scripts_get('{first_script_id}')`")
        if not category:
            output.append("- Filter by category: `scripts_list(category='Anchors')`")
        output.append("- Search for specific scripts: `scripts_search(query='kerning')`")

        return "\n".join(output)

    def _get_installation_message(self) -> str:
        """Get installation message"""
        return """
⚠️  mekkablue script collection not installed

The mekkablue script collection contains 358 production Glyphs development scripts,
covering anchors, kerning, interpolation, paths and all aspects of font design.

Installation:
1. Open Glyphs 3
2. Go to Window > Plugin Manager
3. Switch to the Scripts tab
4. Find "mekkablue scripts" and click Install
5. Restart Glyphs (recommended)

Installation path:
~/Library/Application Support/Glyphs 3/Repositories/mekkablue

Online resources:
https://github.com/mekkablue/Glyphs-Scripts

Note: You need to restart this MCP server after installation.
"""

    def get_module_info(self) -> dict[str, Any]:
        """Get module info"""
        total_scripts = 0
        category_count = 0

        if self.is_initialized and self.accessor:
            categories = self.accessor.list_categories()
            category_count = len(categories)
            total_scripts = sum(
                len(self.accessor.get_category_scripts(cat)) for cat in categories
            )

        return {
            "name": self.name,
            "description": self.description,
            "version": "1.0.0",
            "type": "code_examples",
            "source": "mekkablue Glyphs-Scripts",
            "total_scripts": total_scripts,
            "categories": category_count,
            "capabilities": [
                "Script search",
                "Category browsing",
                "Complete source code reading",
                "Metadata extraction",
            ],
        }
