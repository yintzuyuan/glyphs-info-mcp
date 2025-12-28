#!/usr/bin/env python3
"""
Query Processor - Handles query preprocessing and output postprocessing
Refactored from term_processor.py, implements SearchEngine's QueryProcessor interface
"""

# mypy: ignore-errors

import logging
import re

logger = logging.getLogger(__name__)


class QueryProcessorImpl:
    """Query Processor Implementation - Implements SearchEngine's QueryProcessor interface

    Responsible for:
    1. Input preprocessing: Automatically convert Chinese queries to English for search
    2. Output postprocessing: Automatically convert terms based on user language
    """

    def __init__(self, vocabulary_module):
        """Initialize query processor

        Args:
            vocabulary_module: VocabularyModule instance providing translation services
        """
        self.vocab = vocabulary_module
        self.glyphs_terms_pattern = None
        self._build_term_patterns()

    def _build_term_patterns(self):
        """Build regex patterns for Glyphs professional terms"""
        if not self.vocab.is_initialized:
            return

        # Get all English terms and build regex pattern
        en_terms = list(self.vocab.en_to_zh.keys())
        if en_terms:
            # Sort by length, longer terms match first (avoid partial match issues)
            en_terms.sort(key=len, reverse=True)
            # Escape special characters and build pattern
            escaped_terms = [re.escape(term) for term in en_terms]
            self.glyphs_terms_pattern = re.compile(
                r"\b(" + "|".join(escaped_terms) + r")\b", re.IGNORECASE
            )

    def detect_user_language(self, query: str) -> str:
        """Detect user language

        Args:
            query: Query string

        Returns:
            'zh-TW' or 'en'
        """
        # Simple logic: contains Chinese characters = Chinese user
        if re.search(r"[\u4e00-\u9fff]", query):
            return "zh-TW"
        return "en"

    def preprocess_query(self, query: str) -> tuple[str, str]:
        """Preprocess query string, handle mixed Chinese-English input

        Args:
            query: Original query string

        Returns:
            (processed_query, user_language) - Processed query and detected language
        """
        if not query or not query.strip():
            return query, "en"

        user_language = self.detect_user_language(query)

        # Use unified mixed input processing logic (including pure English and Chinese)
        processed_query = self._translate_chinese_terms_in_query(query)

        logger.debug(
            f"Query preprocessing: '{query}' -> '{processed_query}' (language: {user_language})"
        )

        return processed_query, user_language

    def _translate_chinese_terms_in_query(self, query: str) -> str:
        """Intelligently process mixed input query, prioritize AI-provided English terms

        Args:
            query: Mixed Chinese-English query string

        Returns:
            Optimized pure English query string
        """
        if not self.vocab.is_initialized:
            return query

        # Parse mixed input
        chinese_terms, english_terms = self._parse_mixed_input(query)

        # Standardize English terms (deduplicate, unify format)
        standardized_english = self._standardize_english_terms(english_terms)

        # Detect semantic coverage, find Chinese concepts not covered by English
        uncovered_chinese = self._detect_uncovered_chinese_terms(
            chinese_terms, standardized_english
        )

        # Translate uncovered Chinese terms
        translated_chinese = self._translate_uncovered_chinese_terms(uncovered_chinese)

        # Merge final results
        final_terms = standardized_english + translated_chinese
        result = " ".join(final_terms).strip()

        logger.debug(f"Mixed input processing: '{query}' -> '{result}'")
        logger.debug(f"  Chinese terms: {chinese_terms}")
        logger.debug(f"  English terms: {english_terms} -> {standardized_english}")
        logger.debug(f"  Uncovered Chinese: {uncovered_chinese} -> {translated_chinese}")

        return result

    def _parse_mixed_input(self, query: str) -> tuple[list[str], list[str]]:
        """Parse mixed input, separate Chinese and English terms

        Args:
            query: Mixed input query string

        Returns:
            (chinese_terms, english_terms) - Separated Chinese and English term lists
        """
        words = query.split()
        chinese_terms = []
        english_terms = []

        for word in words:
            clean_word = re.sub(r"[^\w\u4e00-\u9fff]", "", word)
            if not clean_word:
                continue

            # Determine if Chinese or English
            if re.search(r"[\u4e00-\u9fff]", clean_word):
                chinese_terms.append(clean_word)
            else:
                english_terms.append(clean_word)

        return chinese_terms, english_terms

    def _standardize_english_terms(self, english_terms: list[str]) -> list[str]:
        """Standardize English terms, deduplicate and unify format

        Args:
            english_terms: English term list

        Returns:
            Standardized English term list
        """
        if not english_terms:
            return []

        # Sort by length first, keep longer terms
        sorted_terms = sorted(english_terms, key=len, reverse=True)

        standardized = []
        seen_concepts = set()

        for term in sorted_terms:
            term_lower = term.lower()

            # Handle singular/plural unification
            singular = self._get_singular_form(term_lower)

            # Avoid duplicate concepts
            if singular not in seen_concepts:
                standardized.append(term)
                seen_concepts.add(singular)

        return standardized

    def _get_singular_form(self, term: str) -> str:
        """Get singular form of a term

        Args:
            term: English term

        Returns:
            Singular form
        """
        term = term.lower()

        # Handle irregular plurals
        irregular_plurals = {
            "children": "child",
            "feet": "foot",
            "teeth": "tooth",
            "men": "man",
            "women": "woman",
        }

        if term in irregular_plurals:
            return irregular_plurals[term]

        # Handle standard plurals
        if term.endswith("ies") and len(term) > 4:
            return term[:-3] + "y"
        elif term.endswith("es") and len(term) > 3:
            # Handle special es endings
            if term.endswith("ches") or term.endswith("shes") or term.endswith("xes"):
                return term[:-2]
            else:
                return term[:-2]
        elif term.endswith("s") and len(term) > 3:
            return term[:-1]

        return term

    def _detect_uncovered_chinese_terms(
        self, chinese_terms: list[str], english_terms: list[str]
    ) -> list[str]:
        """Detect Chinese terms not covered by English terms

        Args:
            chinese_terms: Chinese term list
            english_terms: English term list

        Returns:
            List of uncovered Chinese terms
        """
        if not chinese_terms:
            return []

        uncovered = []
        english_concepts = set(term.lower().rstrip("s") for term in english_terms)

        for chinese_term in chinese_terms:
            # Try to decompose compound word and check coverage
            is_covered = self._is_chinese_term_covered(chinese_term, english_concepts)

            if not is_covered:
                uncovered.append(chinese_term)

        return uncovered

    def _is_chinese_term_covered(
        self, chinese_term: str, english_concepts: set
    ) -> bool:
        """Check if Chinese term is covered by English concepts

        Args:
            chinese_term: Chinese term
            english_concepts: English concept set (lowercase, plural 's' removed)

        Returns:
            Whether covered
        """
        # Try direct translation check
        direct_translation = self.vocab.translate_to_english(chinese_term)
        if direct_translation != chinese_term:
            # Has direct translation, check if in English concepts
            direct_concept = direct_translation.lower().rstrip("s")
            if direct_concept in english_concepts:
                return True

        # Try compound word decomposition
        decomposed = self._decompose_chinese_compound(chinese_term)
        if len(decomposed) > 1:
            # Check if all decomposed concepts are covered
            covered_count = 0
            for part in decomposed:
                part_translation = self.vocab.translate_to_english(part)
                if part_translation != part:
                    part_concept = part_translation.lower().rstrip("s")
                    if part_concept in english_concepts:
                        covered_count += 1

            # If most concepts are covered, consider the whole term covered
            return covered_count >= len(decomposed) * 0.8  # 80% coverage threshold

        return False

    def _decompose_chinese_compound(self, chinese_term: str) -> list[str]:
        """Decompose Chinese compound word

        Args:
            chinese_term: Chinese compound word

        Returns:
            List of decomposed words
        """
        if not self.vocab.is_initialized:
            return [chinese_term]

        # Use greedy longest match to decompose
        result = []
        i = 0

        while i < len(chinese_term):
            matched = False
            # Start from longest possible match
            for length in range(min(6, len(chinese_term) - i), 0, -1):
                candidate = chinese_term[i : i + length]
                if self.vocab.translate_to_english(candidate) != candidate:
                    # Found term in vocabulary
                    result.append(candidate)
                    i += length
                    matched = True
                    break

            if not matched:
                # No match found, skip current character
                i += 1

        return result if result else [chinese_term]

    def _translate_uncovered_chinese_terms(self, chinese_terms: list[str]) -> list[str]:
        """Translate uncovered Chinese terms

        Args:
            chinese_terms: List of uncovered Chinese terms

        Returns:
            List of translated English terms
        """
        translated = []

        for term in chinese_terms:
            # First try direct translation
            direct_translation = self.vocab.translate_to_english(term)
            if direct_translation != term:
                translated.append(direct_translation)
            else:
                # Try decomposition and translation
                decomposed = self._decompose_chinese_compound(term)
                if len(decomposed) > 1:
                    # Translate each part
                    parts = []
                    for part in decomposed:
                        part_translation = self.vocab.translate_to_english(part)
                        if part_translation != part:
                            parts.append(part_translation)

                    if parts:
                        translated.extend(parts)
                    else:
                        # Decomposition failed, keep original
                        translated.append(term)
                else:
                    # Cannot process, keep original
                    translated.append(term)

        return translated

    def postprocess_output(self, content: str, user_language: str) -> str:
        """Postprocess output content based on user language

        Args:
            content: Original output content
            user_language: User language ('zh-TW' or 'en')

        Returns:
            Processed output content
        """
        if not content or user_language == "en":
            return content

        # Chinese user: Replace English terms with Chinese
        return self._replace_english_terms_with_chinese(content)

    def _replace_english_terms_with_chinese(self, content: str) -> str:
        """Replace English Glyphs terms in content with Chinese

        Args:
            content: Content containing English terms

        Returns:
            Content with replaced terms
        """
        if not self.vocab.is_initialized or not self.glyphs_terms_pattern:
            return content

        def replace_term(match):
            en_term = match.group(1)
            zh_term = self.vocab.translate_to_chinese(en_term)
            return zh_term if zh_term != en_term else en_term

        # Use regex to replace all matching terms
        processed_content = self.glyphs_terms_pattern.sub(replace_term, content)

        return processed_content

    def extract_terms_from_query(self, query: str) -> list[str]:
        """Extract term list from query (for multi-search)

        Args:
            query: Query string

        Returns:
            Extracted term list
        """
        user_language = self.detect_user_language(query)

        # Basic tokenization: split by space
        basic_terms = [term.strip() for term in query.split() if term.strip()]

        if user_language == "zh-TW":
            # Chinese query: try to translate each word
            translated_terms = []
            for term in basic_terms:
                clean_term = re.sub(r"[^\w\u4e00-\u9fff]", "", term)
                if clean_term:
                    translated = self.vocab.translate_to_english(clean_term)
                    translated_terms.append(translated)
            return translated_terms

        return basic_terms

    def get_translation_hints(self, query: str) -> dict[str, str]:
        """Get translation hints for query terms (for debugging)

        Args:
            query: Query string

        Returns:
            Term translation mapping dictionary
        """
        if not self.vocab.is_initialized:
            return {}

        user_language = self.detect_user_language(query)
        words = [re.sub(r"[^\w\u4e00-\u9fff]", "", word) for word in query.split()]

        hints = {}
        for word in words:
            if word:
                if user_language == "zh-TW":
                    translated = self.vocab.translate_to_english(word)
                    if translated != word:
                        hints[word] = translated
                else:
                    translated = self.vocab.translate_to_chinese(word)
                    if translated != word:
                        hints[word] = translated

        return hints


class QueryProcessorFactory:
    """Query Processor Factory class"""

    @staticmethod
    def create(vocabulary_module) -> QueryProcessorImpl:
        """Create query processor instance

        Args:
            vocabulary_module: VocabularyModule instance

        Returns:
            QueryProcessorImpl instance
        """
        return QueryProcessorImpl(vocabulary_module)


# Backward compatibility: keep original TermProcessor class name
TermProcessor = QueryProcessorImpl
TermProcessorFactory = QueryProcessorFactory
