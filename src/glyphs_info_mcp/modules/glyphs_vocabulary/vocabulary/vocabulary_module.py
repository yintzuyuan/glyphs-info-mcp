#!/usr/bin/env python3
"""
Glyphs UI Vocabulary Module

Provides comprehensive Glyphs 3.app UI terminology multi-language translation (988+ terms, 14 locales).
Directly reads Glyphs internal localization strings, zero maintenance, real-time sync.
"""

import logging
import sys
from pathlib import Path
from typing import Any

# Use shared core library - dynamic path calculation
project_root = Path(__file__).parent.parent.parent.parent
shared_core_path = str(project_root / "src" / "shared")
if shared_core_path not in sys.path:
    sys.path.insert(0, shared_core_path)

from glyphs_info_mcp.shared.core.base_module import BaseMCPModule
from glyphs_info_mcp.modules.glyphs_vocabulary.accessors.ui_vocabulary_native_accessor import (
    UIVocabularyNativeAccessor,
)
from glyphs_info_mcp.modules.glyphs_vocabulary.accessors.plugins_vocabulary_accessor import (
    PluginsVocabularyAccessor,
)
from glyphs_info_mcp.modules.glyphs_vocabulary.accessors.framework_vocabulary_accessor import (
    FrameworkVocabularyAccessor,
)

logger = logging.getLogger(__name__)


