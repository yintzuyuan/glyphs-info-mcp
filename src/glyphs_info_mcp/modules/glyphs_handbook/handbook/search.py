"""
Handbook Searcher (revised version)
"""

import logging
from pathlib import Path
from typing import Any

from glyphs_info_mcp.modules.glyphs_handbook.handbook.utils import extract_title
from glyphs_info_mcp.shared.core.query_utils import highlight_keyword
from glyphs_info_mcp.shared.core.scoring_weights import SearchLimits

logger = logging.getLogger(__name__)


class HandbookSearcher:
    """Handbook searcher"""

    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.index_file = data_path / "index.md"
        self.files: list[str] = []
        self._load_files()

    def _load_files(self) -> None:
        """Load file list"""
        try:
            # Directly scan all .md files in directory
            if self.data_path.exists():
                for file_path in self.data_path.glob("*.md"):
                    if file_path.name != "index.md":  # Exclude index file
                        self.files.append(file_path.name)

                logger.info(f"Scanned {len(self.files)} handbook files")

                # Sort by filename
                self.files.sort()
            else:
                logger.error(f"Data directory not found: {self.data_path}")

        except Exception as e:
            logger.error(f"Failed to load file list: {e}")

    def search(self, query: str, max_results: int = SearchLimits.DEFAULT_MAX_RESULTS) -> str:
        """Search handbook content

        Args:
            query: Search keyword
            max_results: Maximum number of results (default: 5)

        Returns:
            Formatted search results string
        """
        if not query.strip():
            return "Please provide a search keyword"

        if not self.files:
            return "No handbook files found"

        results = []
        query_lower = query.lower()

        logger.info(f"Starting search for keyword: '{query}', checking {len(self.files)} files")

        # Search all files
        for filename in self.files:
            file_path = self.data_path / filename
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                continue

            try:
                content = file_path.read_text(encoding='utf-8')

                # Check if contains keyword (case-insensitive)
                if query_lower in content.lower():
                    # Extract relevant excerpts
                    excerpts = self._extract_excerpts(content, query_lower)
                    if excerpts:
                        results.append({
                            'file': filename,
                            'title': extract_title(content),
                            'excerpts': excerpts
                        })
                        logger.info(f"Found matching content in file {filename}")

            except Exception as e:
                logger.error(f"Failed to read file {filename}: {e}")

        if not results:
            return f"No content related to '{query}' found in handbook. Searched {len(self.files)} files."

        # Format results
        return self._format_results(query, results, max_results)

    def _extract_excerpts(self, content: str, query: str) -> list[str]:
        """Extract relevant excerpts"""
        excerpts = []
        lines = content.split('\n')

        for i, line in enumerate(lines):
            if query in line.lower():
                # Extract context lines before and after
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                context_lines = []

                for j in range(start, end):
                    line_content = lines[j].strip()
                    if line_content:  # Keep only non-empty lines
                        context_lines.append(line_content)

                if context_lines:
                    context = '\n'.join(context_lines)
                    excerpts.append(context)

        # Deduplicate and limit count
        unique_excerpts = []
        for excerpt in excerpts:
            if excerpt not in unique_excerpts:
                unique_excerpts.append(excerpt)

        return unique_excerpts[:SearchLimits.MAX_EXCERPTS_PER_RESULT]

    def _format_results(self, query: str, results: list[dict[str, Any]], max_results: int = SearchLimits.DEFAULT_MAX_RESULTS) -> str:
        """Format search results

        Args:
            query: Search keyword
            results: List of search results
            max_results: Maximum number of results to display
        """
        total_found = len(results)
        display_results = results[:max_results]

        output = [f"🔍 Found {total_found} results, showing {len(display_results)}:\n"]

        for i, result in enumerate(display_results, 1):
            output.append(f"**{i}. {result['title']}**")
            output.append(f"📄 File: {result['file']}")

            for j, excerpt in enumerate(result['excerpts']):
                # Highlight keyword
                highlighted = highlight_keyword(excerpt, query)
                output.append("```")
                output.append(highlighted)
                output.append("```")

            output.append("")  # Empty line separator

        return '\n'.join(output)

    def get_file_list(self) -> list[str]:
        """Get file list (for debugging)"""
        return self.files.copy()

    def get_stats(self) -> dict[str, Any]:
        """Get statistics info"""
        return {
            "total_files": len(self.files),
            "data_path": str(self.data_path),
            "index_file_exists": self.index_file.exists(),
            "sample_files": self.files[:5]
        }
