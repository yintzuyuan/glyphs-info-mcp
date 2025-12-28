"""
Framework Vocabulary Accessor - GlyphsCore.framework vocabulary accessor

Reads localization string files (.strings) from
/Applications/Glyphs 3.app/Contents/Frameworks/GlyphsCore.framework/
providing Glyphs core framework UI vocabulary translations.

Includes:
- Localizable.strings - Core UI vocabulary
- customParameterDescriptions.strings - Custom Parameter descriptions
- FeatureNames.strings - OpenType Feature names
- LanguageTags.strings - Language tags
- categories.strings - Character categories
- Panose.strings - PANOSE classification system
- InspectorView*.strings - Inspector panel vocabulary
- Scripts.strings - Writing system names

Unlike the main app's UIVocabularyNativeAccessor, GlyphsCore.framework's
.strings files already contain complete NIB translations, no additional Base.lproj NIB processing needed.
"""

import re
from pathlib import Path
from typing import Any


class FrameworkVocabularyAccessor:
    """GlyphsCore.framework vocabulary accessor

    Reads /Applications/Glyphs 3.app/Contents/Frameworks/GlyphsCore.framework/
    Versions/A/Resources/*.lproj/*.strings providing core framework UI vocabulary translations.
    """

    def __init__(
        self,
        framework_path: Path | None = None,
    ):
        """Initialize Framework vocabulary accessor

        Args:
            framework_path: GlyphsCore.framework path
                (default: /Applications/Glyphs 3.app/Contents/Frameworks/GlyphsCore.framework)
        """
        if framework_path is None:
            framework_path = Path(
                "/Applications/Glyphs 3.app/Contents/Frameworks/"
                "GlyphsCore.framework/Versions/A/Resources"
            )

        self.framework_path = Path(framework_path)
        self.supported_locales = self._discover_locales()
        self._cache: dict[str, dict[str, str]] = {}
        self._strings_files: list[str] | None = None

    def _discover_locales(self) -> list[str]:
        """Auto-discover available locales

        Returns:
            List of locale codes (e.g., ['en', 'zh-Hant', 'ja'])
        """
        if not self.framework_path.exists():
            return []

        locales = []
        for lproj_dir in self.framework_path.glob("*.lproj"):
            if lproj_dir.is_dir():
                locale = lproj_dir.name.replace(".lproj", "")
                if locale != "Base":  # Exclude Base.lproj
                    locales.append(locale)

        return sorted(locales)

    def get_strings_files(self) -> list[str]:
        """Get all .strings file names

        Returns:
            List of .strings file names
        """
        if self._strings_files is not None:
            return self._strings_files

        if not self.framework_path.exists():
            return []

        # Get file list from English locale directory
        en_dir = self.framework_path / "en.lproj"
        if not en_dir.exists():
            return []

        files = []
        for strings_file in en_dir.glob("*.strings"):
            files.append(strings_file.name)

        self._strings_files = sorted(files)
        return self._strings_files

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

        # Parse .strings format: "key" = "value";
        pattern = r'^"([^"]+)"\s*=\s*"([^"]+)";'
        matches = re.findall(pattern, content, re.MULTILINE)

        return dict(matches)

    def get_terms_from_file(
        self,
        filename: str,
        locale: str = "en",
    ) -> dict[str, str]:
        """Get vocabulary from a specific .strings file

        Args:
            filename: .strings file name
            locale: Locale code

        Returns:
            Key-Value vocabulary dictionary
        """
        locale_dir = self.framework_path / f"{locale}.lproj"
        file_path = locale_dir / filename

        return self._parse_strings_file(file_path)

    def get_all_terms(self, locale: str = "en") -> dict[str, str]:
        """Get all vocabulary for a specific locale

        Args:
            locale: Locale code (default: 'en')

        Returns:
            Key-Value vocabulary dictionary
        """
        # Check cache
        if locale in self._cache:
            return self._cache[locale]

        locale_dir = self.framework_path / f"{locale}.lproj"
        if not locale_dir.exists():
            return {}

        # Read all .strings files
        all_terms: dict[str, str] = {}

        for strings_file in locale_dir.glob("*.strings"):
            terms = self._parse_strings_file(strings_file)
            all_terms.update(terms)

        # Cache result
        self._cache[locale] = all_terms

        return all_terms

    def search_term(
        self,
        term: str,
        locale: str = "en",
    ) -> list[dict[str, str]]:
        """Search vocabulary (supports fuzzy matching)

        Args:
            term: Search term
            locale: Search locale

        Returns:
            List of matching vocabulary, each element contains key and value
        """
        all_terms = self.get_all_terms(locale)
        results = []

        search_term = term.lower()

        for key, value in all_terms.items():
            # Case-insensitive search on both key and value
            if search_term in key.lower() or search_term in value.lower():
                results.append({"key": key, "value": value})

        return results

    def get_statistics(self) -> dict[str, Any]:
        """Get vocabulary statistics

        Returns:
            Statistics information dictionary
        """
        files = self.get_strings_files()
        total_terms = 0
        file_stats = {}

        for filename in files:
            terms = self.get_terms_from_file(filename, "en")
            count = len(terms)
            if count > 0:
                file_stats[filename] = count
                total_terms += count

        return {
            "total_terms": total_terms,
            "files": file_stats,
            "file_count": len(files),
            "locale_count": len(self.supported_locales),
            "locales": self.supported_locales,
        }