class VocabularyModule(BaseMCPModule):
    """Glyphs UI Vocabulary Module - Native Accessor for Glyphs UI terms"""

    def __init__(self, name: str = "vocabulary", data_path: Path | None = None):
        super().__init__(name, data_path)

        # Initialize UI Vocabulary Native Accessor
        self.ui_accessor = UIVocabularyNativeAccessor()

        # Initialize Plugins Vocabulary Accessor (plugin vocabulary)
        self.plugins_accessor = PluginsVocabularyAccessor()

        # Initialize Framework Vocabulary Accessor (GlyphsCore.framework vocabulary)
        self.framework_accessor = FrameworkVocabularyAccessor()

        # Reverse index: value.lower() -> (key, locale, source)
        # For O(1) time complexity _find_english_key lookup
        # source: "app", "framework", "plugins"
        self._reverse_term_map: dict[str, tuple[str, str, str]] = {}

    def initialize(self) -> bool:
        """Initialize the vocabulary module"""
        try:
            # Verify Glyphs resources path exists
            if not self.ui_accessor.resources_path.exists():
                logger.warning(
                    f"Glyphs resources path not found: {self.ui_accessor.resources_path}"
                )
                logger.warning("Please ensure Glyphs 3.app is installed.")
                # Still mark as initialized, but functionality will be limited
                self.is_initialized = True
                return True

            # Verify at least one locale is available
            if not self.ui_accessor.supported_locales:
                logger.error("No locales found in Glyphs resources")
                return False

            self.is_initialized = True

            # Build reverse index (English priority, maintain Hub-and-Spoke correctness)
            self._build_reverse_term_map()

            logger.info(
                f"Vocabulary module initialized with {len(self.ui_accessor.supported_locales)} locales"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to initialize vocabulary module: {e}")
            return False

    def get_tools(self) -> dict[str, Any]:
        """Get available tools as dictionary"""
        return {
            "vocab_search_ui_term": self.search_ui_term,
            "vocab_get_translation": self.get_ui_translation,
            "vocab_list_ui_categories": self.list_ui_categories,
            "vocab_translate_term": self.translate_term_tool,
        }

    # === Glyphs UI Vocabulary Tools (Native Accessor) ===

    def translate_term_tool(self, term: str, target_locale: str = "auto") -> str:
        """
        [GLYPHS UI] Translate Glyphs UI term to specified locale

        Universal translation tool supporting bidirectional translation across 14 locales.
        Auto-detects source language and translates to target locale.
        Limited to Glyphs UI vocabulary (988+ terms).

        Supports fuzzy search: if no exact match, returns the best match with suggestions.

        Args:
            term: Term to translate (any supported locale)
            target_locale: Target locale code, "auto" means auto-translate to English
                          Supported locales: en, zh-Hant, zh-Hans, ja, ko, de, fr, es,
                                            it, pt, ru, sv, no, da

        Returns:
            Translation result (if term exists in Glyphs UI vocabulary)

        Examples:
            - Chinese to English: translate_term_tool("取消") → "Cancel"
            - English to Japanese: translate_term_tool("Cancel", "ja") → "キャンセル"
            - Fuzzy match: translate_term_tool("錨點") → finds related terms and translates
        """
        if not term.strip():
            return "## ⚠️ Please provide a term to translate"

        if not self.is_initialized:
            return "## ⚠️ Vocabulary module not initialized\n\nPlease ensure Glyphs 3.app is installed."

        try:
            # First try exact match (using status-aware translation method)
            result, found, _source = self._translate_term_with_status(term, target_locale)

            # Determine if term was found based on found status
            if found:
                # Exact match successful
                target_name = "English" if target_locale == "auto" else target_locale

                # Check if it's a "keep original" case
                display_result = result
                if result == term:
                    display_result = f"{result} (unchanged)"

                output = [
                    f"## ✅ Translation Successful\n",
                    f"**Original:** {term}",
                    f"**Translation:** {display_result}",
                    f"**Target Locale:** {target_name}",
                    "",
                    "---",
                    f"_Source: Glyphs 3.app UI Vocabulary_"
                ]
                return "\n".join(output)

            # Exact match failed, try fuzzy search
            fuzzy_results = self._fuzzy_find_term(term, max_results=5)

            if not fuzzy_results:
                return f"## ⚠️ Term not found\n\n\"{term}\" is not in Glyphs UI vocabulary (988+ terms).\n\n**Note**: This tool only translates Glyphs UI interface terms, not a general text translator."

            # Has fuzzy match results
            best_match = fuzzy_results[0]
            target_name = "English" if target_locale == "auto" else target_locale
            final_target_locale = "en" if target_locale == "auto" else target_locale

            # Get best match translation
            best_key = best_match["key"]
            best_value = best_match["value"]
            best_source = best_match.get("source", "app")
            score_percent = int(best_match["score"] * 100)

            # Use Hub-and-Spoke architecture: get translation from corresponding accessor based on source
            if best_source == "plugins":
                plugin_terms = self.plugins_accessor.get_all_terms_flat(final_target_locale)
                translated_value = plugin_terms.get(best_key)
            elif best_source == "framework":
                framework_terms = self.framework_accessor.get_all_terms(final_target_locale)
                translated_value = framework_terms.get(best_key)
            else:
                translated_value = self.ui_accessor.get_term_by_key(best_key, final_target_locale)

            if not translated_value:
                translated_value = best_value  # Fallback to original

            # Format output (fuzzy match)
            output = [
                f"## ✅ Translation Successful (Fuzzy Match)\n",
                f"**Query:** {term}",
                f"**Best Match:** {best_value}",
                f"**Translation:** {translated_value}",
                f"**Target Locale:** {target_name}",
                f"**Relevance:** {score_percent}%",
            ]

            # If there are other related terms, show suggestions
            if len(fuzzy_results) > 1:
                output.append("")
                output.append("---")
                output.append("")
                output.append("### Other Related Terms\n")
                output.append("| Original | Translation | Relevance |")
                output.append("|----------|-------------|-----------|")

                for match in fuzzy_results[1:]:
                    match_key = match["key"]
                    match_value = match["value"]
                    match_source = match.get("source", "app")
                    match_score = int(match["score"] * 100)

                    # Use Hub-and-Spoke architecture: get translation from corresponding accessor based on source
                    if match_source == "plugins":
                        plugin_terms = self.plugins_accessor.get_all_terms_flat(final_target_locale)
                        match_translated = plugin_terms.get(match_key)
                    elif match_source == "framework":
                        framework_terms = self.framework_accessor.get_all_terms(final_target_locale)
                        match_translated = framework_terms.get(match_key)
                    else:
                        match_translated = self.ui_accessor.get_term_by_key(match_key, final_target_locale)

                    if not match_translated:
                        match_translated = match_value

                    output.append(f"| {match_value} | {match_translated} | {match_score}% |")

            output.append("")
            output.append("---")
            output.append(f"_Source: Glyphs 3.app UI Vocabulary_")

            return "\n".join(output)

        except Exception as e:
            logger.error(f"Failed to translate term '{term}': {e}", exc_info=True)
            return "## ❌ Translation Error\n\nAn internal error occurred, please try again later."

    def search_ui_term(self, term: str, locale: str = "zh-Hant") -> str:
        """
        [GLYPHS UI] Search Glyphs internal UI vocabulary (Hub-and-Spoke architecture)

        Directly reads Glyphs 3.app internal localization strings, providing 988+ UI term translations.
        Uses English as intermediary language to ensure translation accuracy.

        Args:
            term: Search term (supports English or other locales)
            locale: Target locale (default: zh-Hant)

        Returns:
            Matching terms and their translations
        """
        if not term.strip():
            return "Please provide a search term"

        try:
            # Bidirectional search: English and target locale (main app)
            en_results = self.ui_accessor.search_term(term, source_locale="en")
            target_results = []

            if locale != "en":
                target_results = self.ui_accessor.search_term(
                    term, source_locale=locale
                )

            # Framework vocabulary search
            framework_en_results = self.framework_accessor.search_term(term, locale="en")
            framework_target_results = []
            if locale != "en":
                framework_target_results = self.framework_accessor.search_term(term, locale=locale)

            # Plugin vocabulary search
            plugin_en_results = self.plugins_accessor.search_term(term, locale="en")
            plugin_target_results = []
            if locale != "en":
                plugin_target_results = self.plugins_accessor.search_term(term, locale=locale)

            # Merge results and deduplicate, using Hub-and-Spoke architecture for translations
            all_results = {}

            # 1. Main app vocabulary
            for result in en_results + target_results:
                key = result["key"]
                if key not in all_results:
                    # Use get_term_by_key to directly get English and target locale values
                    en_value = self.ui_accessor.get_term_by_key(key, "en")
                    target_value = self.ui_accessor.get_term_by_key(key, locale)

                    if en_value:
                        all_results[key] = {
                            "source": en_value,
                            "target": target_value if target_value else en_value,
                            "key": key,
                            "source_type": "app",
                        }

            # 2. Framework vocabulary
            for result in framework_en_results + framework_target_results:
                key = result["key"]
                unique_key = f"framework/{key}"

                if unique_key not in all_results:
                    # Get translation from framework
                    framework_en_terms = self.framework_accessor.get_all_terms("en")
                    framework_target_terms = self.framework_accessor.get_all_terms(locale)

                    en_value = framework_en_terms.get(key)
                    target_value = framework_target_terms.get(key)

                    if en_value:
                        all_results[unique_key] = {
                            "source": en_value,
                            "target": target_value if target_value else en_value,
                            "key": key,
                            "source_type": "framework",
                        }

            # 3. Plugin vocabulary
            for result in plugin_en_results + plugin_target_results:
                key = result["key"]
                plugin_name = result.get("plugin", "unknown")
                unique_key = f"{plugin_name}/{key}"

                if unique_key not in all_results:
                    # Get translation from plugin
                    plugin_en_terms = self.plugins_accessor.get_plugin_terms(plugin_name, "en")
                    plugin_target_terms = self.plugins_accessor.get_plugin_terms(plugin_name, locale)

                    en_value = plugin_en_terms.get(key)
                    target_value = plugin_target_terms.get(key)

                    if en_value:
                        all_results[unique_key] = {
                            "source": en_value,
                            "target": target_value if target_value else en_value,
                            "key": key,
                            "source_type": "plugins",
                            "plugin": plugin_name,
                        }

            if not all_results:
                return f"## ⚠️ No Related Terms Found\n\nNo results found for \"{term}\" in Glyphs UI vocabulary."

            # Format output
            output = [f"## 🔍 Glyphs UI Vocabulary Search: \"{term}\"\n"]
            output.append(f"Found {len(all_results)} related terms:\n")

            for i, (unique_key, trans) in enumerate(all_results.items(), 1):
                output.append(f"**{i}. {trans['source']}** → {trans['target']}")
                source_type = trans.get("source_type", "app")
                if source_type == "plugins":
                    output.append(f"   Key: `{trans['key']}` (Source: {trans.get('plugin', 'plugins')})")
                elif source_type == "framework":
                    output.append(f"   Key: `{trans['key']}` (Source: GlyphsCore.framework)")
                else:
                    output.append(f"   Key: `{trans['key']}`")
                output.append("")

            return "\n".join(output)

        except Exception as e:
            logger.error(f"Failed to search UI term: {e}")
            return f"Error searching UI vocabulary: {str(e)}"

    def get_ui_translation(
        self,
        term: str,
        source_locale: str = "en",
        target_locales: str = "zh-Hant",
    ) -> str:
        """
        [GLYPHS UI] Get Glyphs UI vocabulary multi-locale translation mapping

        Retrieve translations of a UI term across multiple locales simultaneously.
        Searches across: Glyphs.app UI, GlyphsCore.framework, and plugin vocabulary.

        Args:
            term: Term to translate (English or other supported locale)
            source_locale: Source locale (default: en)
            target_locales: Target locales, comma-separated for multiple (default: zh-Hant)
                           Supported locales: en, zh-Hant, zh-Hans, ja, ko, de, fr, es,
                                             it, pt, ru, sv, no, da
                           Examples:
                           - Single: "zh-Hant"
                           - Multiple: "zh-Hant,ja,ko" (CJK languages)
                           - Multiple: "de,fr,es,it" (European languages)

        Returns:
            Translation mapping showing the term in each requested locale

        Examples:
            - get_ui_translation("Cancel", target_locales="zh-Hant,ja,ko")
              → Returns Cancel in Traditional Chinese, Japanese, Korean
            - get_ui_translation("Font Info", target_locales="zh-Hant,zh-Hans")
              → Compare Traditional vs Simplified Chinese translations
        """
        if not term.strip():
            return "Please provide a term to translate"

        try:
            # Parse target locales
            targets = [loc.strip() for loc in target_locales.split(",")]

            # 1. First try main app vocabulary
            translation = self.ui_accessor.get_translation(
                term=term,
                source_locale=source_locale,
                target_locales=targets,
            )
            source_type = "app"

            # 2. If not found in main app, try Framework
            if not translation:
                translation = self._get_framework_translation(
                    term, source_locale, targets
                )
                if translation:
                    source_type = "framework"

            # 3. If not found in Framework, try Plugins
            if not translation:
                translation = self._get_plugins_translation(
                    term, source_locale, targets
                )
                if translation:
                    source_type = "plugins"

            if not translation:
                return f"## ⚠️ Term Not Found\n\n\"{term}\" not found in Glyphs UI vocabulary."

            # Format output
            output = [f"## 🌐 Term Translation: \"{translation['source']}\"\n"]
            output.append(f"**Key:** `{translation['key']}`")
            if source_type == "framework":
                output.append("**Source:** GlyphsCore.framework")
            elif source_type == "plugins":
                plugin_name = translation.get("plugin", "plugins")
                output.append(f"**Source:** {plugin_name}")
            output.append(f"**Source Locale:** {source_locale}")
            output.append("")

            if "translations" in translation:
                output.append("### Translation Reference\n")
                for locale, text in translation["translations"].items():
                    output.append(f"- **{locale}:** {text}")
            else:
                output.append(
                    f"**{translation['target_locale']}:** {translation['target']}"
                )

            return "\n".join(output)

        except Exception as e:
            logger.error(f"Failed to get UI translation: {e}")
            return f"Error getting translation: {str(e)}"

    def list_ui_categories(self) -> str:
        """
        [GLYPHS UI] List Glyphs UI vocabulary file categories

        Returns:
            List of .strings files with usage descriptions
        """
        try:
            # Get English locale .strings files
            en_dir = self.ui_accessor.resources_path / "en.lproj"

            if not en_dir.exists():
                return "## ⚠️ Glyphs Resources Directory Not Found\n\nPlease ensure Glyphs 3.app is installed."

            strings_files = sorted(en_dir.glob("*.strings"))

            if not strings_files:
                return "## ⚠️ No .strings Files Found"

            # Format output
            output = [f"## 📁 Glyphs UI Vocabulary Categories ({len(strings_files)} files)\n"]

            # Sort by file size and display
            file_info: list[dict[str, Any]] = []
            for file_path in strings_files:
                terms = self.ui_accessor._parse_strings_file(file_path)
                file_info.append(
                    {
                        "name": file_path.name,
                        "terms": len(terms),
                        "size": file_path.stat().st_size,
                    }
                )

            # Sort by term count
            file_info.sort(key=lambda x: x["terms"], reverse=True)

            for i, info in enumerate(file_info, 1):
                size_kb = info["size"] / 1024
                output.append(
                    f"**{i}. {info['name']}** - {info['terms']} terms ({size_kb:.1f} KB)"
                )

            # Show total
            total_terms = sum(f["terms"] for f in file_info)
            total_size = sum(f["size"] for f in file_info) / 1024

            output.append("")
            output.append(f"**Total:** {total_terms} terms, {total_size:.1f} KB")

            # Show available locales
            locales = self.ui_accessor.list_available_locales()
            output.append("")
            output.append(f"**Supported Locales:** {', '.join(locales)}")

            return "\n".join(output)

        except Exception as e:
            logger.error(f"Failed to list UI categories: {e}")
            return f"Error listing vocabulary categories: {str(e)}"

    # === get_ui_translation helper methods ===

    def _get_framework_translation(
        self,
        term: str,
        source_locale: str,
        target_locales: list[str],
    ) -> dict[str, Any] | None:
        """Get translation from Framework vocabulary (case-insensitive)

        Args:
            term: Term to translate
            source_locale: Source locale
            target_locales: Target locale list

        Returns:
            Translation result dictionary, or None if term not found
        """
        source_terms = self.framework_accessor.get_all_terms(source_locale)

        # Find key (case-insensitive)
        key = None
        source_value = None
        term_lower = term.lower()

        # First try direct key match
        if term in source_terms:
            key = term
            source_value = source_terms[term]
        else:
            # Reverse lookup key by value (case-insensitive)
            for k, v in source_terms.items():
                if v.lower() == term_lower:
                    key = k
                    source_value = v
                    break

        if key is None:
            return None

        # Multi-locale translation
        translations = {}
        for locale in target_locales:
            target_terms = self.framework_accessor.get_all_terms(locale)
            value = target_terms.get(key)
            translations[locale] = value if value else source_value

        return {
            "key": key,
            "source": source_value,
            "source_locale": source_locale,
            "translations": translations,
        }

    def _get_plugins_translation(
        self,
        term: str,
        source_locale: str,
        target_locales: list[str],
    ) -> dict[str, Any] | None:
        """Get translation from Plugins vocabulary (case-insensitive)

        Args:
            term: Term to translate
            source_locale: Source locale
            target_locales: Target locale list

        Returns:
            Translation result dictionary (with plugin field), or None if term not found
        """
        term_lower = term.lower()

        # Search each plugin
        for plugin_name in self.plugins_accessor.get_plugin_names():
            source_terms = self.plugins_accessor.get_plugin_terms(plugin_name, source_locale)

            # Find key (case-insensitive)
            key = None
            source_value = None

            # First try direct key match
            if term in source_terms:
                key = term
                source_value = source_terms[term]
            else:
                # Reverse lookup key by value (case-insensitive)
                for k, v in source_terms.items():
                    if v.lower() == term_lower:
                        key = k
                        source_value = v
                        break

            if key is not None:
                # Found, get multi-locale translations
                translations = {}
                for locale in target_locales:
                    target_terms = self.plugins_accessor.get_plugin_terms(plugin_name, locale)
                    value = target_terms.get(key)
                    translations[locale] = value if value else source_value

                return {
                    "key": key,
                    "source": source_value,
                    "source_locale": source_locale,
                    "translations": translations,
                    "plugin": plugin_name,
                }

        return None

    def get_module_info(self) -> dict[str, Any]:
        """Get module information"""
        total_terms = 0
        if self.is_initialized and self.ui_accessor.resources_path.exists():
            # Calculate total term count for English locale
            en_terms = self.ui_accessor.get_all_terms(locale="en")
            total_terms = len(en_terms)

        return {
            'name': self.name,
            'type': 'vocabulary',
            'title': '🌐 Glyphs UI Vocabulary',
            'description': 'Glyphs 3.app UI terminology translation (988+ terms, 14 locales)',
            'initialized': self.is_initialized,
            'vocab_count': total_terms,
            'supported_locales': len(self.ui_accessor.supported_locales),
            'tools': ['vocab_search_ui_term', 'vocab_get_translation', 'vocab_list_ui_categories', 'vocab_translate_term']
        }

    # === Hub-and-Spoke Architecture Core Methods ===

    def _build_reverse_term_map(self) -> None:
        """Build reverse index for O(1) time complexity term lookup

        English locale is filled first to ensure Hub-and-Spoke architecture correctness.
        Same value from subsequent locales will not override English mapping.

        Data source priority:
        1. Main app vocabulary (app) - from Glyphs.app Resources
        2. Framework vocabulary (framework) - from GlyphsCore.framework
        3. Plugin vocabulary (plugins) - from Glyphs.app PlugIns
        """
        self._reverse_term_map.clear()

        # English first, ensure Hub-and-Spoke correctness
        locales_by_priority = ["en"] + [
            loc for loc in self.ui_accessor.supported_locales if loc != "en"
        ]

        # 1. Main app vocabulary (priority)
        for locale in locales_by_priority:
            terms = self.ui_accessor.get_all_terms(locale)
            for key, value in terms.items():
                value_lower = value.lower()
                # Only fill if value doesn't exist yet (English priority)
                if value_lower not in self._reverse_term_map:
                    self._reverse_term_map[value_lower] = (key, locale, "app")

        # 2. Framework vocabulary (GlyphsCore.framework)
        for locale in locales_by_priority:
            framework_terms = self.framework_accessor.get_all_terms(locale)
            for key, value in framework_terms.items():
                value_lower = value.lower()
                # Only fill if value doesn't exist yet (main app priority)
                if value_lower not in self._reverse_term_map:
                    self._reverse_term_map[value_lower] = (key, locale, "framework")

        # 3. Plugin vocabulary (supplementary)
        for locale in locales_by_priority:
            # Use flattened terms (without plugin prefix)
            plugin_terms = self.plugins_accessor.get_all_terms_flat(locale)
            for key, value in plugin_terms.items():
                value_lower = value.lower()
                # Only fill if value doesn't exist yet (main app and framework priority)
                if value_lower not in self._reverse_term_map:
                    self._reverse_term_map[value_lower] = (key, locale, "plugins")

        logger.debug(f"Built reverse term map with {len(self._reverse_term_map)} entries (app + framework + plugins)")

    def _find_english_key(self, term: str) -> tuple[str | None, str | None, str | None]:
        """Find English key corresponding to term in any locale (O(1) time complexity)

        Core method for Hub-and-Spoke architecture. Regardless of input locale,
        returns the corresponding English key for subsequent translation.

        Uses pre-built reverse index, reducing query from O(N) to O(1).

        Args:
            term: Term in any locale

        Returns:
            tuple: (english_key, source_locale, source)
                   english_key: Corresponding key, None if not found
                   source_locale: Locale where match was found
                   source: Source ("app" or "plugins")
        """
        if not self.is_initialized:
            return None, None, None

        result = self._reverse_term_map.get(term.lower())
        return result if result else (None, None, None)

    # === Fuzzy Search Functionality ===

    def _fuzzy_find_term(
        self, term: str, max_results: int = 5
    ) -> list[dict[str, Any]]:
        """Fuzzy search terms and return relevance-sorted results (Hub-and-Spoke architecture)

        Prioritizes English search to ensure official vocabulary standards.
        Only searches other locales if English not found.

        Searches both main app vocabulary and plugin vocabulary.

        Args:
            term: Search term
            max_results: Maximum results to return (default 5)

        Returns:
            list of {
                'key': str,           # Term key
                'value': str,         # Matched value
                'locale': str,        # Source locale
                'score': float,       # Relevance score (0.0-1.0)
                'match_type': str,    # 'exact', 'partial'
                'source': str         # 'app', 'framework', 'plugins'
            }
        """
        if not self.is_initialized:
            return []

        results: list[dict[str, Any]] = []
        seen_keys: set[str] = set()
        term_lower = term.lower()

        def _calculate_score(value: str) -> tuple[float, str]:
            """Calculate relevance score"""
            value_lower = value.lower()
            if value_lower == term_lower:
                return 1.0, "exact"
            elif term_lower in value_lower:
                # Partial match: calculate score based on position and ratio
                position_factor = 1.0 - (value_lower.index(term_lower) / len(value_lower))
                ratio_factor = len(term) / len(value)
                score = 0.5 + (position_factor * 0.25) + (ratio_factor * 0.25)
                return min(score, 0.95), "partial"
            return 0.0, ""

        def _process_results(search_results: list[dict[str, Any]], locale: str, source: str = "app") -> None:
            """Process search results"""
            for result in search_results:
                key = result["key"]
                value = result["value"]

                # Skip already processed keys or empty values
                if key in seen_keys or len(value) == 0:
                    continue

                score, match_type = _calculate_score(value)
                if score == 0.0:
                    continue

                seen_keys.add(key)
                results.append({
                    "key": key,
                    "value": value,
                    "locale": locale,
                    "score": round(score, 2),
                    "match_type": match_type,
                    "source": source,
                })

        # 1. Priority search in main app English (Hub-and-Spoke core)
        en_results = self.ui_accessor.search_term(term, source_locale="en")
        _process_results(en_results, "en", "app")

        # 2. Also search Framework English
        framework_en_results = self.framework_accessor.search_term(term, locale="en")
        _process_results(framework_en_results, "en", "framework")

        # 3. Also search plugin English
        plugin_en_results = self.plugins_accessor.search_term(term, locale="en")
        for result in plugin_en_results:
            _process_results([result], "en", "plugins")

        # 4. Only search other locales if English not found
        if not results:
            for locale in self.ui_accessor.supported_locales:
                if locale == "en":
                    continue
                # Main app other locales
                locale_results = self.ui_accessor.search_term(term, source_locale=locale)
                _process_results(locale_results, locale, "app")
                # Framework other locales
                framework_locale_results = self.framework_accessor.search_term(term, locale=locale)
                _process_results(framework_locale_results, locale, "framework")
                # Plugin other locales
                plugin_locale_results = self.plugins_accessor.search_term(term, locale=locale)
                for result in plugin_locale_results:
                    _process_results([result], locale, "plugins")
                if results:
                    break  # Stop when found

        # Sort by score (descending)
        results.sort(key=lambda x: x["score"], reverse=True)

        # Limit result count
        return results[:max_results]

    # === Backward Compatibility Interface (for QueryProcessor) ===

    def _translate_term_with_status(
        self, term: str, target_locale: str = "auto"
    ) -> tuple[str, bool, str | None]:
        """Translate term and return status information

        Same translation logic as translate_term, but additionally returns
        whether the term was found. Used by translate_term_tool to distinguish
        between "no translation" and "translation equals original".

        Args:
            term: Term to translate
            target_locale: Target locale code

        Returns:
            tuple: (translated_value, found, source)
                - translated_value: Translation result (or original)
                - found: True means term exists in vocabulary
                - source: Source ("app", "framework", "plugins") or None
        """
        if not self.is_initialized:
            return term, False, None

        try:
            # Use Hub-and-Spoke core method to find English key and source
            english_key, _, source = self._find_english_key(term)

            if not english_key:
                return term, False, None

            # Determine target locale
            final_target_locale = "en" if target_locale == "auto" else target_locale

            # Get translation from corresponding accessor based on source
            if source == "plugins":
                plugin_terms = self.plugins_accessor.get_all_terms_flat(final_target_locale)
                translated = plugin_terms.get(english_key)
            elif source == "framework":
                framework_terms = self.framework_accessor.get_all_terms(final_target_locale)
                translated = framework_terms.get(english_key)
            else:
                translated = self.ui_accessor.get_term_by_key(english_key, final_target_locale)

            # Found key means term exists, even if translation equals original
            if translated:
                return translated, True, source
            else:
                return term, True, source  # Key exists but target locale has no translation

        except Exception as e:
            logger.error(f"Failed to translate term: {e}")
            return term, False, None

    def translate_term(self, term: str, target_locale: str = "auto") -> str:
        """Universal translation method: all translations go through English (Hub-and-Spoke architecture)

        Core translation method supporting bidirectional translation across all 14 locales.
        Uses English as the hub language (official vocabulary standard).

        Supports both main app vocabulary and plugin vocabulary translation.

        Args:
            term: Term to translate (any supported locale)
            target_locale: Target locale code, "auto" means translate to English

        Returns:
            Translated term, or original if not found

        Examples:
            translate_term("取消") → "Cancel" (zh-Hant → en, auto)
            translate_term("Cancel", "ja") → "キャンセル" (en → ja)
            translate_term("キャンセル") → "Cancel" (ja → en, auto)
            translate_term("Cancel", "zh-Hant") → "取消" (en → zh-Hant)
            translate_term("選取工具") → "Select" (zh-Hant → en, from plugins)
        """
        translated, _, _ = self._translate_term_with_status(term, target_locale)
        return translated

    @property
    def en_to_zh(self) -> dict[str, str]:
        """Backward compatibility property: English to Traditional Chinese term mapping

        Note: This is a dynamically generated property based on UIVocabularyNativeAccessor
        Returns all English UI terms and their Traditional Chinese translations
        """
        if not self.is_initialized:
            return {}

        try:
            en_terms = self.ui_accessor.get_all_terms(locale="en")
            zh_terms = self.ui_accessor.get_all_terms(locale="zh-Hant")

            # Build English to Traditional Chinese mapping
            result = {}
            for key, en_value in en_terms.items():
                if key in zh_terms:
                    result[en_value] = zh_terms[key]

            return result
        except Exception as e:
            logger.error(f"Failed to generate en_to_zh mapping: {e}")
            return {}

    def translate_to_english(self, term: str) -> str:
        """Translate term in any supported language to English (backward compatibility method)

        This method is retained for backward compatibility.
        New code should use translate_term(term, target_locale="en") directly

        Args:
            term: Term in any supported language (supports 14 locales)

        Returns:
            Corresponding English term, or original if not found
        """
        return self.translate_term(term, target_locale="en")

    def translate_to_chinese(self, en_term: str) -> str:
        """Translate English term to Chinese (backward compatibility method)

        Args:
            en_term: English term

        Returns:
            Corresponding Chinese term, or original if not found
        """
        return self.translate_term(en_term, target_locale="zh-Hant")
