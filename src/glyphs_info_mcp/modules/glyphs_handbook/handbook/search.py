"""
Handbook Searcher (revised version)
"""

import logging
import re
from pathlib import Path
from typing import Any

from glyphs_info_mcp.shared.core.query_utils import highlight_keyword

logger = logging.getLogger(__name__)


class HandbookSearcher:
    """Handbook searcher"""

    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.index_file = data_path / "index.md"
        self.files = []
        self._load_files()

    def _load_files(self):
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

    def search(self, query: str) -> str:
        """Search handbook content"""
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
                            'title': self._extract_title(content),
                            'excerpts': excerpts
                        })
                        logger.info(f"Found matching content in file {filename}")

            except Exception as e:
                logger.error(f"Failed to read file {filename}: {e}")

        if not results:
            return f"No content related to '{query}' found in handbook. Searched {len(self.files)} files."

        # Format results
        return self._format_results(query, results)

    def _extract_title(self, content: str) -> str:
        """Extract document title"""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                # Remove Markdown link syntax
                title = line[2:].strip()
                # Remove [title](url) format links
                title = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', title)
                return title
        return "Unnamed chapter"

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

        return unique_excerpts[:3]  # Return max 3 excerpts

    def _format_results(self, query: str, results: list[dict[str, Any]]) -> str:
        """Format search results"""
        output = [f"🔍 Found {len(results)} related results in handbook:\n"]

        for i, result in enumerate(results[:5], 1):  # Show max 5 results
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
