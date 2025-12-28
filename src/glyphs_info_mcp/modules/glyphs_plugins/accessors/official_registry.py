# encoding: utf-8
"""
Official Registry - Glyphs official plugin registry manager

Features:
- Downloads plugin info from official registry
- 24-hour TTL cache mechanism
- URL parsing (extracts author and repository name)
- Cache version management (v1.0 → v2.0 auto-upgrade)
"""

import json
import logging
import plistlib
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional
import httpx

from glyphs_info_mcp.shared.core.scoring_weights import (
    SCORE_EXACT_MATCH,
    SCORE_TITLE_MATCH,
    SCORE_NAME_MATCH,
    SCORE_OWNER_MATCH,
    SCORE_DESC_MATCH,
)
from glyphs_info_mcp.shared.core.query_utils import normalize_for_matching, tokenize_query


logger = logging.getLogger(__name__)


class OfficialRegistry:
    """Official plugin registry manager"""

    # Official plugin registry URL (plist format)
    OFFICIAL_PACKAGES_URL = "https://raw.githubusercontent.com/schriftgestalt/glyphs-packages/glyphs3/packages.plist"

    # Cache TTL (24 hours)
    CACHE_TTL_HOURS = 24

    # Current cache version
    CURRENT_CACHE_VERSION = "2.0"

    # Relevance scoring weights (imported from shared module, kept as attributes for backward compatibility)
    SCORE_EXACT_MATCH = SCORE_EXACT_MATCH
    SCORE_TITLE_MATCH = SCORE_TITLE_MATCH
    SCORE_NAME_MATCH = SCORE_NAME_MATCH
    SCORE_OWNER_MATCH = SCORE_OWNER_MATCH
    SCORE_DESC_MATCH = SCORE_DESC_MATCH

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize official registry manager

        Args:
            cache_dir: Cache directory (optional, defaults to modules/glyphs_plugins/data)
        """
        if cache_dir is None:
            # Default cache directory
            module_dir = Path(__file__).parent.parent
            cache_dir = module_dir / "data"

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.cache_path = self.cache_dir / "packages_cache.json"

    def _parse_github_url(self, url: str) -> tuple[str, str]:
        """Parse author and repository name from GitHub URL

        Args:
            url: GitHub URL (e.g., https://github.com/mekkablue/Risorizer)

        Returns:
            (owner, repo_name) tuple

        Examples:
            >>> _parse_github_url("https://github.com/mekkablue/Risorizer")
            ("mekkablue", "Risorizer")

            >>> _parse_github_url("https://github.com/Mark2Mark/Show-Stems/")
            ("Mark2Mark", "Show-Stems")
        """
        if not url:
            return ("", "")

        # Remove trailing slashes
        url = url.rstrip("/")

        # Split URL
        parts = url.split("/")

        # Check if there are enough parts
        if len(parts) < 2:
            return ("", "")

        # Take last two segments as owner and repo_name
        repo_name = parts[-1].removesuffix(".git")
        owner = parts[-2]

        return (owner, repo_name)

    def _enrich_package(self, package: dict) -> dict:
        """Enrich plugin info (pure URL parsing)

        Args:
            package: Original plugin info dictionary

        Returns:
            Enriched plugin info (with owner and repo_name fields added)
        """
        url = package.get("url", "")

        if url:
            owner, repo_name = self._parse_github_url(url)
            package["owner"] = owner
            package["repo_name"] = repo_name
        else:
            package["owner"] = ""
            package["repo_name"] = ""

        return package

    def _is_cache_valid(self) -> bool:
        """Check if cache is valid (within 24 hours)

        Returns:
            Whether cache is valid
        """
        if not self.cache_path.exists():
            return False

        try:
            with open(self.cache_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            # Check cache timestamp
            timestamp_str = cache_data.get("timestamp")
            if not timestamp_str:
                return False

            # Parse timestamp
            cache_time = datetime.fromisoformat(timestamp_str)
            now = datetime.now()

            # Check if TTL exceeded
            if now - cache_time > timedelta(hours=self.CACHE_TTL_HOURS):
                logger.info(f"Cache expired (over {self.CACHE_TTL_HOURS} hours)")
                return False

            return True

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to read cache: {e}")
            return False

    def _upgrade_cache(self, cache_data: dict) -> dict:
        """Upgrade cache format (v1.0 → v2.0)

        Args:
            cache_data: Original cache data

        Returns:
            Upgraded cache data
        """
        cache_version = cache_data.get("cache_version", "1.0")

        # If already v2.0, no upgrade needed
        if cache_version == self.CURRENT_CACHE_VERSION:
            return cache_data

        logger.info(f"Upgrading cache version: {cache_version} → {self.CURRENT_CACHE_VERSION}")

        # Upgrade v1.0 → v2.0: enrich all packages
        packages = cache_data.get("packages", [])
        enriched_packages = [self._enrich_package(pkg.copy()) for pkg in packages]

        # Update version number
        cache_data["cache_version"] = self.CURRENT_CACHE_VERSION
        cache_data["packages"] = enriched_packages

        # Save upgraded cache
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)

        return cache_data

    def _load_from_cache(self) -> Optional[list[dict]]:
        """Load plugin list from cache

        Returns:
            Plugin list, or None if cache is invalid
        """
        if not self._is_cache_valid():
            return None

        try:
            with open(self.cache_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            # Upgrade cache format if needed
            cache_data = self._upgrade_cache(cache_data)

            packages = cache_data.get("packages", [])
            logger.info(f"Loaded {len(packages)} plugins from cache")

            return packages

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to read cache: {e}")
            return None

    def _download_packages(self) -> list[dict]:
        """Download plugin info from official registry (ASCII plist format)

        Returns:
            Plugin list (converted to unified dict format)

        Raises:
            httpx.HTTPError: Download failed
        """
        logger.info(f"Downloading official plugin registry: {self.OFFICIAL_PACKAGES_URL}")

        try:
            response = httpx.get(self.OFFICIAL_PACKAGES_URL, timeout=30.0)
            response.raise_for_status()

            # Use plutil to convert ASCII plist to XML format
            # Built-in macOS tool, supports ASCII/XML/Binary plist conversion
            result = subprocess.run(
                ['plutil', '-convert', 'xml1', '-o', '-', '-'],
                input=response.content,
                capture_output=True,
                check=True
            )

            # Parse converted XML plist
            plist_data = plistlib.loads(result.stdout)

            # Extract plugins array
            plugins = plist_data.get("packages", {}).get("plugins", [])

            # Convert plist format to unified dict format
            packages = []
            for item in plugins:
                package = {
                    "name": item.get("path", ""),
                    "title": item.get("titles", {}).get("en", ""),
                    "url": item.get("url", ""),
                    "description": item.get("descriptions", {}).get("en", ""),
                    "screenshot": item.get("screenshot", "")
                }
                packages.append(package)

            logger.info(f"Download successful: {len(packages)} plugins")

            return packages

        except httpx.HTTPError as e:
            logger.error(f"Download failed: {e}")
            raise
        except subprocess.CalledProcessError as e:
            logger.error(f"plist conversion failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Parse failed: {e}")
            raise

    def _save_to_cache(self, packages: list[dict]) -> None:
        """Save plugin list to cache

        Args:
            packages: Plugin list
        """
        # Enrich all plugin info
        enriched_packages = [self._enrich_package(pkg.copy()) for pkg in packages]

        cache_data = {
            "cache_version": self.CURRENT_CACHE_VERSION,
            "timestamp": datetime.now().isoformat(),
            "packages": enriched_packages
        }

        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Cache updated: {len(enriched_packages)} plugins")

    def fetch_packages(self) -> list[dict]:
        """Get official plugin list (cache-first)

        Returns:
            Plugin list
        """
        # Try to load from cache
        packages = self._load_from_cache()

        if packages is not None:
            return packages

        # Cache invalid, download from network
        try:
            packages = self._download_packages()
            self._save_to_cache(packages)

            # Return enriched data
            return [self._enrich_package(pkg.copy()) for pkg in packages]

        except httpx.HTTPError:
            # Download failed, return empty list
            logger.error("Download failed and no valid cache available")
            return []

    def _calculate_relevance_score(
        self,
        query: str,
        title: str,
        name: str,
        description: str,
        owner: str
    ) -> float:
        """Calculate relevance score (0.0-1.0)

        Scoring strategy:
        - Exact match: 1.0
        - Title match: 0.6
        - Name match: 0.5
        - Author match: 0.4
        - Description match: 0.3

        Supports multi-word search (AND logic): all words must match to score

        Args:
            query: Search query
            title: Plugin title
            name: Plugin name
            description: Plugin description
            owner: Author name

        Returns:
            Relevance score (0.0-1.0)
        """
        score = 0.0

        # Use normalization for comparison (case-insensitive, ignore hyphens/underscores)
        query_norm = normalize_for_matching(query)
        title_norm = normalize_for_matching(title)
        name_norm = normalize_for_matching(name)
        description_norm = normalize_for_matching(description)
        owner_norm = normalize_for_matching(owner)

        # Exact match (highest score) - normalized full query
        if query_norm == title_norm or query_norm == name_norm:
            return self.SCORE_EXACT_MATCH

        # Tokenized search (multi-word AND logic)
        query_words = tokenize_query(query)

        # If no valid words, fall back to entire query string matching
        if not query_words:
            query_words = [query.lower().strip()] if query.strip() else []

        # Combine all searchable text
        all_text = f"{title_norm} {name_norm} {description_norm} {owner_norm}"

        # Check if all words are in the text (AND logic)
        matched_words = 0
        for word in query_words:
            word_norm = normalize_for_matching(word)
            if word_norm in all_text:
                matched_words += 1

        # If not all words match, return 0 score
        if query_words and matched_words < len(query_words):
            return 0.0

        # Calculate score: give different weights based on match location
        for word in query_words:
            word_norm = normalize_for_matching(word)

            if word_norm in title_norm:
                score += self.SCORE_TITLE_MATCH / len(query_words)
            elif word_norm in name_norm:
                score += self.SCORE_NAME_MATCH / len(query_words)
            elif word_norm in owner_norm:
                score += self.SCORE_OWNER_MATCH / len(query_words)
            elif word_norm in description_norm:
                score += self.SCORE_DESC_MATCH / len(query_words)

        # Multi-word match bonus
        if len(query_words) > 1 and matched_words == len(query_words):
            score *= 1.2  # 20% bonus

        # Max 1.0
        return min(self.SCORE_EXACT_MATCH, score)

    def core_search(
        self,
        query: str,
        max_results: int = 10,
        **kwargs: Any
    ) -> list[dict[str, Any]]:
        """Core search function - exclusively for unified search engine

        Args:
            query: Search query
            max_results: Maximum number of results
            **kwargs: Additional parameters (e.g., filter_by_author)

        Returns:
            Structured search result list

        Result structure:
            {
                "title": str,          # Plugin title
                "description": str,    # Description
                "url": str,            # Repository URL
                "owner": str,          # Author
                "repo_name": str,      # Repository name
                "score": float,        # Relevance score (0.0-1.0)
                "type": str,           # "plugin"
                "source": str          # "official_registry"
            }
        """
        # Get plugin list
        packages = self.fetch_packages()

        # Extract author filter parameter
        filter_by_author = kwargs.get("filter_by_author")

        results = []

        for package in packages:
            # Author filtering
            if filter_by_author:
                if package.get("owner", "").lower() != filter_by_author.lower():
                    continue

            # Calculate relevance score
            score = self._calculate_relevance_score(
                query.lower(),
                package.get("title", ""),
                package.get("name", ""),
                package.get("description", ""),
                package.get("owner", "")
            )

            # Only keep results with score (score > 0), unless query is empty
            if score > 0 or not query:
                results.append({
                    "title": package.get("title") or package.get("name"),
                    "description": package.get("description", ""),
                    "url": package.get("url", ""),
                    "owner": package.get("owner", ""),
                    "repo_name": package.get("repo_name", ""),
                    "screenshot": package.get("screenshot", ""),
                    "score": score if query else 0.0,  # Score is 0 for empty query
                    "type": "plugin",
                    "source": "official_registry"
                })

        # Sort by score (descending)
        results.sort(key=lambda x: x["score"], reverse=True)

        # Limit result count
        return results[:max_results]
