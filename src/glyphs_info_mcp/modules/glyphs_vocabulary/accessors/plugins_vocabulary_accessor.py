"""
Plugins Vocabulary Accessor - Glyphs plugin UI vocabulary accessor

Scans .strings files from all plugins under /Applications/Glyphs 3.app/Contents/PlugIns/,
providing additional 372+ UI vocabulary multi-locale translations (e.g., tool names, filter names).

Complements UIVocabularyNativeAccessor to provide complete Glyphs UI vocabulary coverage.
"""

import re
from pathlib import Path
from typing import Any


class PluginsVocabularyAccessor:
    """Glyphs plugin vocabulary accessor

    Scans /Applications/Glyphs 3.app/Contents/PlugIns/ directory,
    reads localization string files from each plugin.
    """

    def __init__(
        self,
        plugins_path: Path | None = None,
    ):
        """Initialize plugin vocabulary accessor

        Args:
            plugins_path: PlugIns directory path (default: /Applications/Glyphs 3.app/Contents/PlugIns)
        """
        if plugins_path is None:
            plugins_path = Path(
                "/Applications/Glyphs 3.app/Contents/PlugIns"
            )

        self.plugins_path = Path(plugins_path)
        self._cache: dict[str, dict[str, str]] = {}
        self._plugin_names: list[str] | None = None

    def _discover_plugins(self) -> list[str]:
        """Discover all plugins containing localization resources

        Returns:
            List of plugin names
        """
        if not self.plugins_path.exists():
            return []

        plugins = []
        for plugin_dir in self.plugins_path.iterdir():
            if not plugin_dir.is_dir():
                continue

            # Check if Resources directory exists
            resources_path = plugin_dir / "Contents" / "Resources"
            if resources_path.exists():
                # Check if any .lproj directory exists
                lproj_dirs = list(resources_path.glob("*.lproj"))
                if lproj_dirs:
                    plugins.append(plugin_dir.name)

        return sorted(plugins)

    def get_plugin_names(self) -> list[str]:
        """Get all plugin names

        Returns:
            List of plugin names
        """
        if self._plugin_names is None:
            self._plugin_names = self._discover_plugins()
        return self._plugin_names

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
        pattern = r'^"([^"]+)"\s*=\s*"([^"]+)";'
        matches = re.findall(pattern, content, re.MULTILINE)

        return dict(matches)

    def _get_plugin_resources_path(self, plugin_name: str) -> Path:
        """Get plugin's Resources path

        Args:
            plugin_name: Plugin name

        Returns:
            Resources directory path
        """
        return self.plugins_path / plugin_name / "Contents" / "Resources"

    def get_plugin_terms(
        self,
        plugin_name: str,
        locale: str = "en",
    ) -> dict[str, str]:
        """Get all vocabulary for a specific plugin

        Args:
            plugin_name: Plugin name
            locale: Locale code

        Returns:
            Key-Value vocabulary dictionary
        """
        resources_path = self._get_plugin_resources_path(plugin_name)
        locale_dir = resources_path / f"{locale}.lproj"

        if not locale_dir.exists():
            return {}

        terms: dict[str, str] = {}
        for strings_file in locale_dir.glob("*.strings"):
            file_terms = self._parse_strings_file(strings_file)
            terms.update(file_terms)

        return terms

    def get_all_terms(self, locale: str = "en") -> dict[str, str]:
        """Get vocabulary from all plugins (merged)

        Uses plugin_name/key format as key to avoid key conflicts between different plugins.

        Args:
            locale: Locale code

        Returns:
            Key-Value vocabulary dictionary, key format is "plugin_name/original_key"
        """
        # Check cache
        if locale in self._cache:
            return self._cache[locale]

        all_terms: dict[str, str] = {}

        for plugin_name in self.get_plugin_names():
            plugin_terms = self.get_plugin_terms(plugin_name, locale)
            for key, value in plugin_terms.items():
                # Use plugin_name/key format
                prefixed_key = f"{plugin_name}/{key}"
                all_terms[prefixed_key] = value

        # Cache result
        self._cache[locale] = all_terms

        return all_terms

    def get_all_terms_flat(self, locale: str = "en") -> dict[str, str]:
        """Get vocabulary from all plugins (flattened, no prefix)

        Note: If different plugins have the same key, later ones will override earlier ones.

        Args:
            locale: Locale code

        Returns:
            Key-Value vocabulary dictionary
        """
        all_terms: dict[str, str] = {}

        for plugin_name in self.get_plugin_names():
            plugin_terms = self.get_plugin_terms(plugin_name, locale)
            all_terms.update(plugin_terms)

        return all_terms

    def search_term(
        self,
        term: str,
        locale: str = "en",
    ) -> list[dict[str, Any]]:
        """Search vocabulary (supports fuzzy matching)

        Args:
            term: Search term
            locale: Search locale

        Returns:
            List of matching vocabulary, each element contains key, value, plugin
        """
        results = []
        search_term = term.lower()

        for plugin_name in self.get_plugin_names():
            plugin_terms = self.get_plugin_terms(plugin_name, locale)

            for key, value in plugin_terms.items():
                if (
                    search_term in key.lower()
                    or search_term in value.lower()
                ):
                    results.append({
                        "key": key,
                        "value": value,
                        "plugin": plugin_name,
                    })

        return results

    def get_statistics(self) -> dict[str, Any]:
        """Get plugin vocabulary statistics

        Returns:
            Statistics information dictionary
        """
        plugins = self.get_plugin_names()
        total_terms = 0
        plugin_stats = {}

        for plugin_name in plugins:
            terms = self.get_plugin_terms(plugin_name, "en")
            count = len(terms)
            if count > 0:
                plugin_stats[plugin_name] = count
                total_terms += count

        return {
            "plugin_count": len(plugins),
            "total_terms": total_terms,
            "plugins": plugin_stats,
        }
