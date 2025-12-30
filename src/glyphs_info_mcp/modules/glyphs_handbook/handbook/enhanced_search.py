"""
Enhanced Handbook Searcher - Smart search engine based on Python API search optimization architecture.
Supports relevance scoring, multi-word search, and search scope control.
"""

import logging
import re
from pathlib import Path
from typing import Any

from glyphs_info_mcp.modules.glyphs_handbook.handbook.section_parser import (
    MarkdownSectionParser,
)
from glyphs_info_mcp.modules.glyphs_handbook.handbook.utils import extract_title
from glyphs_info_mcp.shared.core.query_utils import highlight_keyword, tokenize_query
from glyphs_info_mcp.shared.core.scoring_weights import (
    MatchTypeWeights,
    MultiWordWeights,
    SearchLimits,
)

logger = logging.getLogger(__name__)


class EnhancedHandbookSearcher:
    """Enhanced handbook searcher - Smart search engine"""

    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.index_file = data_path / "index.md"
        self.files: list[str] = []
        self.file_cache: dict[str, str] = {}  # File content cache
        self.section_parser = MarkdownSectionParser()  # Section parser
        self._load_files()

    def _load_files(self) -> None:
        """Load file list"""
        try:
            if self.data_path.exists():
                for file_path in self.data_path.glob("*.md"):
                    if file_path.name != "index.md":
                        self.files.append(file_path.name)

                logger.info(f"Scanned {len(self.files)} handbook files")
                self.files.sort()
            else:
                logger.error(f"Data directory not found: {self.data_path}")
        except Exception as e:
            logger.error(f"Failed to load file list: {e}")

    def search(self, query: str, search_scope: str = 'all', max_results: int = SearchLimits.DEFAULT_MAX_RESULTS) -> str:
        """Smart search handbook content

        Args:
            query: Search keyword
            search_scope: Search scope
                - 'titles': Search titles only
                - 'content': Search content only
                - 'all': Search all content (default)
            max_results: Maximum number of results (default: 5)

        Returns:
            Formatted search results string
        """
        if not query.strip():
            return "Please provide a search keyword"

        if not self.files:
            return "No handbook files found"

        # Use new extended search logic
        results = self._extended_search(query, search_scope)

        if not results:
            return f"No content related to '{query}' found in handbook. Searched {len(self.files)} files."

        return self._format_search_results(query, results, max_results)

    def _extended_search(self, query: str, search_scope: str = 'all') -> list[dict]:
        """Execute extended search supporting multi-word, title, and content search

        Args:
            query: Search query
            search_scope: Search scope

        Returns:
            List of search results with relevance scores
        """
        results = []
        query_lower = query.lower()

        # Use shared tokenization tool (automatically filters short words)
        query_words = tokenize_query(query)

        logger.info(f"Starting smart search for keyword: '{query}', scope: {search_scope}, checking {len(self.files)} files")

        # Search all files
        for filename in self.files:
            file_matches = self._search_in_file(filename, query_lower, query_words, search_scope)
            results.extend(file_matches)

        # Sort results (by relevance score)
        results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

        return results

    def _search_in_file(self, filename: str, query_lower: str, query_words: list[str], search_scope: str) -> list[dict[str, Any]]:
        """Search within a file"""
        results: list[dict[str, Any]] = []

        # Get file content
        content = self._get_file_content(filename)
        if not content:
            return results

        # Extract title and content
        title = extract_title(content)

        # Calculate relevance score
        file_score = self._calculate_relevance_score(
            target_title=title,
            target_content=content,
            query_lower=query_lower,
            query_words=query_words,
            search_scope=search_scope
        )

        if file_score > 0:
            results.append({
                'type': 'handbook_file',
                'filename': filename,
                'title': title,
                'content': content,
                'relevance_score': file_score,
                'match_type': self._get_match_type(title, content, query_lower, search_scope),
                'excerpts': self._extract_excerpts(content, query_lower)
            })

        return results

    def _calculate_relevance_score(self, target_title: str, target_content: str,
                                  query_lower: str, query_words: list, search_scope: str) -> float:
        """Calculate relevance score - improved version, resolves 0.65 score clustering issue

        Args:
            target_title: Target title
            target_content: Target content
            query_lower: Lowercase query string
            query_words: Query word list
            search_scope: Search scope

        Returns:
            Relevance score (0.0-1.0), 0 means no match
        """
        score = 0.0
        match_details = []  # For debugging and analysis

        target_title_lower = target_title.lower()
        target_content_lower = target_content.lower()

        # Determine content to search based on search scope
        search_in_titles = search_scope in ['titles', 'all']
        search_in_content = search_scope in ['content', 'all']

        # Title match scoring (highest priority)
        if search_in_titles:
            title_score = self._calculate_title_score(query_lower, query_words, target_title_lower)
            if title_score > 0:
                score = max(score, title_score)
                match_details.append(f"title: {title_score:.3f}")

        # Section header match scoring (medium priority)
        if search_scope == 'all':
            section_score = self._calculate_section_score(query_lower, query_words, target_content)
            if section_score > 0:
                score = max(score, section_score)
                match_details.append(f"section: {section_score:.3f}")

        # Content match scoring
        if search_in_content:
            content_score = self._calculate_content_score(query_lower, query_words, target_content_lower)
            if content_score > 0:
                score = max(score, content_score)
                match_details.append(f"content: {content_score:.3f}")

        return score

    def _calculate_title_score(self, query_lower: str, query_words: list, target_title_lower: str) -> float:
        """Calculate title match score - dynamic scoring

        Uses shared weight constants to ensure scoring consistency.
        """

        # Exact match - highest score
        if query_lower == target_title_lower:
            return MatchTypeWeights.EXACT  # 1.0

        # Title prefix match - very high score
        if target_title_lower.startswith(query_lower):
            return MatchTypeWeights.PREFIX  # 0.95

        # Title partial match - high score, adjusted by match position
        if query_lower in target_title_lower:
            # Give different scores based on match position
            match_position = target_title_lower.find(query_lower)
            position_factor = max(0.1, 1.0 - (match_position / len(target_title_lower)))
            base_score = MatchTypeWeights.CONTAINS  # 0.85
            return base_score + (0.05 * position_factor)  # 0.85-0.90

        # Multi-word title match - dynamic scoring
        if len(query_words) > 1:
            match_ratio, match_quality = self._advanced_multi_word_match(query_words, target_title_lower)
            if match_ratio >= MultiWordWeights.HIGH_MATCH_THRESHOLD:  # 0.8
                base_score = MultiWordWeights.HIGH_MATCH_BASE  # 0.75
                quality_bonus = match_quality * MultiWordWeights.QUALITY_BONUS_MAX  # 0.1
                return base_score + quality_bonus  # 0.75-0.85
            elif match_ratio >= MultiWordWeights.MEDIUM_MATCH_THRESHOLD:  # 0.6
                base_score = MultiWordWeights.MEDIUM_MATCH_BASE  # 0.65
                return base_score + (match_ratio - 0.6) * 0.25  # 0.65-0.70

        return 0.0

    def _calculate_section_score(self, query_lower: str, query_words: list, target_content: str) -> float:
        """Calculate section header match score

        Uses shared weight constants to ensure scoring consistency.
        """
        max_section_score = 0.0

        section_headers = self._extract_section_headers(target_content)
        for header in section_headers:
            header_lower = header.lower()

            # Section header exact match
            if query_lower == header_lower:
                max_section_score = max(max_section_score, MatchTypeWeights.CONTAINS)  # 0.85
            # Section header partial match
            elif query_lower in header_lower:
                max_section_score = max(max_section_score, 0.80)
            # Section header multi-word match
            elif len(query_words) > 1:
                match_ratio, match_quality = self._advanced_multi_word_match(query_words, header_lower)
                if match_ratio >= MultiWordWeights.HIGH_MATCH_THRESHOLD:  # 0.8
                    score = 0.70 + (match_quality * MultiWordWeights.DENSITY_BONUS_MAX)  # 0.70-0.75
                    max_section_score = max(max_section_score, score)
                elif match_ratio >= MultiWordWeights.MEDIUM_MATCH_THRESHOLD:  # 0.6
                    score = 0.60 + (match_ratio - 0.6) * 0.25  # 0.60-0.65
                    max_section_score = max(max_section_score, score)

        return max_section_score

    def _calculate_content_score(self, query_lower: str, query_words: list, target_content_lower: str) -> float:
        """Calculate content match score - considers match frequency and density

        Uses shared weight constants to ensure scoring consistency.
        """

        # Direct match, but consider frequency
        if query_lower in target_content_lower:
            # Calculate match frequency
            match_count = target_content_lower.count(query_lower)
            frequency_factor = min(1.0, match_count / 3)  # Max score at 3 occurrences
            base_score = 0.55
            return base_score + (MultiWordWeights.QUALITY_BONUS_MAX * frequency_factor)  # 0.55-0.65

        # Multi-word content match - improved scoring
        if len(query_words) > 1:
            match_ratio, match_quality = self._advanced_multi_word_match(query_words, target_content_lower)
            if match_ratio >= MultiWordWeights.HIGH_MATCH_THRESHOLD:  # 0.8
                # Consider word distribution density
                density_score = self._calculate_match_density(query_words, target_content_lower)
                base_score = 0.45
                ratio_bonus = (match_ratio - 0.8) * 0.5  # Max add 0.1 (at 100%)
                quality_bonus = match_quality * MultiWordWeights.DENSITY_BONUS_MAX  # 0.05
                density_bonus = density_score * MultiWordWeights.DENSITY_BONUS_MAX   # 0.05
                return base_score + ratio_bonus + quality_bonus + density_bonus  # 0.45-0.65
            elif match_ratio >= MultiWordWeights.MEDIUM_MATCH_THRESHOLD:  # 0.6
                return 0.35 + (match_ratio - 0.6) * 0.25  # 0.35-0.40

        return 0.0

    def _advanced_multi_word_match(self, query_words: list, target_text: str) -> tuple[float, float]:
        """Improved multi-word matching, returns match ratio and quality score

        Returns:
            tuple[match_ratio, match_quality]: Match ratio and quality score (0.0-1.0)
        """
        if len(query_words) <= 1:
            return 0.0, 0.0

        found_words = 0
        total_importance = 0.0
        found_importance = 0.0

        # Assign importance weight to each word (longer words are more important)
        word_importance = {}
        for word in query_words:
            importance = min(1.0, len(word) / 6)  # Words 6+ letters are most important
            word_importance[word] = importance
            total_importance += importance

        # Check matches
        for word in query_words:
            if word in target_text:
                found_words += 1
                found_importance += word_importance[word]

        # Calculate match ratio (average of two methods)
        count_ratio = found_words / len(query_words)
        importance_ratio = found_importance / total_importance if total_importance > 0 else 0
        match_ratio = (count_ratio + importance_ratio) / 2

        # Calculate match quality (considering word importance distribution)
        match_quality = importance_ratio

        return match_ratio, match_quality

    def _calculate_match_density(self, query_words: list, target_text: str) -> float:
        """Calculate match density score - closer words score higher"""
        found_positions = []

        for word in query_words:
            pos = target_text.find(word)
            if pos != -1:
                found_positions.append(pos)

        if len(found_positions) < 2:
            return 0.0

        # Calculate average distance between words
        found_positions.sort()
        distances = []
        for i in range(1, len(found_positions)):
            distances.append(found_positions[i] - found_positions[i-1])

        if not distances:
            return 0.0

        avg_distance = sum(distances) / len(distances)
        # Smaller distance = higher density score, normalized to 0-1
        density_score = max(0.0, 1.0 - (avg_distance / 200))  # Within 200 chars is high density

        return density_score

    def _multi_word_match(self, query_words: list, target_text: str) -> bool:
        """Check multi-word match - using improved logic

        Args:
            query_words: Query word list
            target_text: Target text

        Returns:
            True if high match threshold is reached
        """
        if len(query_words) <= 1:
            return False

        match_ratio, _ = self._advanced_multi_word_match(query_words, target_text)
        return match_ratio >= MultiWordWeights.HIGH_MATCH_THRESHOLD  # 0.8

    def _get_match_type(self, target_title: str, target_content: str,
                       query_lower: str, search_scope: str) -> str:
        """Get match type (for display)

        Returns:
            Match type: 'title', 'section', 'content', 'multi_word'
        """
        target_title_lower = target_title.lower()
        target_content_lower = target_content.lower()

        if query_lower in target_title_lower:
            return 'title'

        # Check section header match
        section_headers = self._extract_section_headers(target_content)
        for header in section_headers:
            if query_lower in header.lower():
                return 'section'

        if query_lower in target_content_lower:
            return 'content'
        else:
            return 'multi_word'  # Multi-word match

    def _extract_section_headers(self, content: str) -> list[str]:
        """Extract section headers"""
        headers = []
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            # Match Markdown headers (##, ###, ####)
            if re.match(r'^#{2,4}\s+', line):
                header = re.sub(r'^#{2,4}\s+', '', line)
                header = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', header)  # Remove links
                headers.append(header)

        return headers

    def _get_file_content(self, filename: str) -> str:
        """Get file content (using cache)"""
        if filename not in self.file_cache:
            file_path = self.data_path / filename
            try:
                content = file_path.read_text(encoding='utf-8')
                self.file_cache[filename] = content
            except Exception as e:
                logger.error(f"Failed to read file {filename}: {e}")
                return ""

        return self.file_cache.get(filename, "")

    def _extract_intro_only(self, content: str) -> str:
        """Layer 1 extraction: Return file introduction only

        For title matches, return the most concise content (1-3 lines).
        Extract the first non-empty paragraph after the title as introduction.

        Args:
            content: Complete file content

        Returns:
            Introduction text (1-3 lines), or empty string if none
        """
        if not content.strip():
            return ""

        lines = content.split('\n')
        intro_lines: list[str] = []
        found_header = False

        for line in lines:
            stripped = line.strip()

            # Skip main title (# prefix)
            if stripped.startswith('# '):
                found_header = True
                continue

            # Skip subheadings (## or more)
            if stripped.startswith('##'):
                # If we've collected intro content, stop at subheading
                if intro_lines:
                    break
                continue

            # Skip empty lines (before finding content)
            if not stripped and not intro_lines:
                continue

            # End collection when empty line encountered with existing content
            if not stripped and intro_lines:
                break

            # Collect intro content
            intro_lines.append(stripped)

            # Maximum 3 lines
            if len(intro_lines) >= 3:
                break

        return '\n'.join(intro_lines)

    def _extract_section_summary(self, content: str, query: str) -> str:
        """Layer 2 extraction: Return matching subsection summary

        For section header matches, return subsection title + 3 lines of summary.

        Args:
            content: Complete file content
            query: Search keyword

        Returns:
            Subsection title + summary (~5 lines), or empty string if no match
        """
        if not content.strip():
            return ""

        lines = content.split('\n')
        query_lower = query.lower()

        # Find subsection containing keyword
        for i, line in enumerate(lines):
            stripped = line.strip()

            # Look for ### or #### subsection headers
            if stripped.startswith('###'):
                # Check if header contains keyword
                # Remove Markdown syntax to check
                title_text = stripped.lstrip('#').strip()
                # Remove link syntax [Title](#anchor)
                title_clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', title_text)

                if query_lower in title_clean.lower():
                    # Found matching subsection, collect title + 3 lines of content
                    summary_lines = [stripped]  # Title
                    content_count = 0

                    for j in range(i + 1, len(lines)):
                        next_line = lines[j].strip()

                        # Stop at next subsection header
                        if next_line.startswith('##'):
                            break

                        # Skip empty lines
                        if not next_line:
                            continue

                        summary_lines.append(next_line)
                        content_count += 1

                        # Maximum 3 lines of content
                        if content_count >= 3:
                            break

                    return '\n'.join(summary_lines)

        return ""

    def _extract_excerpts_by_layer(
        self, content: str, query: str, match_type: str
    ) -> str:
        """Main entry point for layered extraction: Return content of varying detail based on match type

        Args:
            content: Complete file content
            query: Search keyword
            match_type: Match type ('title', 'section', 'content', 'multi_word')

        Returns:
            Extracted content based on match type
        """
        if match_type == 'title':
            # Layer 1: Title match → return intro only
            return self._extract_intro_only(content)

        elif match_type == 'section':
            # Layer 2: Section match → return subsection summary
            return self._extract_section_summary(content, query)

        else:
            # Layer 3: Content match / multi-word match → use full section extraction
            excerpts = self._extract_excerpts(content, query)
            return '\n\n'.join(excerpts) if excerpts else ""

    def _extract_excerpts(self, content: str, query: str) -> list[str]:
        """Extract relevant sections - smart extraction based on Markdown section structure

        Uses Section Parser to identify ###/#### subsection structure,
        returns complete semantic units rather than arbitrary line fragments.
        """
        lines = content.split('\n')

        # Parse section structure
        sections = self.section_parser.parse_sections(content)

        # Fall back to legacy logic if no sections parsed
        if not sections:
            return self._extract_excerpts_legacy(content, query)

        excerpts = []
        matched_sections: set[str] = set()

        # Find all lines containing query keyword
        query_lower = query.lower()
        for i, line in enumerate(lines):
            if query_lower in line.lower():
                # Find which section this line belongs to
                section = self.section_parser.find_section_for_line(sections, i)
                if section and section.title not in matched_sections:
                    matched_sections.add(section.title)
                    # Smart extract section content
                    excerpt = self.section_parser.extract_smart_excerpt(
                        section, query, lines
                    )
                    excerpts.append(excerpt)

        # Fall back to legacy logic if no matching sections found
        if not excerpts:
            return self._extract_excerpts_legacy(content, query)

        return excerpts[:SearchLimits.MAX_EXCERPTS_PER_RESULT]

    def _extract_excerpts_legacy(self, content: str, query: str) -> list[str]:
        """Extract relevant sections (legacy logic, used as fallback)"""
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

    def _format_search_results(self, query: str, results: list[dict], max_results: int = SearchLimits.DEFAULT_MAX_RESULTS) -> str:
        """Format search results

        Args:
            query: Search keyword
            results: List of search results
            max_results: Maximum number of results to display

        Returns:
            Formatted search results string
        """
        total_found = len(results)
        display_results = results[:max_results]

        output = [f"🔍 **Smart Search Results** - Showing {len(display_results)} of {total_found} related files:\n"]

        for i, result in enumerate(display_results, 1):
            # Display relevance score and match type
            score = result.get('relevance_score', 0)
            match_type = result.get('match_type', 'unknown')
            match_type_display = {
                'title': '📌 Title Match',
                'section': '📋 Section Match',
                'content': '📄 Content Match',
                'multi_word': '🔍 Multi-word Match'
            }.get(match_type, '❓ Unknown Match')

            output.append(f"**{i}. {result['title']}** (Relevance: {score:.2f})")
            output.append(f"🏷️ Match Type: {match_type_display}")
            output.append(f"📄 File: `{result['filename']}`")

            # Display relevant excerpts
            for j, excerpt in enumerate(result.get('excerpts', [])[:2]):  # Show max 2 excerpts
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
        """Get statistics information"""
        return {
            "total_files": len(self.files),
            "cache_size": len(self.file_cache),
            "data_path": str(self.data_path),
            "index_file_exists": self.index_file.exists(),
            "sample_files": self.files[:5]
        }
