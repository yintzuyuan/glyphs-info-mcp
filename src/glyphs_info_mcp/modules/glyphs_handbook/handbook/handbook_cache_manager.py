"""
HandbookCacheManager - Glyphs Handbook cache manager

Manages stable cache and dynamic update cache path selection and update logic.
"""

import importlib.util
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Dynamic import of HandbookScraper (avoid circular import)
_scraper_file = Path(__file__).parent / "handbook_scraper.py"
_spec = importlib.util.spec_from_file_location("handbook_scraper", _scraper_file)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Cannot load module spec from {_scraper_file}")
_scraper_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_scraper_module)
HandbookScraper = _scraper_module.HandbookScraper


class HandbookCacheManager:
    """Handbook cache manager"""

    def __init__(
        self,
        project_root: Optional[Path] = None,
        cache_max_age_days: int = 7,
    ):
        """
        Initialize cache manager

        Args:
            project_root: Project root directory (auto-detect if not specified)
            cache_max_age_days: Maximum cache age (in days)
        """
        if project_root is None:
            # Auto-detect project root directory
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent.parent

        self.project_root = project_root
        self.cache_max_age_days = cache_max_age_days

        # Cache directories
        self.stable_cache_dir = project_root / "data" / "handbook-cache" / "stable"
        self.fresh_cache_dir = project_root / "data" / "handbook-cache" / "fresh"

        # Cache info files
        self.stable_info_file = self.stable_cache_dir / ".cache-info.json"
        self.fresh_info_file = self.fresh_cache_dir / ".cache-info.json"

    def get_active_cache_path(self) -> Path:
        """
        Get the currently active cache path

        Priority:
        1. fresh cache (if exists and fresh)
        2. stable cache (fallback)

        Returns:
            Cache directory path
        """
        if self.is_fresh_cache_valid():
            logger.info(
                f"Using fresh cache: {self.fresh_cache_dir}"
            )
            return self.fresh_cache_dir

        logger.info(
            f"Using stable cache (fallback): {self.stable_cache_dir}"
        )
        return self.stable_cache_dir

    def is_fresh_cache_valid(self) -> bool:
        """
        Check if fresh cache is valid

        Conditions:
        - fresh cache directory exists
        - .cache-info.json exists
        - cache not expired (< cache_max_age_days)
        - contains at least one .md file

        Returns:
            True if cache is valid, otherwise False
        """
        if not self.fresh_cache_dir.exists():
            logger.debug("fresh cache directory does not exist")
            return False

        if not self.fresh_info_file.exists():
            logger.debug("fresh cache info file does not exist")
            return False

        # Check if MD files exist
        md_files = list(self.fresh_cache_dir.glob("*.md"))
        if not md_files:
            logger.debug("no MD files in fresh cache")
            return False

        # Check cache age
        try:
            cache_info = self._load_cache_info(self.fresh_info_file)
            cache_date_str = cache_info.get("cache_date")
            if not cache_date_str:
                logger.warning("cache info missing cache_date field")
                return False

            cache_date = datetime.fromisoformat(cache_date_str)
            age_days = (datetime.now(timezone.utc) - cache_date).days

            if age_days >= self.cache_max_age_days:
                logger.info(f"fresh cache expired ({age_days} days >= {self.cache_max_age_days} days)")
                return False

            logger.debug(f"fresh cache valid ({age_days} days < {self.cache_max_age_days} days)")
            return True

        except Exception as e:
            logger.error(f"Error checking fresh cache: {e}")
            return False

    def _load_cache_info(self, info_file: Path) -> Dict:
        """Load cache info JSON file"""
        try:
            return json.loads(info_file.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error(f"Failed to load cache info {info_file}: {e}")
            return {}

    def _save_cache_info(
        self,
        target_dir: Path,
        total_files: int,
        scraper_version: str = "1.0",
        source_url: str = "https://handbook.glyphsapp.com",
    ) -> None:
        """
        Save cache info

        Args:
            target_dir: Target cache directory
            total_files: Total file count
            scraper_version: Scraper version
            source_url: Source URL
        """
        info_file = target_dir / ".cache-info.json"
        cache_info = {
            "cache_date": datetime.now(timezone.utc).isoformat(),
            "scraper_version": scraper_version,
            "source_url": source_url,
            "total_files": total_files,
            "cache_max_age_days": self.cache_max_age_days,
        }

        info_file.write_text(
            json.dumps(cache_info, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        logger.info(f"Saved cache info: {info_file}")

    async def update_fresh_cache(self, force: bool = False) -> bool:
        """
        Update fresh cache

        Args:
            force: Whether to force update (ignore cache validity check)

        Returns:
            True if update successful, otherwise False
        """
        # Check if update is needed
        if not force and self.is_fresh_cache_valid():
            logger.info("fresh cache still valid, skipping update")
            return True

        logger.info("Starting fresh cache update...")

        try:
            async with HandbookScraper() as scraper:
                # Scrape all chapters
                chapters = await scraper.scrape_single_page()

                # Save to fresh cache directory
                self.fresh_cache_dir.mkdir(parents=True, exist_ok=True)
                scraper.save_to_directory(chapters, self.fresh_cache_dir)

                # Save cache info
                self._save_cache_info(self.fresh_cache_dir, len(chapters))

                logger.info(
                    f"✅ fresh cache update successful ({len(chapters)} files)"
                )
                return True

        except Exception as e:
            logger.error(f"❌ Failed to update fresh cache: {e}")
            return False

    async def generate_stable_cache(
        self,
        source_url: str = "https://handbook.glyphsapp.com",
    ) -> bool:
        """
        Generate stable cache (only used during initial setup or manual trigger)

        Args:
            source_url: Handbook source URL

        Returns:
            True if generation successful, otherwise False
        """
        logger.info("Starting stable cache generation...")

        try:
            async with HandbookScraper(base_url=source_url) as scraper:
                # Scrape all chapters
                chapters = await scraper.scrape_single_page()

                # Save to stable cache directory
                self.stable_cache_dir.mkdir(parents=True, exist_ok=True)
                scraper.save_to_directory(chapters, self.stable_cache_dir)

                # Save cache info
                self._save_cache_info(
                    self.stable_cache_dir,
                    len(chapters),
                    source_url=source_url,
                )

                logger.info(
                    f"✅ stable cache generation successful ({len(chapters)} files)"
                )
                return True

        except Exception as e:
            logger.error(f"❌ Failed to generate stable cache: {e}")
            return False

    def get_cache_status(self) -> Dict[str, Any]:
        """
        Get cache status info

        Returns:
            Dictionary containing cache status
        """
        stable_cache_info: Dict[str, Any] = {
            "exists": self.stable_cache_dir.exists(),
            "file_count": len(list(self.stable_cache_dir.glob("*.md")))
            if self.stable_cache_dir.exists()
            else 0,
        }
        fresh_cache_info: Dict[str, Any] = {
            "exists": self.fresh_cache_dir.exists(),
            "valid": self.is_fresh_cache_valid(),
            "file_count": len(list(self.fresh_cache_dir.glob("*.md")))
            if self.fresh_cache_dir.exists()
            else 0,
        }

        # Load cache info
        if self.stable_info_file.exists():
            stable_cache_info["info"] = self._load_cache_info(
                self.stable_info_file
            )

        if self.fresh_info_file.exists():
            fresh_cache_info["info"] = self._load_cache_info(
                self.fresh_info_file
            )

        status: Dict[str, Any] = {
            "active_cache": "fresh" if self.is_fresh_cache_valid() else "stable",
            "stable_cache": stable_cache_info,
            "fresh_cache": fresh_cache_info,
        }

        return status

    def clear_fresh_cache(self) -> None:
        """Clear fresh cache"""
        if self.fresh_cache_dir.exists():
            import shutil

            shutil.rmtree(self.fresh_cache_dir)
            logger.info(f"Cleared fresh cache: {self.fresh_cache_dir}")
        else:
            logger.info("fresh cache does not exist, no need to clear")
