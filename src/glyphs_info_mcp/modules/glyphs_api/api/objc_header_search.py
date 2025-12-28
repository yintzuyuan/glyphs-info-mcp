#!/usr/bin/env python3
"""
Objective-C Header Search Engine

TDD Green Phase: Implement minimum functionality to pass tests
"""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

# Dynamically import HeaderParser
current_dir = Path(__file__).parent
parser_module_file = current_dir / "objc_header_parser.py"


def _load_parser_module() -> ModuleType:
    """Load the parser module dynamically"""
    spec = importlib.util.spec_from_file_location("objc_header_parser", parser_module_file)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {parser_module_file}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


parser_module = _load_parser_module()
HeaderParser: type[Any] = parser_module.HeaderParser


class HeaderSearchEngine:
    """Header search engine core functionality"""

    def __init__(self) -> None:
        self.headers_data: list[dict[str, Any]] = []
        self.parser = HeaderParser()

    def add_header(self, header_data: dict[str, Any]) -> None:
        """Add Header data to search index

        Args:
            header_data: Parsed Header data
        """
        self.headers_data.append(header_data)

    def search(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
        """Search Headers

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of search results
        """
        if not query.strip():
            return []

        query_lower = query.lower().strip()
        results = []

        for header_data in self.headers_data:
            matches = self._find_matches(header_data, query_lower)
            results.extend(matches)

        # Sort by relevance score
        results.sort(key=lambda x: x['relevance_score'], reverse=True)

        return results[:max_results]

    def build_index_from_directory(self, headers_path: Path) -> None:
        """Build complete index from directory

        Args:
            headers_path: Headers directory path
        """
        if not headers_path.exists():
            return

        for header_file in headers_path.glob("*.h"):
            try:
                parsed_data = self.parser.parse_file(header_file)
                self.add_header(parsed_data)
            except Exception as e:
                # Skip files that cannot be parsed, but log the error
                print(f"Failed to parse {header_file}: {e}", file=sys.stderr)

    def get_indexed_files_count(self) -> int:
        """Get number of files in index"""
        return len(self.headers_data)

    def _find_matches(self, header_data: dict[str, Any], query_lower: str) -> list[dict[str, Any]]:
        """Find matching items in a single Header"""
        matches = []

        # File name matching
        file_stem = header_data.get('file_stem', '').lower()
        if query_lower == file_stem:
            matches.append({
                'file_name': header_data.get('file_name', ''),
                'relevance_score': 1.0,
                'match_type': 'file_name',
                'matched_content': header_data.get('file_name', '')
            })
        elif query_lower in file_stem:
            # Partial file name matching
            matches.append({
                'file_name': header_data.get('file_name', ''),
                'relevance_score': 0.85,
                'match_type': 'file_name',
                'matched_content': header_data.get('file_name', '')
            })

        # Class name matching
        for interface in header_data.get('interfaces', []):
            interface_name = interface.get('name', '').lower()
            if query_lower in interface_name:
                score = 0.9 if query_lower == interface_name else 0.7
                matches.append({
                    'file_name': header_data.get('file_name', ''),
                    'relevance_score': score,
                    'match_type': 'class_name',
                    'matched_content': interface.get('name', '')
                })

        # Method name matching
        for method in header_data.get('methods', []):
            method_name = method.get('name', '').lower()
            if query_lower in method_name:
                score = 0.85 if query_lower == method_name else 0.6
                matches.append({
                    'file_name': header_data.get('file_name', ''),
                    'relevance_score': score,
                    'match_type': 'method',
                    'matched_content': method.get('name', '')
                })

        # Property name matching
        for prop in header_data.get('properties', []):
            prop_name = prop.get('name', '').lower()
            if query_lower in prop_name:
                score = 0.8 if query_lower == prop_name else 0.55
                matches.append({
                    'file_name': header_data.get('file_name', ''),
                    'relevance_score': score,
                    'match_type': 'property',
                    'matched_content': prop.get('name', '')
                })

        # Comment content matching
        for comment in header_data.get('comments', []):
            comment_text = comment.get('text', '').lower()
            if query_lower in comment_text:
                matches.append({
                    'file_name': header_data.get('file_name', ''),
                    'relevance_score': 0.4,
                    'match_type': 'comment',
                    'matched_content': comment.get('text', '')[:100] + '...'
                })

        # Multi-word query processing
        if ' ' in query_lower:
            words = query_lower.split()
            combined_score = self._calculate_multi_word_score(header_data, words)
            if combined_score > 0.5:
                matches.append({
                    'file_name': header_data.get('file_name', ''),
                    'relevance_score': combined_score,
                    'match_type': 'multi_word',
                    'matched_content': f"Multiple matches for: {' '.join(words)}"
                })

            # CamelCase matching - check if multiple words appear in the same identifier
            camel_case_score = self._calculate_camel_case_score(header_data, words)
            if camel_case_score > 0.6:
                matches.append({
                    'file_name': header_data.get('file_name', ''),
                    'relevance_score': camel_case_score,
                    'match_type': 'camel_case',
                    'matched_content': f"CamelCase match for: {' '.join(words)}"
                })

        return matches

    def _calculate_multi_word_score(self, header_data: dict[str, Any], words: list[str]) -> float:
        """Calculate combined score for multi-word queries"""
        total_score: float = 0.0
        word_matches = 0

        for word in words:
            if len(word) <= 1:
                continue

            # Check matches in various fields
            file_stem = header_data.get('file_stem', '').lower()
            if word in file_stem:
                total_score += 0.8
                word_matches += 1
                continue

            # Check class names
            for interface in header_data.get('interfaces', []):
                if word in interface.get('name', '').lower():
                    total_score += 0.6
                    word_matches += 1
                    break

            # Check method names (important: fix tokenized search)
            for method in header_data.get('methods', []):
                if word in method.get('name', '').lower():
                    total_score += 0.7  # Higher score for method matches
                    word_matches += 1
                    break

            # Check property names
            for prop in header_data.get('properties', []):
                if word in prop.get('name', '').lower():
                    total_score += 0.65  # Property match score
                    word_matches += 1
                    break

            # Check comments
            for comment in header_data.get('comments', []):
                if word in comment.get('text', '').lower():
                    total_score += 0.3
                    word_matches += 1
                    break

        # If most words have matches, give higher score
        if word_matches >= len(words) * 0.7:
            return min(total_score / len(words), 0.9)

        return 0

    def _calculate_camel_case_score(self, header_data: dict[str, Any], words: list[str]) -> float:
        """Calculate matching score for CamelCase naming"""
        if len(words) < 2:
            return 0.0

        # Create query patterns - combine multiple words into CamelCase patterns
        # Example: ["add", "anchor"] -> "addanchor" and "addAnchor"
        query_patterns = [
            ''.join(words),  # All lowercase: addanchor
            words[0] + ''.join(w.capitalize() for w in words[1:])  # CamelCase: addAnchor
        ]

        best_score: float = 0.0

        # Check method names
        for method in header_data.get('methods', []):
            method_name = method.get('name', '').lower()
            for pattern in query_patterns:
                pattern_lower = pattern.lower()
                if pattern_lower in method_name:
                    score = 0.9 if pattern_lower == method_name else 0.8
                    best_score = max(best_score, score)

        # Check property names
        for prop in header_data.get('properties', []):
            prop_name = prop.get('name', '').lower()
            for pattern in query_patterns:
                pattern_lower = pattern.lower()
                if pattern_lower in prop_name:
                    score = 0.85 if pattern_lower == prop_name else 0.75
                    best_score = max(best_score, score)

        # Check class names
        for interface in header_data.get('interfaces', []):
            interface_name = interface.get('name', '').lower()
            for pattern in query_patterns:
                pattern_lower = pattern.lower()
                if pattern_lower in interface_name:
                    score = 0.8 if pattern_lower == interface_name else 0.7
                    best_score = max(best_score, score)

        return best_score


class HeaderSearchIndex:
    """Search index (for test compatibility)"""

    def __init__(self) -> None:
        self.index: dict[str, dict[str, Any]] = {
            'file_names': {},
            'class_names': {},
            'property_names': {},
            'method_names': {}
        }
        self.search_engine = HeaderSearchEngine()

    def add_header(self, header_data: dict[str, Any]) -> None:
        """Add Header to index"""
        # Add to search engine
        self.search_engine.add_header(header_data)

        # Build index entries (for test verification)
        file_stem = header_data.get('file_stem', '').lower()
        self.index['file_names'][file_stem] = header_data

        for interface in header_data.get('interfaces', []):
            class_name = interface.get('name', '').lower()
            self.index['class_names'][class_name] = header_data

        for prop in header_data.get('properties', []):
            prop_name = prop.get('name', '').lower()
            self.index['property_names'][prop_name] = header_data

        for method in header_data.get('methods', []):
            method_name = method.get('name', '').lower()
            self.index['method_names'][method_name] = header_data

    def search(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
        """Search"""
        return self.search_engine.search(query, max_results)


class HeaderSearchModule:
    """Header search module (integrated with unified search engine)"""

    def __init__(self) -> None:
        self.search_engine: Any = None
        self.header_search_engine = HeaderSearchEngine()

    def search_headers(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
        """Search Headers"""
        # If vocabulary translation search engine exists, preprocess first
        processed_query = query
        if self.search_engine and self.search_engine.query_processor:
            processed_query, _ = self.search_engine.query_processor.preprocess_query(query)

        return self.header_search_engine.search(processed_query, max_results)
