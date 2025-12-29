"""
Chapter Finder (revised) - Resolves file mapping issues
"""

import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ChapterFinder:
    """Improved chapter finder"""

    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.index_file = data_path / "index.md"
        self._load_toc()

    def _load_toc(self) -> None:
        """Load table of contents"""
        self.toc: dict[str, dict[str, Any]] = {}
        self.file_mapping: dict[str, str] = {}

        if self.index_file.exists():
            try:
                content = self.index_file.read_text(encoding='utf-8')
                self._parse_toc(content)
                self._build_smart_file_mapping()  # Use new smart mapping algorithm
            except Exception as e:
                logger.error(f"Failed to load table of contents: {e}")

    def _parse_toc(self, content: str) -> None:
        """Parse table of contents structure"""
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Match various chapter title formats
            patterns = [
                r'^#+\s*(\d+(?:\.\d+)*)\.\s*(.+)',  # ## 11. Interpolation
                r'^-\s*(\d+(?:\.\d+)*)\s+(.+)',     # - 11.1 Setting up Multiple Masters
                r'^\s*(\d+(?:\.\d+)*)\.\s*(.+)'     # 11. Interpolation
            ]

            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    chapter_num = match.group(1)
                    chapter_title = match.group(2).strip()

                    self.toc[chapter_num] = {
                        'title': chapter_title,
                        'file': None,
                        'content': None
                    }
                    break

    def _build_smart_file_mapping(self) -> None:
        """Smart file mapping algorithm"""
        # Step 1: Collect and analyze all available files
        available_files = {}
        for file_path in self.data_path.glob("*.md"):
            if file_path.name == "index.md":
                continue

            file_info = self._analyze_file(file_path.name)
            if file_info:
                available_files[file_path.name] = file_info

        # Step 2: Find best match for each chapter
        for chapter_num, chapter_info in self.toc.items():
            best_match = self._find_best_file_match(
                chapter_num,
                chapter_info,
                available_files
            )

            if best_match:
                self.file_mapping[chapter_num] = best_match
                self.toc[chapter_num]['file'] = best_match
                logger.debug(f"Mapped chapter {chapter_num} to file {best_match}")

        logger.info(f"Smart mapping complete: {len(self.file_mapping)} chapter-file mappings")

    def _analyze_file(self, filename: str) -> dict | None:
        """Analyze filename and extract info"""
        # Match format: topic_subtopic.md (simplified filename)
        match = re.match(r'(.+)\.md', filename)
        if not match:
            return None

        topic_path = match.group(1)
        topic_parts = topic_path.split('_')

        return {
            'filename': filename,
            'topic_path': topic_path,
            'topic_parts': topic_parts,
            'main_topic': topic_parts[0] if topic_parts else '',
            'subtopic_count': len(topic_parts),
            'is_main_topic': len(topic_parts) == 1,  # Only one topic word
            'full_topic': ' '.join(topic_parts)
        }

    def _find_best_file_match(self, chapter_num: str, chapter_info: dict, available_files: dict) -> str | None:
        """Find best file match for a specific chapter"""
        chapter_title = chapter_info['title'].lower()
        chapter_parts = chapter_num.split('.')
        is_main_chapter = len(chapter_parts) == 1  # Main chapter vs sub-chapter

        candidates = []

        for filename, file_info in available_files.items():
            score = self._calculate_match_score(
                chapter_num, chapter_title, is_main_chapter, file_info
            )

            if score > 0:
                candidates.append((filename, score, file_info))

        if not candidates:
            return None

        # Sort by score, select best match
        candidates.sort(key=lambda x: x[1], reverse=True)

        # For main chapters, verify if topic file was selected
        if is_main_chapter and candidates:
            best_candidate = candidates[0]
            # If best candidate is not a topic file, try to find one
            if not best_candidate[2]['is_main_topic']:
                main_topic_candidates = [c for c in candidates if c[2]['is_main_topic']]
                if main_topic_candidates:
                    return main_topic_candidates[0][0]

        return candidates[0][0]

    def _calculate_match_score(self, chapter_num: str, chapter_title: str,
                             is_main_chapter: bool, file_info: dict) -> int:
        """Calculate match score between file and chapter"""
        score = 0

        # Basic topic match
        main_topic = file_info['main_topic']
        if main_topic in chapter_title or chapter_title in main_topic:
            score += 50

        # Full title match
        full_topic = file_info['full_topic']
        if chapter_title in full_topic or full_topic in chapter_title:
            score += 30

        # Main chapters prefer topic files
        if is_main_chapter:
            if file_info['is_main_topic']:
                score += 100  # Significant bonus
            else:
                score -= 50   # Significant penalty
        else:
            # Sub-chapters prefer specific files
            if not file_info['is_main_topic']:
                score += 20

        # Keyword match
        chapter_words = set(chapter_title.split())
        topic_words = set(file_info['full_topic'].split())

        common_words = chapter_words.intersection(topic_words)
        score += len(common_words) * 10

        # Exact match bonus
        if chapter_title == file_info['full_topic']:
            score += 200

        return score

    def find(self, chapter_path: str) -> str:
        """Find chapter content"""
        if not chapter_path.strip():
            return "Please provide a chapter number (e.g., '11' or '4.1')"

        chapter_path = chapter_path.strip()

        # Exact match
        if chapter_path in self.toc:
            return self._get_chapter_content(chapter_path)

        # Fuzzy match
        matches = self._fuzzy_match(chapter_path)
        if matches:
            if len(matches) == 1:
                return self._get_chapter_content(matches[0]['num'])
            else:
                return self._format_matches(chapter_path, matches)

        return f"Chapter '{chapter_path}' not found\n\n💡 Use `get_handbook_toc()` to view the complete table of contents"

    def _get_chapter_content(self, chapter_num: str) -> str:
        """Get chapter content"""
        chapter_info = self.toc[chapter_num]
        file_name = self.file_mapping.get(chapter_num)

        if file_name:
            content = self._load_chapter_content(file_name)
            if content:
                return f"# {chapter_num}. {chapter_info['title']}\n\n{content}"
            else:
                return f"❌ Failed to read file `{file_name}` for chapter {chapter_num}. {chapter_info['title']}"

        return f"📄 No corresponding file found for chapter {chapter_num}. {chapter_info['title']}"

    def _load_chapter_content(self, filename: str) -> str | None:
        """Load and clean chapter content"""
        file_path = self.data_path / filename
        if not file_path.exists():
            return None

        try:
            content = file_path.read_text(encoding='utf-8')
            return self._clean_content(content)
        except Exception as e:
            logger.error(f"Failed to read file {filename}: {e}")
            return None

    def _clean_content(self, content: str) -> str:
        """Clean content formatting"""
        lines = content.split('\n')
        cleaned_lines = []
        skip_nav = True

        for line in lines:
            # Skip navigation links at the beginning until main title is found
            if skip_nav:
                if line.startswith('# '):
                    skip_nav = False
                    cleaned_lines.append(line)
                continue

            # Skip navigation links at the end
            if line.startswith('- [') and ('Previous' in line or 'Next' in line):
                continue

            cleaned_lines.append(line)

        # Remove trailing empty lines
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()

        return '\n'.join(cleaned_lines)

    def _fuzzy_match(self, query: str) -> list[dict]:
        """Improved fuzzy matching"""
        matches = []
        query_lower = query.lower()

        for chapter_num, chapter_info in self.toc.items():
            score = 0

            # Chapter number match
            if query == chapter_num:
                score = 100
            elif query in chapter_num:
                score = 80
            elif chapter_num.startswith(query):
                score = 70

            # Title match
            title_lower = chapter_info['title'].lower()
            if query_lower == title_lower:
                score = max(score, 90)
            elif query_lower in title_lower:
                score = max(score, 60)

            # Keyword match
            query_words = set(query_lower.split())
            title_words = set(title_lower.split())
            common_words = query_words.intersection(title_words)

            if common_words:
                score = max(score, len(common_words) * 20)

            if score > 0:
                matches.append({
                    'num': chapter_num,
                    'title': chapter_info['title'],
                    'score': score,
                    'has_file': chapter_num in self.file_mapping
                })

        matches.sort(key=lambda x: (x['score'], x['has_file']), reverse=True)
        return matches[:5]

    def _format_matches(self, query: str, matches: list[dict]) -> str:
        """Format match results"""
        output = [f"🔍 Found {len(matches)} chapters related to '{query}':\n"]

        for i, match in enumerate(matches, 1):
            status = "✅" if match['has_file'] else "📄"
            output.append(f"{i}. {status} **{match['num']}.** {match['title']}")

        if matches:
            best = matches[0]
            output.append(f"\n💡 Use `find_chapter_content(\"{best['num']}\")` to view the most relevant content")

        return '\n'.join(output)

    def get_toc(self) -> str:
        """Get enhanced table of contents"""
        if not self.toc:
            return "❌ Table of contents not loaded or empty"

        output = ["# 📚 Glyphs Handbook Complete Table of Contents\n"]

        # Smart sorting
        def sort_key(chapter_num: str) -> list[int]:
            parts = [int(x) for x in chapter_num.split('.')]
            return parts + [0] * (10 - len(parts))

        sorted_chapters = sorted(self.toc.keys(), key=sort_key)

        for chapter_num in sorted_chapters:
            chapter_info = self.toc[chapter_num]
            level = len(chapter_num.split('.'))
            indent = "  " * (level - 1)

            # File status indicator
            if chapter_num in self.file_mapping:
                status = "✅"
                file_info = f" `{self.file_mapping[chapter_num]}`" if level == 1 else ""
            else:
                status = "📄"
                file_info = ""

            output.append(f"{indent}{status} **{chapter_num}.** {chapter_info['title']}{file_info}")

        output.extend([
            "\n**Status Legend**:",
            "✅ Has complete content file",
            "📄 Table of contents entry only (may be included in other chapters)",
            "\n💡 **Usage**:",
            "- `find_chapter_content(\"11\")` - View chapter content",
            "- `search_handbook(\"interpolation\")` - Search related topics"
        ])

        return '\n'.join(output)

    def debug_mapping(self) -> dict:
        """Debug mapping information"""
        available_files = list(self.data_path.glob("*.md"))
        mapped_files = set(self.file_mapping.values())
        unmapped_files = [f.name for f in available_files
                         if f.name != "index.md" and f.name not in mapped_files]

        return {
            "total_chapters": len(self.toc),
            "mapped_chapters": len(self.file_mapping),
            "available_files": len(available_files) - 1,  # Exclude index.md
            "unmapped_files": unmapped_files,
            "mapping_details": {num: file for num, file in self.file_mapping.items()},
            "unmapped_chapters": [num for num in self.toc.keys() if num not in self.file_mapping]
        }
