"""
Markdown Section Parser - Section structure parser

Parses Handbook Markdown file ##, ###, #### header structures,
supporting intelligent content extraction based on sections.
"""

import re
from dataclasses import dataclass


@dataclass
class Section:
    """Markdown section data structure"""

    level: int  # Header level (2=##, 3=###, 4=####)
    title: str  # Section title (without Markdown syntax)
    anchor: str  # Anchor ID
    start_line: int  # Start line number (0-indexed)
    end_line: int  # End line number (0-indexed, inclusive)


class MarkdownSectionParser:
    """Markdown section structure parser"""

    # Constants
    MAX_EXCERPT_LINES = 15  # Maximum lines for section excerpt
    CONTEXT_LINES_BEFORE = 2  # Context lines before match
    CONTEXT_LINES_AFTER = 3  # Context lines after match

    # Header regex patterns
    # Match format: ## [Title](#anchor) or ## Title
    HEADER_WITH_ANCHOR_PATTERN = re.compile(
        r'^(#{2,4})\s*\[([^\]]+)\]\(#([^)]+)\)'
    )
    HEADER_SIMPLE_PATTERN = re.compile(r'^(#{2,4})\s+(.+)$')

    def parse_sections(self, content: str) -> list[Section]:
        """Parse Markdown content into section structure

        Args:
            content: Markdown content string

        Returns:
            List of sections in order of appearance
        """
        if not content.strip():
            return []

        sections: list[Section] = []
        lines = content.split('\n')
        current_section: Section | None = None

        for i, line in enumerate(lines):
            # Try to parse header line
            parsed = self._parse_header_line(line)
            if parsed is None:
                continue

            level, title, anchor = parsed

            # End previous section
            if current_section is not None:
                current_section.end_line = i - 1
                sections.append(current_section)

            # Start new section
            current_section = Section(
                level=level,
                title=title,
                anchor=anchor,
                start_line=i,
                end_line=len(lines) - 1,  # Temporarily set to end of file
            )

        # Handle last section
        if current_section is not None:
            sections.append(current_section)

        return sections

    def _parse_header_line(self, line: str) -> tuple[int, str, str] | None:
        """Parse header line, return (level, title, anchor) or None

        Args:
            line: Line to parse

        Returns:
            (level, title, anchor) tuple, or None if not a header line
        """
        # Try to match header with anchor
        match = self.HEADER_WITH_ANCHOR_PATTERN.match(line)
        if match:
            level = len(match.group(1))
            title = match.group(2)
            anchor = match.group(3)
            return (level, title, anchor)

        # Try to match simple header (without anchor)
        match = self.HEADER_SIMPLE_PATTERN.match(line)
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            return (level, title, "")

        return None

    def find_section_for_line(
        self, sections: list[Section], line_number: int
    ) -> Section | None:
        """Find the section containing a specific line

        Args:
            sections: Parsed section list
            line_number: Line number (0-indexed)

        Returns:
            Section containing the line, or None if not found
        """
        for section in reversed(sections):
            # Search from end to find the most specific section (subsection over parent)
            if section.start_line <= line_number <= section.end_line:
                return section
        return None

    def extract_smart_excerpt(
        self, section: Section, query: str, all_lines: list[str]
    ) -> str:
        """Intelligently extract relevant content from a section

        Args:
            section: Section data
            query: Search keyword (for locating match line)
            all_lines: All lines of the complete file

        Returns:
            Extracted content string
        """
        # Extract all lines of the section
        section_lines = all_lines[section.start_line : section.end_line + 1]

        # Short section: return complete content
        if len(section_lines) <= self.MAX_EXCERPT_LINES:
            return '\n'.join(section_lines)

        # Long section: intelligent truncation
        return self._truncate_long_section(section_lines, query)

    def _truncate_long_section(self, section_lines: list[str], query: str) -> str:
        """Truncate long section to key content

        Args:
            section_lines: All lines of the section
            query: Search keyword

        Returns:
            Truncated content with omission markers
        """
        query_lower = query.lower()

        # Find positions of matching lines
        match_positions = []
        for i, line in enumerate(section_lines):
            if query_lower in line.lower():
                match_positions.append(i)

        # Title line (first line)
        title_line = section_lines[0]

        # If no match found, return title + beginning content
        if not match_positions:
            # Return title + first few lines + omission marker
            intro_end = min(self.MAX_EXCERPT_LINES, len(section_lines))
            intro_lines = section_lines[:intro_end]
            omitted = len(section_lines) - intro_end

            if omitted > 0:
                intro_lines.append(f"\n[... {omitted} lines omitted ...]")

            return '\n'.join(intro_lines)

        # Extract centered on first match
        first_match = match_positions[0]

        # Calculate extraction range (preserve title line)
        # If match is near the beginning, start from title
        if first_match <= self.CONTEXT_LINES_BEFORE + 1:
            end = min(self.MAX_EXCERPT_LINES, len(section_lines))
            omitted_after = len(section_lines) - end

            result_lines = [title_line]
            result_lines.extend(section_lines[1:end])

            if omitted_after > 0:
                result_lines.append(f"\n[... {omitted_after} lines omitted ...]")

            return '\n'.join(result_lines)

        # If match is near the end
        if first_match >= len(section_lines) - self.CONTEXT_LINES_AFTER - 1:
            # Calculate content lines to show (excluding title)
            content_lines_to_show = min(
                self.MAX_EXCERPT_LINES - 1,  # Exclude title line
                len(section_lines) - 1  # Exclude title line
            )
            content_start = len(section_lines) - content_lines_to_show
            omitted_before = content_start - 1  # Exclude title line

            result_lines = [title_line]

            if omitted_before > 0:
                result_lines.append(f"\n[... {omitted_before} lines omitted ...]")

            result_lines.extend(section_lines[content_start:])

            return '\n'.join(result_lines)

        # Match is in the middle
        # Preserve title + context around match line
        context_start = max(1, first_match - self.CONTEXT_LINES_BEFORE)
        context_end = min(
            len(section_lines), first_match + self.CONTEXT_LINES_AFTER + 1
        )
        omitted_before = context_start - 1
        omitted_after = len(section_lines) - context_end

        result_lines = [title_line]

        if omitted_before > 0:
            result_lines.append(f"\n[... {omitted_before} lines omitted ...]")

        result_lines.extend(section_lines[context_start:context_end])

        if omitted_after > 0:
            result_lines.append(f"\n[... {omitted_after} lines omitted ...]")

        return '\n'.join(result_lines)
