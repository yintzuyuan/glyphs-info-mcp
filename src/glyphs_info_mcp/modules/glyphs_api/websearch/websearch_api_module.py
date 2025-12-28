#!/usr/bin/env python3
"""
WebSearch API module for Vanilla UI framework
"""

import logging
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

# Use shared core library
# From modules/glyphs-api/src/modules/websearch/websearch_api_module.py to project root requires 6 levels
project_root = Path(__file__).parent.parent.parent.parent
shared_core_path = str(project_root / "src" / "shared")
if shared_core_path not in sys.path:
    sys.path.insert(0, shared_core_path)

from glyphs_info_mcp.shared.core.base_module import BaseMCPModule  # noqa: E402
from glyphs_info_mcp.shared.fetch.web_fetcher import WebFetcher  # noqa: E402

logger = logging.getLogger(__name__)


class WebSearchAPIModule(BaseMCPModule):
    """WebSearch API module for Vanilla UI framework"""

    def __init__(self, name: str = "websearch-api", data_path: Path | None = None):
        if data_path is None:
            # Get the module root directory (4 levels up from this file)
            module_root = Path(__file__).parent.parent.parent.parent
            data_path = module_root / "data"

        super().__init__(name, data_path)
        self.web_fetcher = WebFetcher()
        self._vanilla_items: set[str] = set()
        self._vanilla_search_index: dict[str, Any] = {}  # Vanilla UI search index data
        self.search_engine = None  # Will be injected by server.py

    def set_search_engine(self, search_engine: Any) -> None:
        """Set search engine (called by server.py)"""
        self.search_engine = search_engine

    def initialize(self) -> bool:
        """Initialize the websearch API module"""
        try:
            # Create data directory if it doesn't exist
            self.data_path.mkdir(parents=True, exist_ok=True)

            # Load Vanilla UI items
            self._load_vanilla_items()
            self._load_vanilla_search_index()

            self.is_initialized = True
            logger.info("WebSearch API module initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize websearch API module: {e}")
            return False


    def _load_vanilla_items(self) -> None:
        """Load Vanilla UI item list from official JSON file docnames"""
        index_file = self.data_path / "web_search" / "vanilla_ui_searchindex.json"
        if not index_file.exists():
            logger.warning(f"Official Vanilla UI index file not found: {index_file}")
            self._vanilla_items = set()
            return

        try:
            import json

            with open(index_file, encoding='utf-8') as f:
                data = json.load(f)

            docnames = data.get('docnames', [])
            self._vanilla_items = set()

            # Use only official docnames, do not add any extra items
            for docname in docnames:
                if docname.startswith('objects/'):
                    self._vanilla_items.add(docname)  # objects/Button
                    name_only = docname.split('/')[-1]
                    self._vanilla_items.add(name_only)  # Button

            logger.info(f"Loaded {len(self._vanilla_items)} official Vanilla UI items")

        except Exception as e:
            logger.error(f"Failed to load official Vanilla UI data: {e}")
            self._vanilla_items = set()


    def _load_vanilla_search_index(self) -> None:
        """Load Vanilla UI search index (from local file)"""
        try:
            import json

            # Use local search index file
            index_file = self.data_path / "web_search" / "vanilla_ui_searchindex.json"
            logger.info(f"Loading local Vanilla UI search index: {index_file}")

            if not index_file.exists():
                logger.warning(f"Local search index file not found: {index_file}")
                self._vanilla_search_index = {}
                return

            # Read local JSON file
            with open(index_file, encoding='utf-8') as f:
                search_data = json.load(f)

            # Extract searchable UI component information
            ui_components = {}

            # Extract document paths from docnames
            docnames = search_data.get('docnames', [])
            alltitles = search_data.get('alltitles', {})

            # Build component index
            for docname in docnames:
                if docname.startswith('objects/'):
                    # Extract component name
                    component_name = docname.split('/')[-1]

                    # Find corresponding title from alltitles
                    component_title = component_name
                    for title, refs in alltitles.items():
                        if any(ref[0] == docnames.index(docname) for ref in refs if ref[1] is None):
                            component_title = title
                            break

                    # Determine component category
                    category = self._categorize_ui_component(component_name)

                    ui_components[component_name] = {
                        'name': component_name,
                        'title': component_title,
                        'path': docname,
                        'category': category,
                        'url': f"https://vanilla.robotools.dev/en/latest/{docname}.html"
                    }

            # Add special items
            if 'concepts/positioning' in docnames:
                ui_components['concepts'] = {
                    'name': 'concepts',
                    'title': 'Core Concepts',
                    'path': 'concepts/positioning',
                    'category': 'Core',
                    'url': 'https://vanilla.robotools.dev/en/latest/concepts/positioning.html'
                }

            self._vanilla_search_index = ui_components
            logger.info(f"Loaded {len(ui_components)} Vanilla UI components into search index")

        except Exception as e:
            logger.error(f"Failed to load Vanilla UI search index: {e}")
            self._vanilla_search_index = {}

    def _categorize_ui_component(self, component_name: str) -> str:
        """Categorize component based on name"""
        component_lower = component_name.lower()

        # Window category
        if any(keyword in component_lower for keyword in ['window', 'sheet', 'drawer', 'modal']):
            return 'Windows'

        # Button category
        if any(keyword in component_lower for keyword in ['button']):
            return 'Buttons'

        # Input controls
        if any(keyword in component_lower for keyword in ['text', 'edit', 'search', 'date', 'color', 'slider', 'check', 'radio', 'combo', 'popup']):
            return 'Inputs'

        # Layout views
        if any(keyword in component_lower for keyword in ['group', 'tabs', 'scroll', 'split', 'box', 'stack', 'grid']):
            return 'Layout Views'

        # Data views
        if any(keyword in component_lower for keyword in ['list', 'image', 'level']):
            return 'Data Views'

        # Progress indicators
        if any(keyword in component_lower for keyword in ['progress']):
            return 'Progress Indicators'

        # Navigation
        if any(keyword in component_lower for keyword in ['path']):
            return 'Navigation'

        # Separators
        if any(keyword in component_lower for keyword in ['line']):
            return 'Layout Views'

        # Other popup views
        if any(keyword in component_lower for keyword in ['popover']):
            return 'Layout Views'

        return 'General'


    def _normalize_vanilla_item(self, vanilla_item: str) -> str | None:
        """Normalize and validate Vanilla UI item name (preserve exact case)

        Args:
            vanilla_item: Original Vanilla UI item name

        Returns:
            Normalized Vanilla UI item path, or None if invalid
        """
        if not self._vanilla_items:
            return None

        # Remove possible .html extension
        vanilla_item = vanilla_item.replace('.html', '')

        # Exact match (preserve case)
        if vanilla_item in self._vanilla_items:
            # If it's a full path, return directly
            if '/' in vanilla_item:
                return vanilla_item

            # If it's just a name, try to find the full path (exact case match)
            for item in self._vanilla_items:
                if '/' in item and item.endswith('/' + vanilla_item):
                    return item

        # If exact match fails, try case-insensitive match but return correct case version
        vanilla_item_lower = vanilla_item.lower()
        for item in self._vanilla_items:
            if item.lower() == vanilla_item_lower:
                if '/' in item:
                    return item
            elif '/' in item and item.split('/')[-1].lower() == vanilla_item_lower:
                return item

        return None





    def get_tools(self) -> dict[str, Callable]:
        """Get available tools as dictionary

        Wrap async bound methods into standalone async functions to ensure FastMCP/MCP clients
        correctly handle async calls. This fixes the issue where coroutine objects were not
        properly awaited.
        """
        # Wrap async bound methods into standalone async functions
        async def search_vanilla_ui_wrapper(query: str, max_results: int = 5) -> str:
            return await self.search_vanilla_ui(query, max_results)

        async def fetch_vanilla_ui_doc_wrapper(
            ui_item: str, max_length: int = 5000, raw_html: bool = False
        ) -> str:
            return await self.fetch_vanilla_ui_doc(ui_item, max_length, raw_html)

        return {
            'api_search_vanilla_ui': search_vanilla_ui_wrapper,
            'api_get_vanilla_ui': fetch_vanilla_ui_doc_wrapper
        }




    async def _fetch_component_summary(self, component_info: dict) -> str:
        """Fetch component summary, mimicking official website search result format

        Args:
            component_info: Component info dict containing name, url, etc.

        Returns:
            Formatted summary text, limited to 120-150 characters
        """
        try:
            import re

            # Fetch first section of component page content
            content, _ = await self.web_fetcher.fetch_url(component_info['url'])

            if '<error>' in content:
                return "Description not available."

            # Remove Markdown formatting, get plain text
            clean_content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)  # Remove links
            clean_content = re.sub(r'[*_`]', '', clean_content)  # Remove formatting symbols
            clean_content = re.sub(r'\n+', ' ', clean_content)  # Merge newlines

            # Find class definition
            class_pattern = rf'class\s+vanilla\.{component_info["name"]}\s*\([^)]*\)'
            class_match = re.search(class_pattern, clean_content, re.IGNORECASE)

            # Find description text (usually first sentence after class definition)
            desc_patterns = [
                r':\s*([A-Z][^.]+\.)',  # Description after colon
                r'.*?([A-Z][a-z]+(?:\s+[a-z]+)*\s+(?:control|widget|view|button|text|window)[^.]*\.)',  # Description with keywords
                r'([A-Z][^.]+\.)',  # Any sentence starting with uppercase
            ]

            description = ""
            for pattern in desc_patterns:
                desc_match = re.search(pattern, clean_content)
                if desc_match:
                    description = desc_match.group(1).strip()
                    break

            # Find import statement
            import_pattern = r'from\s+vanilla\s+import[^.]*'
            import_match = re.search(import_pattern, clean_content)

            # Combine summary
            summary_parts = []

            if description:
                summary_parts.append(description)

            if class_match:
                class_def = class_match.group(0)
                # Shorten parameter list
                if len(class_def) > 60:
                    class_def = class_def[:57] + "...)"
                summary_parts.append(class_def)

            if import_match:
                import_statement = import_match.group(0)
                if len(import_statement) > 40:
                    import_statement = import_statement[:37] + "..."
                summary_parts.append(import_statement)

            # Combine and control length
            summary = " ".join(summary_parts)

            # Ensure not exceeding 150 characters
            if len(summary) > 150:
                summary = summary[:147] + "..."

            return summary if summary else "UI component documentation available."

        except Exception as e:
            logger.debug(f"Failed to fetch summary for {component_info['name']}: {e}")
            return "Description not available."

    async def search_vanilla_ui(self, query: str, max_results: int = 5) -> str:
        """
        🔍 **Vanilla UI Search Tool** Search available UI components and controls

        📌 **When to use**: Use this tool first to discover available UI components, then use api_get_vanilla_ui for specific content

        Args:
            query: Search keyword (English, e.g., "button", "text", "window")
            max_results: Maximum number of results (default 10)

        Returns:
            List of matching UI components for subsequent selection
        """
        if not self.is_initialized:
            return "WebSearch API module not initialized"

        if not query.strip():
            return "Please provide a search keyword"

        if not self._vanilla_search_index:
            return "Vanilla UI search index not loaded, please try again later"

        # Use term processor for preprocessing and postprocessing
        if self.search_engine and self.search_engine.query_processor:
            processed_query, user_language = self.search_engine.query_processor.preprocess_query(query)
            query_lower = processed_query.lower().strip()
        else:
            query_lower = query.lower().strip()
            user_language = 'en'

        matches = []

        # Match in search index
        for component_name, component_info in self._vanilla_search_index.items():
            # Calculate match score
            score = 0
            component_name_lower = component_name.lower()
            component_title_lower = component_info['title'].lower()
            component_category_lower = component_info['category'].lower()

            # Exact match gets highest score
            if query_lower == component_name_lower:
                score += 10
            elif query_lower in component_name_lower:
                score += 5

            # Title match
            if query_lower in component_title_lower:
                score += 3

            # Category match
            if query_lower in component_category_lower:
                score += 2

            # Fuzzy match: keyword contains
            if any(word in component_name_lower for word in query_lower.split()):
                score += 1

            if score > 0:
                matches.append({
                    'name': component_info['name'],
                    'title': component_info['title'],
                    'path': component_info['path'],
                    'category': component_info['category'],
                    'url': component_info['url'],
                    'score': score
                })

        if not matches:
            # Provide search suggestions
            all_components = list(self._vanilla_search_index.keys())
            suggestions = []
            for comp in all_components:
                if any(part in comp.lower() for part in query_lower.split() if len(part) > 1):
                    suggestions.append(comp)

            suggestion_text = ""
            if suggestions:
                suggestion_text = "\n\nSimilar components:\n" + "\n".join(f"- {s}" for s in suggestions[:10])

            return f"""No UI components found matching '{query}'

Available main categories:
- Windows
- Buttons
- Inputs
- Layout Views
- Data Views
- Progress Indicators

Suggestions:
- Try using more general keywords (e.g., "button", "text", "window")
- Use English keywords for search{suggestion_text}"""

        # Sort by score and limit results
        matches.sort(key=lambda x: x['score'], reverse=True)
        matches = matches[:max_results]

        # Fetch summaries in parallel
        import asyncio

        async def fetch_match_with_summary(match: dict[str, Any]) -> dict[str, Any]:
            summary = await self._fetch_component_summary(match)
            match['summary'] = summary
            return match

        try:
            # Limit concurrency to avoid overload
            semaphore = asyncio.Semaphore(5)

            async def fetch_with_semaphore(match: dict[str, Any]) -> dict[str, Any]:
                async with semaphore:
                    return await fetch_match_with_summary(match)

            # Fetch all summaries in parallel
            matches_with_summaries = await asyncio.gather(
                *[fetch_with_semaphore(match) for match in matches],
                return_exceptions=True
            )

            # Filter exception results
            processed_matches: list[dict[str, Any]] = []
            for gather_result in matches_with_summaries:
                if isinstance(gather_result, dict):
                    processed_matches.append(gather_result)
                else:
                    # If summary fetch failed, use original match with default summary
                    match_index = matches_with_summaries.index(gather_result)
                    if match_index < len(matches):
                        matches[match_index]['summary'] = "Description not available."
                        processed_matches.append(matches[match_index])

            matches = processed_matches

        except Exception as e:
            logger.warning(f"Failed to fetch summaries: {e}")
            # If parallel fetch failed, add default summary to all matches
            for match in matches:
                match['summary'] = "Description not available."

        # Format output (with summaries)
        result_lines = [f"# 🔍 Found {len(matches)} matching UI components"]
        result_lines.append(f"**Search keyword:** {query}\n")

        for i, match in enumerate(matches, 1):
            result_lines.append(f"## {i}. {match['name']}")
            result_lines.append(f"**Full path:** `{match['path']}`")
            result_lines.append(f"**Category:** {match['category']}")
            result_lines.append(f"**Summary:** {match.get('summary', 'Description not available.')}")
            result_lines.append(f"**URL:** {match['url']}")
            result_lines.append("")

        result_lines.append("---")
        result_lines.append("**Next step:** Use `api_get_vanilla_ui` tool to get the complete documentation for specific components")

        result = "\n".join(result_lines)

        # Use term processor for postprocessing
        if self.search_engine and self.search_engine.query_processor:
            return self.search_engine.query_processor.postprocess_output(result, user_language)
        else:
            return result

    async def fetch_vanilla_ui_doc(self, ui_item: str, max_length: int = 5000, raw_html: bool = False) -> str:
        """
        📄 **Vanilla UI Document Fetch Tool** Fetch complete official documentation for specified UI component

        📌 **When to use**: After selecting a specific component from api_search_vanilla_ui results, use this tool to get complete content

        Args:
            ui_item: UI component name (e.g., "Button", "objects/Window", "TextBox")
            max_length: Content length limit (default 5000 characters)
            raw_html: Whether to return raw HTML (default False, returns Markdown)

        Returns:
            Complete UI component documentation content
        """
        if not self.is_initialized:
            return "WebSearch API module not initialized"

        if not ui_item.strip():
            return "Please provide a UI component name (e.g., Button, Window, TextBox)"

        # Normalize and validate UI item name
        normalized_item = self._normalize_vanilla_item(ui_item)
        if not normalized_item:
            # Suggest using search tool
            available_items = []
            if self._vanilla_search_index:
                available_items = sorted(self._vanilla_search_index.keys())[:10]
            else:
                available_items = sorted([item for item in self._vanilla_items if '/' in item])[:10]

            return f"""Vanilla UI component not found: {ui_item}

Available UI component examples:
{chr(10).join(available_items)}

**Suggestion**: Use `api_search_vanilla_ui` tool first to search for related components:
Example: api_search_vanilla_ui("button") or api_search_vanilla_ui("text")"""

        # Build complete URL
        vanilla_url = f"https://vanilla.robotools.dev/en/latest/{normalized_item}.html"

        try:
            # Fetch content
            content, prefix = await self.web_fetcher.fetch_url(vanilla_url, force_raw=raw_html)

            # Handle content length limit
            if len(content) > max_length:
                content = content[:max_length]
                content += f"\n\n<truncated>Content truncated, visit for full content: {vanilla_url}</truncated>"

            response = f"""{prefix}Vanilla UI Document: {normalized_item}
Source: {vanilla_url}

{content}"""

            # Use term processor for postprocessing
            if self.search_engine and self.search_engine.query_processor:
                # Detect user language (infer from ui_item, or default to Chinese)
                user_language = self.search_engine.query_processor.detect_user_language(  # type: ignore[attr-defined]
                    ui_item
                )
                return self.search_engine.query_processor.postprocess_output(response, user_language)
            else:
                return response

        except Exception as e:
            logger.error(f"Failed to fetch Vanilla UI document {vanilla_url}: {e}")
            return f"""Failed to fetch Vanilla UI document: {e}

Attempted URL: {vanilla_url}
Suggestion: Please check network connection or try again later, or use `api_search_vanilla_ui` tool first to confirm component name"""

    def get_module_info(self) -> dict[str, Any]:
        """Get module information"""
        return {
            'name': self.name,
            'type': 'websearch-api',
            'title': 'WebSearch API Module',
            'description': 'Vanilla UI framework documentation fetching and search',
            'initialized': self.is_initialized,
            'vanilla_items_count': len(self._vanilla_items) if self._vanilla_items else 0,
            'tools': ['api_search_vanilla_ui', 'api_get_vanilla_ui']
        }

    def get_resources(self) -> dict[str, Any]:
        """Get MCP resources provided by this module"""
        return {
            "websearch-api://guide": self._websearch_api_guide_resource
        }

    def _websearch_api_guide_resource(self) -> str:
        """WebSearch API Guide - Modular API documentation fetching"""
        vanilla_count = len(self._vanilla_items) if self._vanilla_items else 0

        return f"""Glyphs WebSearch API Module - Vanilla UI Document Search System

Core Feature: Provides complete document query and retrieval for Vanilla UI framework

Main Domain:
- Vanilla UI: https://vanilla.robotools.dev/en/latest/

## 🔧 Tool Set

### 1. api_search_vanilla_ui - Vanilla UI Search Tool
- **Function**: Search available Vanilla UI components and controls ({vanilla_count} components)
- **Purpose**: Provide UI component overview for AI to select specific components
- **Output**: List of matching UI components with name, category, URL

### 2. api_get_vanilla_ui - Vanilla UI Document Fetch Tool
- **Function**: Fetch complete official documentation for specified UI component
- **Purpose**: Get complete UI component reference for interface development
- **Output**: Complete UI component documentation, not truncated

## 🚀 Typical Usage Flow

### Vanilla UI Workflow
1. **Search Phase**: Use api_search_vanilla_ui to find related UI components
2. **Fetch Phase**: Use api_get_vanilla_ui to get specific component documentation

## 💡 Design Advantages
- **Specialized**: Focused on Vanilla UI framework documentation
- **On-demand**: AI can selectively invoke as needed
- **Complete Content**: All UI development references provide full content
- **Efficient Search**: Precise search based on official index
"""
