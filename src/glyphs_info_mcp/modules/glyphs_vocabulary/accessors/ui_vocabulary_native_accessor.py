"""
UI Vocabulary Native Accessor - Glyphs internal UI vocabulary native accessor

Directly reads Glyphs 3.app internal localization string files (.strings),
providing 988+ UI vocabulary multi-locale translations (14 locales).

Zero maintenance, real-time sync, complete Glyphs UI interface coverage.

For English (en), additionally extracts vocabulary from Base.lproj nib files,
supplementing menu items missing from .strings files (e.g., MainMenu).
"""

import re
from pathlib import Path
from typing import Any

from glyphs_info_mcp.modules.glyphs_vocabulary.accessors.base_nib_extractor import (
    BaseNibExtractor,
)


class UIVocabularyNativeAccessor:
    """Glyphs UI vocabulary native accessor

    Directly reads /Applications/Glyphs 3.app/Contents/Resources/*.lproj/*.strings
    providing complete Glyphs UI interface vocabulary multi-locale translations.
    """

    def __init__(
        self,
        resources_path: Path | None = None,
    ):
        """Initialize UI vocabulary accessor

        Args:
            resources_path: Glyphs resources path (default: /Applications/Glyphs 3.app/Contents/Resources)
        """
        if resources_path is None:
            resources_path = Path(
                "/Applications/Glyphs 3.app/Contents/Resources"
            )

        self.resources_path = Path(resources_path)
        self.supported_locales = self._discover_locales()
        self._cache: dict[str, dict[str, str]] = {}

        # Initialize Base.lproj nib extractor (for supplementing English vocabulary)
        self._base_nib_extractor = BaseNibExtractor(self.resources_path)

    def _discover_locales(self) -> list[str]:
        """Auto-discover available locales

        Returns:
            List of locale codes (e.g., ['en', 'zh-Hant', 'ja'])
        """
        if not self.resources_path.exists():
            return []

        locales = []
        for lproj_dir in self.resources_path.glob("*.lproj"):
            if lproj_dir.is_dir():
                locale = lproj_dir.name.replace(".lproj", "")
                if locale != "Base":  # Exclude Base.lproj (Interface Builder)
                    locales.append(locale)

        return sorted(locales)

    def _parse_strings_file(self, file_path: Path) -> dict[str, str]:
        """Parse .strings file

        Args:
            file_path: .strings file path

        Returns:
            Key-Value vocabulary dictionary
        """
        if not file_path.exists():
            return {}

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return {}

        # Parse .strings format: \"key\" = \"value\";
        # Supports multi-line, comments, special characters
        pattern = r'^"([^"]+)"\s*=\s*"([^"]+)";'
        matches = re.findall(pattern, content, re.MULTILINE)

        return dict(matches)

    def get_all_terms(self, locale: str = "en") -> dict[str, str]:
        """Get all vocabulary for a specific locale

        For English (en), merges vocabulary from Base.lproj NIB files,
        supplementing menu items and other UI elements missing from .strings files.

        Args:
            locale: Locale code (default: 'en')

        Returns:
            Key-Value vocabulary dictionary
        """
        # Check cache
        if locale in self._cache:
            return self._cache[locale]

        # Read all .strings files
        all_terms: dict[str, str] = {}
        locale_dir = self.resources_path / f"{locale}.lproj"

        if not locale_dir.exists():
            return {}

        for strings_file in locale_dir.glob("*.strings"):
            terms = self._parse_strings_file(strings_file)
            all_terms.update(terms)

        # For English, merge Base.lproj NIB vocabulary
        # .strings takes priority (don't override existing keys)
        if locale == "en" and self._base_nib_extractor.is_available:
            nib_terms = self._base_nib_extractor.extract_all_terms()
            for key, value in nib_terms.items():
                if key not in all_terms:
                    all_terms[key] = value

        # Cache result
        self._cache[locale] = all_terms

        return all_terms

    def get_term_by_key(self, key: str, locale: str = "en") -> str | None:
        """Query vocabulary by key exactly (with Base.lproj fallback)

        For English locale, if not found in .strings, will automatically query
        from Base.lproj nib files (supplementing missing menu items like MainMenu).

        Args:
            key: Vocabulary key (e.g., "210.title")
            locale: Target locale

        Returns:
            Vocabulary translation, or None if not found
        """
        # 1. First query from .strings files
        all_terms = self.get_all_terms(locale)
        if key in all_terms:
            return all_terms[key]

        # 2. If English and not found, try querying from Base.lproj nib files
        if locale == "en" and self._base_nib_extractor.is_available:
            return self._base_nib_extractor.get_term(key)

        return None

    def get_translation(
        self,
        term: str,
        source_locale: str = "en",
        target_locale: str | None = None,
        target_locales: list[str] | None = None,
    ) -> dict[str, Any] | None:
        """Get vocabulary translation

        Supports single locale or multi-locale translation comparison.

        Args:
            term: Vocabulary to translate (can be key or value)
            source_locale: Source locale
            target_locale: Target locale (single)
            target_locales: Target locale list (multi-locale)

        Returns:
            Translation result dictionary containing key, source, target/translations, etc.
            Returns None if vocabulary doesn't exist
        """
        source_terms = self.get_all_terms(source_locale)

        # Find key (supports reverse lookup by value)
        key = None
        source_value = None

        # First try direct key match
        if term in source_terms:
            key = term
            source_value = source_terms[term]
        else:
            # Reverse lookup key by value (case-insensitive)
            term_lower = term.lower()
            for k, v in source_terms.items():
                if v.lower() == term_lower:
                    key = k
                    source_value = v
                    break

        if key is None:
            return None

        # Single locale translation
        if target_locale is not None:
            target_value = self.get_term_by_key(key, target_locale)
            if target_value is None:
                target_value = source_value  # Fallback to original

            return {
                "key": key,
                "source": source_value,
                "target": target_value,
                "source_locale": source_locale,
                "target_locale": target_locale,
            }

        # Multi-locale translation
        if target_locales is not None:
            translations = {}
            for locale in target_locales:
                value = self.get_term_by_key(key, locale)
                translations[locale] = value if value else source_value

            return {
                "key": key,
                "source": source_value,
                "source_locale": source_locale,
                "translations": translations,
            }

        return None

    def search_term(
        self,
        term: str,
        source_locale: str = "en",
    ) -> list[dict[str, str]]:
        """Search vocabulary (supports fuzzy matching)

        Args:
            term: Search term
            source_locale: Search locale

        Returns:
            List of matching vocabulary, each element contains key and value
        """
        all_terms = self.get_all_terms(source_locale)
        results = []

        search_term = term.lower()

        for key, value in all_terms.items():
            # Case-insensitive search on both key and value
            if (
                search_term in key.lower()
                or search_term in value.lower()
            ):
                results.append({"key": key, "value": value})

        return results

    def list_available_locales(self) -> list[str]:
        """List all available locales

        Returns:
            List of locale codes
        """
        return self.supported_locales
