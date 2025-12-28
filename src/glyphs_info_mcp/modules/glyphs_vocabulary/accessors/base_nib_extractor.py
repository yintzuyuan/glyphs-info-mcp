"""
Base NIB Extractor - Extract English vocabulary from Base.lproj nib files

In macOS localization mechanism, English UI directly uses compiled .nib files
from Base.lproj, rather than .strings files. This module extracts English vocabulary
from nib files as a supplement to .strings.

Technical details:
- keyedobjects.nib in nib files is Apple Binary Property List format
- Uses plutil to convert to XML then parse
- Extracts key-value pairs (e.g., "210.title" = "View")
"""

import logging
import re
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class BaseNibExtractor:
    """Extract English vocabulary from Base.lproj nib files

    Used to supplement vocabulary missing from en.lproj .strings files,
    such as menu items in MainMenu.nib.
    """

    def __init__(self, resources_path: Path | None = None):
        """Initialize NIB extractor

        Args:
            resources_path: Glyphs resources path (default: /Applications/Glyphs 3.app/Contents/Resources)
        """
        if resources_path is None:
            resources_path = Path("/Applications/Glyphs 3.app/Contents/Resources")

        self.resources_path = Path(resources_path)
        self.base_lproj = self.resources_path / "Base.lproj"
        self._cache: dict[str, str] = {}
        self._is_extracted = False

    @property
    def is_available(self) -> bool:
        """Check if Base.lproj directory exists"""
        return self.base_lproj.exists() and self.base_lproj.is_dir()

    def extract_all_terms(self) -> dict[str, str]:
        """Extract English vocabulary from all nib files

        Returns:
            key-value vocabulary dictionary (e.g., {"210.title": "View"})
        """
        if self._is_extracted:
            return self._cache

        if not self.is_available:
            logger.warning(f"Base.lproj not found: {self.base_lproj}")
            return {}

        def _add_terms_from_path(path: Path) -> None:
            """Helper function: parse nib file and update cache"""
            if path.exists():
                self._cache.update(self._parse_nib(path))

        # Iterate all .nib directories
        for nib_dir in self.base_lproj.iterdir():
            if not nib_dir.is_dir():
                continue

            # Process .nib directories
            if nib_dir.suffix == ".nib":
                _add_terms_from_path(nib_dir / "keyedobjects.nib")
            # Process .storyboardc directories (may contain multiple nibs)
            elif ".storyboardc" in nib_dir.name:
                for sub_item in nib_dir.iterdir():
                    if sub_item.is_file() and sub_item.suffix == ".nib":
                        _add_terms_from_path(sub_item)
                    elif sub_item.is_dir() and sub_item.suffix == ".nib":
                        _add_terms_from_path(sub_item / "keyedobjects.nib")

        self._is_extracted = True
        logger.info(f"Extracted {len(self._cache)} terms from Base.lproj nib files")

        return self._cache

    def _parse_nib(self, nib_path: Path) -> dict[str, str]:
        """Parse a single nib file

        Uses plutil to convert Binary Property List to XML,
        then uses regex to extract key-value pairs.

        Args:
            nib_path: nib file path

        Returns:
            key-value vocabulary dictionary
        """
        try:
            # Use plutil to convert to XML
            result = subprocess.run(
                ["plutil", "-convert", "xml1", "-o", "-", str(nib_path)],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                logger.debug(f"Failed to convert nib: {nib_path}")
                return {}

            # Extract key-value pairs
            # Format: <string>123.title</string>\n<string>Value</string>
            # Or IB ID format: <string>d99-hx-YMa.title</string>\n<string>Value</string>
            pattern = r"<string>([a-zA-Z0-9-]+\.(?:title|label|headerCell\.title))</string>\s*<string>([^<]+)</string>"
            matches = re.findall(pattern, result.stdout)

            return dict(matches)

        except subprocess.TimeoutExpired:
            logger.warning(f"Timeout parsing nib: {nib_path}")
            return {}
        except Exception as e:
            logger.debug(f"Error parsing nib {nib_path}: {e}")
            return {}

    def get_term(self, key: str) -> str | None:
        """Get English vocabulary by key

        Args:
            key: Vocabulary key (e.g., "210.title")

        Returns:
            English vocabulary, or None
        """
        if not self._is_extracted:
            self.extract_all_terms()

        return self._cache.get(key)

    def clear_cache(self) -> None:
        """Clear cache"""
        self._cache.clear()
        self._is_extracted = False
