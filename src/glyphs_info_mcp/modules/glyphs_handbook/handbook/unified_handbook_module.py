#!/usr/bin/env python3
"""
Unified Handbook module for Glyphs.app documentation
Combines functionality from handbook and handbook_search modules
"""

import logging
import sys
from pathlib import Path
from typing import Any, Callable

# Use shared core library
project_root = Path(__file__).parent.parent.parent.parent
shared_core_path = str(project_root / "src" / "shared")
if shared_core_path not in sys.path:
    sys.path.insert(0, shared_core_path)

# Use absolute imports to avoid relative import issues
import importlib.util
from pathlib import Path

from glyphs_info_mcp.shared.core.base_module import BaseMCPModule
from glyphs_info_mcp.shared.core.scoring_weights import SearchLimits

logger = logging.getLogger(__name__)


def _dynamic_import(file_path: Path, module_name: str, class_name: str) -> type[Any]:
    """Dynamically import a class from a file"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, class_name)


# Dynamically import search module
search_file = Path(__file__).parent / "search.py"
HandbookSearcher: type[Any] = _dynamic_import(search_file, "search", "HandbookSearcher")

# Dynamically import HandbookCacheManager
cache_manager_file = Path(__file__).parent / "handbook_cache_manager.py"
HandbookCacheManager: type[Any] = _dynamic_import(
    cache_manager_file, "handbook_cache_manager", "HandbookCacheManager"
)

# Try to import enhanced searcher
ENHANCED_SEARCH_AVAILABLE = False
EnhancedHandbookSearcher: type[Any] | None = None
try:
    enhanced_search_file = Path(__file__).parent / "enhanced_search.py"
    if enhanced_search_file.exists():
        EnhancedHandbookSearcher = _dynamic_import(
            enhanced_search_file, "enhanced_search", "EnhancedHandbookSearcher"
        )
        ENHANCED_SEARCH_AVAILABLE = True
except ImportError:
    logger.warning("Enhanced search not available, using basic search")


class UnifiedHandbookModule(BaseMCPModule):
    """Unified Handbook documentation module"""

    def __init__(self, name: str = "handbook", data_path: Path | None = None):
        if data_path is None:
            # Read from project root's data/official/handbook
            project_root = Path(__file__).parent.parent.parent.parent
            data_path = project_root / "data" / "official"

        super().__init__(name, data_path)
        self.handbook_files: list[dict[str, str]] = []
        self.use_enhanced_search = ENHANCED_SEARCH_AVAILABLE

        # Initialize cache manager
        self.cache_manager: Any = HandbookCacheManager(
            project_root=Path(__file__).parent.parent.parent.parent
        )

    def set_search_engine(self, search_engine: Any) -> None:
        """Set unified search engine (called by server.py)"""
        self.search_engine = search_engine

    def initialize(self) -> bool:
        """Initialize the handbook module"""
        try:
            # Use cache manager to determine handbook path
            handbook_path = self.cache_manager.get_active_cache_path()

            if not handbook_path.exists():
                logger.error(f"Handbook directory not found: {handbook_path}")
                logger.error(
                    "Please run 'uv run python scripts/generate_stable_cache.py' "
                    "to generate stable cache"
                )
                return False

            logger.info(f"Using Handbook path: {handbook_path}")

            # Initialize searcher
            if self.use_enhanced_search and EnhancedHandbookSearcher is not None:
                logger.info("Using enhanced searcher")
                self.searcher = EnhancedHandbookSearcher(handbook_path)
            else:
                logger.info("Using basic searcher")
                self.searcher = HandbookSearcher(handbook_path)

            # Vocabulary processing moved to unified VocabularyModule service
            # Vocabulary conversion provided through SearchEngine

            self._load_handbook_files(handbook_path)
            self.is_initialized = True
            logger.info(
                f"Handbook module initialized with {len(self.handbook_files)} files"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to initialize handbook module: {e}")
            return False

    def core_search(
        self, query: str, max_results: int = SearchLimits.DEFAULT_MAX_RESULTS, **kwargs: Any
    ) -> list[dict[str, Any]]:
        """Core search function - for unified search engine use only

        Returns structured search results without vocabulary processing or formatting

        Args:
            query: Search query (pre-processed)
            max_results: Maximum number of results

        Returns:
            List of structured search results
        """
        if not self.is_initialized:
            return []

        results = []

        try:
            # Use internal search engine
            search_result = self._unified_search(query, max_results)

            if search_result and search_result.strip():
                # Convert string result to structured result
                # Can perform more detailed parsing based on actual result format
                results.append(
                    {
                        "title": f"Handbook search: {query}",
                        "content": search_result,
                        "source": "handbook",
                        "score": 0.8,  # Default score
                        "type": "handbook_content",
                    }
                )

                # If possible, try to extract specific chapter information
                chapter_results = self._extract_chapter_info(search_result, query)
                results.extend(chapter_results)

        except Exception as e:
            logger.error(f"Handbook core search failed: {e}")

        return results[:max_results]

    def _extract_chapter_info(
        self, search_result: str, query: str
    ) -> list[dict[str, Any]]:
        """Extract chapter information from search results"""
        # ChapterFinder removed, this method no longer extracts chapter info
        return []

    def _load_handbook_files(self, handbook_path: Path) -> None:
        """Load handbook files"""
        try:
            self.handbook_files = []
            for file_path in handbook_path.glob("*.md"):
                if file_path.name != "index.md":  # Skip index file
                    self.handbook_files.append(
                        {
                            "name": file_path.name,
                            "path": str(file_path),
                            "title": self._extract_title(file_path),
                        }
                    )

        except Exception as e:
            logger.error(f"Failed to load handbook files: {e}")

    def _extract_title(self, file_path: Path) -> str:
        """Extract title from markdown file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                first_line = f.readline().strip()
                if first_line.startswith("# "):
                    return first_line[2:].strip()
                return file_path.stem.replace("_", " ").title()
        except Exception:
            return file_path.stem.replace("_", " ").title()

    def get_tools(self) -> dict[str, Callable[..., Any]]:
        """Get available tools as dictionary"""

        # Wrap async method as standalone function (consistent with News/API modules)
        async def update_cache_wrapper(force: bool = False) -> str:
            return await self.update_cache(force)

        return {
            # Main tools
            "handbook_search_content": self.handbook_search,
            "handbook_get_content": self.handbook_fetch,
            # Custom Parameters specific tools
            "handbook_get_custom_parameter": self.fetch_custom_parameter,
            "handbook_list_parameters": self.get_custom_parameters_list,
            # TOC structure tools (Issue #17)
            "handbook_get_toc": self.get_toc,
            "handbook_get_chapter_children": self.get_chapter_children,
            # Cache management tools
            "handbook_update_cache": update_cache_wrapper,
            "handbook_get_cache_info": self.get_cache_info,
        }

    def handbook_search(
        self, query: str, search_scope: str = "all", max_results: int = SearchLimits.DEFAULT_MAX_RESULTS
    ) -> str:
        """
        [HANDBOOK] Search Glyphs handbook for related content

        Features:
        1. Smart relevance scoring: title match > paragraph match > content match
        2. Multi-term search: supports compound queries like "interpolation master"
        3. Search scope control: search titles, content, or all
        4. 70% match threshold: ensures search precision

        Args:
            query: Search keywords
            search_scope: Search scope ('titles', 'content', 'all')
            max_results: Maximum number of results (default: 5)

        Returns:
            Smart-formatted handbook search results
        """
        if not self.is_initialized:
            return "Handbook module not initialized"

        # Prefer enhanced searcher (new feature)
        if self.use_enhanced_search and hasattr(self, "searcher"):
            # Directly use enhanced searcher's smart search functionality
            return self.searcher.search(query, search_scope, max_results)

        # If unified search engine available, delegate to it
        elif self.search_engine:
            return self.search_engine.search(
                query,
                sources=["handbook"],
                max_results=max_results,
                formatter_type="handbook",
            )
        else:
            # Fall back to legacy search (backward compatibility)
            logger.warning("Using legacy search engine, recommend upgrading to enhanced search")
            return self._unified_search(query, max_results)

    def handbook_fetch(self, filename: str) -> str:
        """
        [HANDBOOK] Fetch complete Handbook content by filename

        Supports intelligent content handling:
        - Regular chapters: complete content loading
        - Custom Parameters: smart segmentation to avoid overly long content
        - Automatic content cleanup and formatting

        Args:
            filename: Filename (e.g., "anchors.md")
                     .md extension can be omitted
                     Legacy "handbook_glyphsapp_com_" prefix is auto-removed

        Returns:
            Complete file content or intelligently segmented content

        Examples:
            handbook_fetch("anchors")
            handbook_fetch("custom_parameters")
            handbook_fetch("anchors.md")
        """
        if not self.is_initialized:
            return "Handbook module not initialized"

        # Use term processor for post-processing
        result = self._smart_fetch_content(filename)

        if self.search_engine and self.search_engine.query_processor:
            # Detect user language (inferred from filename, or default to Chinese)
            user_language = self.search_engine.query_processor.detect_user_language(  # type: ignore[attr-defined]
                filename
            )
            return self.search_engine.query_processor.postprocess_output(
                result, user_language
            )
        else:
            return result

    def _search_handbook(self, query: str, max_results: int) -> str:
        """Search handbook content"""
        try:
            # Use the configured searcher
            result = self.searcher.search(query)

            # Search result processing unified, no fallback search needed

            return result

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return f"Search error: {str(e)}"

    def get_module_info(self) -> dict[str, Any]:
        """Get module information"""
        return {
            "name": self.name,
            "type": "handbook",
            "title": "📖 Handbook Module",
            "description": "Official Glyphs.app handbook and documentation search",
            "initialized": self.is_initialized,
            "files_count": len(self.handbook_files),
            "search_type": "enhanced" if self.use_enhanced_search else "basic",
            "tools": [
                "handbook_search_content",
                "handbook_get_content",
                "handbook_get_custom_parameter",
                "handbook_list_parameters",
                "handbook_get_toc",
                "handbook_get_chapter_children",
                "handbook_update_cache",
                "handbook_get_cache_info",
            ],
        }

    def get_resources(self) -> dict[str, Any]:
        """Get MCP resources provided by this module"""
        return {}

    def get_toc(self, chapter: str = "") -> str:
        """
        [HANDBOOK] Get Handbook table of contents

        Returns top-level chapters by default (~170 tokens).
        Specify a chapter name to expand that section with its children.

        Args:
            chapter: Optional chapter name to expand (partial match supported)

        Returns:
            Formatted TOC structure or error message

        Examples:
            get_toc()                    # Top-level chapters only
            get_toc("Interpolation")     # Expand Interpolation section
            get_toc("Edit View")         # Expand Edit View section
        """
        if not self.is_initialized:
            return "Handbook module not initialized"

        try:
            toc_data = self.cache_manager.load_toc_structure()

            if not toc_data:
                return (
                    "❌ TOC structure not found.\n\n"
                    "💡 The cache may need to be regenerated with TOC support.\n"
                    "Run `handbook_update_cache(force=True)` to regenerate."
                )

            chapters = toc_data.get("chapters", [])

            # If chapter specified, show focused view
            if chapter:
                return self._format_focused_toc(chapters, chapter)

            # Default: show top-level summary only
            return self._format_top_level_toc(chapters)

        except Exception as e:
            logger.error(f"Failed to get TOC: {e}")
            return f"❌ Failed to get TOC: {str(e)}"

    def _format_top_level_toc(self, chapters: list[dict]) -> str:
        """Format top-level chapters only (compact view)"""
        lines = ["# Handbook TOC (18 chapters)\n"]

        for ch in chapters:
            title = ch.get("title", "Unknown")
            file = ch.get("file", "")
            children_count = len(ch.get("children", []))

            if children_count > 0:
                lines.append(f"- {title} ({file}) [{children_count} sub]")
            else:
                lines.append(f"- {title} ({file})")

        lines.append("\n💡 Use `handbook_get_toc(chapter)` to expand a section")
        return "\n".join(lines)

    def _format_focused_toc(self, chapters: list[dict], target: str) -> str:
        """Format TOC focused on a specific chapter with context"""
        target_lower = target.lower()

        # Find the target chapter and its index (top-level only)
        target_idx = -1
        target_chapter = None
        for i, ch in enumerate(chapters):
            if target_lower in ch.get("title", "").lower():
                target_idx = i
                target_chapter = ch
                break

        if target_chapter is None:
            # Use recursive search for nested chapters
            matches = self._find_chapters_by_title(chapters, target)
            if matches:
                # Find parent context for the first match
                match = matches[0]
                parent = self._find_parent_chapter(chapters, match)
                if parent:
                    return self._format_chapter_with_children(parent, target)
                # Match is a deeply nested entry without clear parent context
                return self._format_matched_entry(match, target)
            return f"❌ No chapter found matching '{target}'"

        lines = [f"# TOC: {target_chapter['title']}\n"]

        # Show previous chapter (context)
        if target_idx > 0:
            prev = chapters[target_idx - 1]
            lines.append(f"← {prev['title']} ({prev.get('file', '')})")

        # Show target chapter with full children
        lines.append(f"\n**{target_chapter['title']}** ({target_chapter.get('file', '')})")
        for child in target_chapter.get("children", []):
            child_title = child.get("title", "")
            child_file = child.get("file", "")
            grandchildren = child.get("children", [])
            if grandchildren:
                lines.append(f"  - {child_title} ({child_file}) [{len(grandchildren)} sub]")
            else:
                lines.append(f"  - {child_title} ({child_file})")

        # Show next chapter (context)
        if target_idx < len(chapters) - 1:
            next_ch = chapters[target_idx + 1]
            lines.append(f"\n→ {next_ch['title']} ({next_ch.get('file', '')})")

        return "\n".join(lines)

    def _format_chapter_with_children(self, chapter: dict, highlight: str) -> str:
        """Format a chapter with its children, highlighting the target"""
        highlight_lower = highlight.lower()
        lines = [f"# TOC: {chapter['title']}\n"]
        lines.append(f"**{chapter['title']}** ({chapter.get('file', '')})")

        for child in chapter.get("children", []):
            child_title = child.get("title", "")
            child_file = child.get("file", "")
            grandchildren = child.get("children", [])

            # Highlight matching child
            if highlight_lower in child_title.lower():
                if grandchildren:
                    lines.append(f"  → **{child_title}** ({child_file}) [{len(grandchildren)} sub]")
                else:
                    lines.append(f"  → **{child_title}** ({child_file})")
            else:
                if grandchildren:
                    lines.append(f"  - {child_title} ({child_file}) [{len(grandchildren)} sub]")
                else:
                    lines.append(f"  - {child_title} ({child_file})")

        return "\n".join(lines)

    def get_chapter_children(self, chapter_title: str) -> str:
        """
        [HANDBOOK] Get children of a specific chapter

        Args:
            chapter_title: Title of the parent chapter (partial match supported)

        Returns:
            List of child chapters or error message

        Examples:
            get_chapter_children("Interpolation")
            get_chapter_children("Drawing")
        """
        if not self.is_initialized:
            return "Handbook module not initialized"

        try:
            toc_data = self.cache_manager.load_toc_structure()

            if not toc_data:
                return "❌ TOC structure not found."

            chapters = toc_data.get("chapters", [])
            matches = self._find_chapters_by_title(chapters, chapter_title)

            if not matches:
                return (
                    f"❌ No chapter found matching '{chapter_title}'\n\n"
                    "💡 Use `handbook_get_toc()` to see all available chapters."
                )

            # Format results
            output = [f"# 📂 Children of '{chapter_title}'\n"]

            for match in matches:
                title = match.get("title", "Unknown")
                children = match.get("children", [])

                if not children:
                    output.append(f"**{title}** has no children (leaf chapter).\n")
                else:
                    output.append(f"## {title}\n")
                    for child in children:
                        child_title = child.get("title", "Unknown")
                        child_file = child.get("file", "")
                        grandchildren = child.get("children", [])

                        if child_file:
                            output.append(f"- **{child_title}** (`{child_file}`)")
                        else:
                            output.append(f"- **{child_title}** (index)")

                        if grandchildren:
                            output.append(f"  - ({len(grandchildren)} sub-chapters)")

                    output.append("")

            return "\n".join(output)

        except Exception as e:
            logger.error(f"Failed to get chapter children: {e}")
            return f"❌ Failed to get chapter children: {str(e)}"

    def _find_chapters_by_title(
        self, entries: list[dict], title: str
    ) -> list[dict]:
        """Find chapters matching title (case-insensitive partial match)"""
        matches = []
        title_lower = title.lower()

        for entry in entries:
            entry_title = entry.get("title", "").lower()
            if title_lower in entry_title:
                matches.append(entry)

            # Search children recursively
            children = entry.get("children", [])
            if children:
                matches.extend(self._find_chapters_by_title(children, title))

        return matches

    def _find_parent_chapter(
        self, chapters: list[dict], target: dict
    ) -> dict | None:
        """Find the parent chapter of a nested entry"""
        for ch in chapters:
            children = ch.get("children", [])
            if target in children:
                return ch
            # Search deeper
            for child in children:
                grandchildren = child.get("children", [])
                if target in grandchildren:
                    return ch  # Return top-level parent for context
                # Continue searching
                if grandchildren:
                    result = self._find_parent_in_children(child, target)
                    if result:
                        return ch
        return None

    def _find_parent_in_children(self, parent: dict, target: dict) -> dict | None:
        """Helper to find parent in nested children"""
        for child in parent.get("children", []):
            if child is target:
                return parent
            grandchildren = child.get("children", [])
            if target in grandchildren:
                return child
            if grandchildren:
                result = self._find_parent_in_children(child, target)
                if result:
                    return result
        return None

    def _format_matched_entry(self, entry: dict, highlight: str) -> str:
        """Format a matched entry with its children (only entries with files)"""
        lines = [f"# TOC: {entry['title']}\n"]

        # Show entry itself if it has a file
        entry_file = entry.get("file", "")
        if entry_file:
            lines.append(f"**{entry['title']}** ({entry_file})")

        # Show children that have files
        children = entry.get("children", [])
        children_with_files = [c for c in children if c.get("file")]

        if children_with_files:
            for child in children_with_files:
                child_title = child.get("title", "")
                child_file = child.get("file", "")
                grandchildren = [gc for gc in child.get("children", []) if gc.get("file")]
                if grandchildren:
                    lines.append(f"  - {child_title} ({child_file}) [{len(grandchildren)} sub]")
                else:
                    lines.append(f"  - {child_title} ({child_file})")

        if not entry_file and not children_with_files:
            lines.append("(No associated files for this entry)")

        return "\n".join(lines)

    def _unified_search(self, query: str, max_results: int) -> str:
        """Unified search implementation: pure content search (TOC matching removed)"""
        try:
            # Directly use searcher for content search
            result = self.searcher.search(query, max_results=max_results)

            if result and not result.startswith("No results found"):
                return result
            else:
                return f"🔍 No content related to '{query}' found in handbook.\n\n💡 Try using different keywords or search in English"

        except Exception as e:
            logger.error(f"Unified search failed: {e}")
            return f"Search error: {str(e)}"

    def _smart_fetch_content(self, filename: str) -> str:
        """Smart content fetch, handles filename and auto-completion"""
        try:
            filename = filename.strip()

            # Check if this is a Custom Parameters intro request
            if "custom_parameter" in filename.lower():
                return self._fetch_custom_parameters_intro()

            # Normalize filename (remove legacy prefix and suffix)
            clean_name = filename.removesuffix(".md").removeprefix(
                "handbook_glyphsapp_com_"
            )
            # New simplified filename format
            full_filename = f"{clean_name}.md"

            return self._load_file_directly(full_filename)

        except Exception as e:
            logger.error(f"Smart fetch failed: {e}")
            return f"Content fetch error: {str(e)}"

    def _load_file_directly(self, filename: str) -> str:
        """Directly load content from specified filename"""
        try:
            handbook_path = self.cache_manager.get_active_cache_path()
            file_path = handbook_path / filename

            if not file_path.exists():
                return (
                    f"❌ File not found: {filename}\n\n"
                    f"💡 Use `handbook_search_content()` to search for related content"
                )

            content = file_path.read_text(encoding="utf-8")

            # Special handling: Custom Parameters file is very long, provide segmented processing
            if "custom_parameter" in filename.lower():
                return self._process_custom_parameters_file(content)

            # Regular files return complete content directly
            return content

        except Exception as e:
            logger.error(f"Failed to load file directly {filename}: {e}")
            return f"❌ Failed to load file: {filename}\nError: {str(e)}"

    def _clean_content(self, content: str) -> str:
        """Clean content (simplified version, replaces ChapterFinder._clean_content)"""
        # Remove excessive blank lines
        lines = content.split("\n")
        cleaned_lines = []
        prev_empty = False

        for line in lines:
            is_empty = not line.strip()
            if is_empty:
                if not prev_empty:
                    cleaned_lines.append("")
                prev_empty = True
            else:
                cleaned_lines.append(line)
                prev_empty = False

        return "\n".join(cleaned_lines).strip()

    def _process_custom_parameters_file(self, content: str) -> str:
        """Process Custom Parameters file with smart segmentation"""
        lines = content.split("\n")

        # If content is not long, return directly
        if len(lines) <= 50:
            return content

        # Provide intro section and usage instructions
        intro_lines = lines[:18]  # First 18 lines (not including first parameter title)
        intro_content = "\n".join(intro_lines)

        return f"""{intro_content}

---

⚠️ **This is a very long file** containing 200+ Custom Parameters descriptions.

💡 **Recommended tools**:
- `handbook_get_custom_parameter("parameter_name")` - View complete description of specific parameter
- `handbook_list_parameters()` - List all 205 available parameters
- `handbook_search_content("keyword")` - Search for related content in handbook

---
"""

    def _fetch_custom_parameters_intro(self) -> str:
        """Fetch Custom Parameters chapter intro (first 18 lines)"""
        try:
            # Find custom parameters file
            custom_params_file = None
            for file_info in self.handbook_files:
                if "custom_parameter" in file_info["name"]:
                    custom_params_file = Path(file_info["path"])
                    break

            if not custom_params_file or not custom_params_file.exists():
                return "❌ Custom Parameters file not found"

            with open(custom_params_file, encoding="utf-8") as f:
                lines = f.readlines()

            # Extract first 18 lines (not including first parameter title)
            intro_lines = lines[:18]
            content = "".join(intro_lines)

            # Clean and format content
            cleaned_content = self._clean_content(content)

            return f"# 📖 Custom Parameters Chapter Overview\n\n{cleaned_content}"

        except Exception as e:
            logger.error(f"Custom Parameters chapter intro fetch failed: {e}")
            return f"Chapter intro fetch error: {str(e)}"

    def fetch_custom_parameter(self, parameter_name: str) -> str:
        """
        [CUSTOM PARAMETER] Fetch specific Custom Parameter complete description by name

        Features:
        - Uses exact matching, parameter name must be completely correct
        - Supports space-separated parameter names (e.g., "Add Class", "CJK Grid")
        - Returns complete parameter description until next parameter

        Args:
            parameter_name: Parameter name (must be exact match, case-sensitive)

        Returns:
            Complete parameter description content, or error message if not found

        Examples:
            fetch_custom_parameter("ascender")
            fetch_custom_parameter("Add Class")
            fetch_custom_parameter("CJK Grid")
        """
        if not self.is_initialized:
            return "Handbook module not initialized"

        # Use term processor for post-processing
        result = self._fetch_specific_parameter_exact(parameter_name)

        if self.search_engine and self.search_engine.query_processor:
            # Detect user language (inferred from parameter_name, or default to Chinese)
            user_language = self.search_engine.query_processor.detect_user_language(  # type: ignore[attr-defined]
                parameter_name
            )
            return self.search_engine.query_processor.postprocess_output(
                result, user_language
            )
        else:
            return result

    def get_custom_parameters_list(self) -> str:
        """
        [CUSTOM PARAMETER] Get list of all available Custom Parameter names

        Features:
        - Provides complete name list of all 205 Custom Parameters
        - Lists all parameter names in order
        - Includes line number of each parameter in the document
        - For AI reference to call fetch_custom_parameter with correct names

        Returns:
            Structured parameter list with all available parameter names
        """
        if not self.is_initialized:
            return "Handbook module not initialized"

        return self._get_parameters_list_only()

    def _fetch_specific_parameter_exact(self, parameter_name: str) -> str:
        """Fetch specific parameter using exact matching (no fuzzy search)"""
        try:
            # Find custom parameters file
            custom_params_file = None
            for file_info in self.handbook_files:
                if "custom_parameter" in file_info["name"]:
                    custom_params_file = Path(file_info["path"])
                    break

            if not custom_params_file or not custom_params_file.exists():
                return "❌ Custom Parameters file not found"

            with open(custom_params_file, encoding="utf-8") as f:
                lines = f.readlines()

            # Use exact matching to find parameter
            parameter_content = self._extract_parameter_exact_match(
                lines, parameter_name
            )

            if parameter_content:
                return parameter_content
            else:
                return (
                    f"❌ Parameter '{parameter_name}' not found\n"
                    f"💡 Use `get_custom_parameters_list()` to view all available parameter names\n"
                    f"⚠️  Parameter name must be exactly correct and case-sensitive"
                )

        except Exception as e:
            logger.error(f"Parameter '{parameter_name}' fetch failed: {e}")
            return f"Parameter fetch error: {str(e)}"

    def _extract_parameter_exact_match(
        self, lines: list[str], parameter_name: str
    ) -> str | None:
        """Extract specific parameter from file lines using exact matching"""
        # Start searching from line 20 (exact matching)
        for i in range(19, len(lines)):
            line = lines[i].strip()

            # Exact match check
            if line == parameter_name:
                # Found parameter, start collecting content
                content_lines = [f"# 🔧 {line}\n"]

                # Collect all content from next line until next parameter
                j = i + 1
                while j < len(lines):
                    current_line = lines[j].strip()

                    # Check if this is the start of next parameter
                    # Core conditions: word count ≤ 6 and not a list item
                    if (
                        current_line
                        and not current_line.startswith("-")
                        and len(current_line.split()) <= 6
                        and j > i + 2
                    ):
                        break

                    content_lines.append(lines[j])
                    j += 1

                # Clean and format content
                raw_content = "".join(content_lines)
                return self._clean_content(raw_content)

        return None

    def _get_parameters_list_only(self) -> str:
        """Get list of all parameters (without summaries)"""
        try:
            # Find custom parameters file
            custom_params_file = None
            for file_info in self.handbook_files:
                if "custom_parameter" in file_info["name"]:
                    custom_params_file = Path(file_info["path"])
                    break

            if not custom_params_file or not custom_params_file.exists():
                return "❌ Custom Parameters file not found"

            with open(custom_params_file, encoding="utf-8") as f:
                lines = f.readlines()

            # Start identifying parameters from line 20
            parameters = []

            for i in range(19, len(lines)):  # Start from line 20 (index 19)
                line = lines[i].strip()

                # Core conditions: word count ≤ 6 and not a list item or heading
                if (
                    line
                    and not line.startswith("#")
                    and not line.startswith("-")
                    and len(line.split()) <= 6
                ):

                    parameters.append({"name": line, "line": i + 1})

            # Format output
            output = [f"# 📋 Custom Parameters Complete List ({len(parameters)} parameters)"]
            output.append(
                "Below are all available parameter names, use the exact same name to call `fetch_custom_parameter()`:\n"
            )

            for i, param in enumerate(parameters, 1):
                output.append(f"{i:3d}. **{param['name']}** (line {param['line']})")

            output.append("\n💡 **Usage**:")
            output.append("- Use `fetch_custom_parameter('parameter_name')` to fetch specific parameter")
            output.append("- Parameter name must be exactly correct, including spaces and case")
            output.append(
                "- Example: `fetch_custom_parameter('Add Class')` or `fetch_custom_parameter('ascender')`"
            )

            return "\n".join(output)

        except Exception as e:
            logger.error(f"Parameter list fetch failed: {e}")
            return f"Parameter list fetch error: {str(e)}"

    async def update_cache(self, force: bool = False) -> str:
        """
        [CACHE MANAGEMENT] Update Handbook dynamic cache

        Features:
        - Re-fetch latest Handbook content from official website
        - Update fresh cache to latest version
        - Option to force update (ignore cache validity check)

        Args:
            force: Whether to force update (default: False)
                - True: Force re-fetch even if cache is still valid
                - False: Only update when cache is expired

        Returns:
            Update result message

        Examples:
            update_cache()  # Auto-check and update expired cache
            update_cache(force=True)  # Force update
        """
        if not self.is_initialized:
            return "Handbook module not initialized"

        try:
            logger.info(f"Starting Handbook cache update (force={force})")

            # Execute update
            success = await self.cache_manager.update_fresh_cache(force=force)

            if success:
                # Reload module to use new cache
                new_handbook_path = self.cache_manager.get_active_cache_path()
                logger.info(f"Cache update successful, reloading: {new_handbook_path}")

                # Reinitialize searcher
                if self.use_enhanced_search and EnhancedHandbookSearcher is not None:
                    self.searcher = EnhancedHandbookSearcher(new_handbook_path)
                else:
                    self.searcher = HandbookSearcher(new_handbook_path)

                self._load_handbook_files(new_handbook_path)

                return (
                    "✅ Handbook cache update successful!\n\n"
                    f"- Cache path: {new_handbook_path}\n"
                    f"- File count: {len(self.handbook_files)}\n"
                    f"- Status: Reloaded and activated\n\n"
                    "💡 All queries will now use the latest Handbook content."
                )
            else:
                return (
                    "❌ Handbook cache update failed\n\n"
                    "Possible causes:\n"
                    "- Network connection issue\n"
                    "- Official website inaccessible\n"
                    "- Insufficient permissions\n\n"
                    "Check logs for detailed error messages."
                )

        except Exception as e:
            logger.error(f"Cache update error occurred: {e}")
            return f"Cache update error: {str(e)}"

    async def get_cache_info(self) -> str:
        """
        [CACHE MANAGEMENT] View Handbook cache status information

        Features:
        - Display current cache version in use (stable or fresh)
        - Display cache file count and location
        - Display cache creation time and age
        - Provide cache management suggestions

        Returns:
            Structured cache status information

        Examples:
            get_cache_info()
        """
        if not self.is_initialized:
            return "Handbook module not initialized"

        try:
            status = self.cache_manager.get_cache_status()

            output = ["# 📊 Handbook Cache Status Information\n"]

            # Current active cache
            active_cache = status["active_cache"]
            output.append("## Current Active Cache")
            output.append(f"- **Type**: {active_cache.upper()}")

            # Stable cache info
            output.append("\n## Stable Cache (Stable Version)")
            stable = status["stable_cache"]
            output.append(f"- **Exists**: {'Yes' if stable['exists'] else 'No'}")
            output.append(f"- **File count**: {stable['file_count']}")

            if "info" in stable:
                info = stable["info"]
                output.append(f"- **Cache date**: {info.get('cache_date', 'N/A')}")
                output.append(f"- **Source**: {info.get('source_url', 'N/A')}")
                output.append(f"- **Scraper version**: {info.get('scraper_version', 'N/A')}")

            # Fresh cache info
            output.append("\n## Fresh Cache (Dynamic Update)")
            fresh = status["fresh_cache"]
            output.append(f"- **Exists**: {'Yes' if fresh['exists'] else 'No'}")
            output.append(f"- **Valid**: {'Yes' if fresh['valid'] else 'No'}")
            output.append(f"- **File count**: {fresh['file_count']}")

            if "info" in fresh:
                info = fresh["info"]
                output.append(f"- **Last updated**: {info.get('cache_date', 'N/A')}")
                output.append(f"- **Source**: {info.get('source_url', 'N/A')}")
                output.append(
                    f"- **Cache validity**: {info.get('cache_max_age_days', 7)} days"
                )

            # Management suggestions
            output.append("\n## 💡 Management Suggestions")

            if not fresh["exists"]:
                output.append("- Recommend running `update_cache()` to create dynamic cache")
            elif not fresh["valid"]:
                output.append("- Fresh cache expired, recommend running `update_cache()` to update")
            else:
                output.append("- Cache status is good, no action needed")

            output.append("\n## 🔧 Available Operations")
            output.append("- `update_cache()` - Update dynamic cache")
            output.append("- `update_cache(force=True)` - Force re-fetch")

            return "\n".join(output)

        except Exception as e:
            logger.error(f"Failed to get cache info: {e}")
            return f"Cache info fetch error: {str(e)}"
