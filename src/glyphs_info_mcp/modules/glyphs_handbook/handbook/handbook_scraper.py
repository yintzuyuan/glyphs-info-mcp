"""
HandbookScraper - Glyphs Handbook automated scraping tool

Scrapes from https://handbook.glyphsapp.com/single-page/document.md
and splits into individual chapter files.

Issue #17: Added TOC structure parsing from single-page version.
"""

import asyncio
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

import httpx
from bs4 import BeautifulSoup, Tag

from glyphs_info_mcp.modules.glyphs_handbook.handbook.toc_parser import (
    TocEntry,
    build_title_file_mapping,
    build_toc_tree,
    parse_headings,
)

logger = logging.getLogger(__name__)


def extract_nav_links_from_html(html: str) -> List[str]:
    """
    Extract navigation links from HTML content

    Args:
        html: HTML content string

    Returns:
        List of unique URL paths (e.g., ["/create/", "/palette/fit-curve/"])
    """
    if not html.strip():
        return []

    soup = BeautifulSoup(html, "html.parser")
    links: List[str] = []
    seen: set[str] = set()

    for anchor in soup.find_all("a", href=True):
        if not isinstance(anchor, Tag):
            continue
        href_attr = anchor.get("href")
        if not isinstance(href_attr, str):
            continue
        href: str = href_attr

        # Skip external links
        if href.startswith("http://") or href.startswith("https://"):
            continue

        # Skip anchor-only links
        if href.startswith("#"):
            continue

        # Strip anchor from URL
        if "#" in href:
            href = href.split("#")[0]

        # Skip empty hrefs
        if not href:
            continue

        # Skip PDF links (no document.md available)
        if ".pdf" in href.lower():
            continue

        # Ensure leading slash
        if not href.startswith("/"):
            href = "/" + href

        # Add trailing slash if missing
        if not href.endswith("/"):
            href = href + "/"

        # Skip single-page (contains all content, causes duplicates)
        if href == "/single-page/":
            continue

        # Deduplicate
        if href not in seen:
            seen.add(href)
            links.append(href)

    return links


class HandbookScraper:
    """Glyphs Handbook automated scraper"""

    def __init__(
        self,
        base_url: str = "https://handbook.glyphsapp.com",
        timeout: float = 30.0,
    ):
        """
        Initialize scraper

        Args:
            base_url: Handbook website base URL
            timeout: HTTP request timeout (seconds)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "HandbookScraper":
        """Async context manager entry"""
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            headers={
                "User-Agent": "GlyphsInfoMCP/1.0 (Handbook Cache Generator)"
            },
        )
        return self

    async def __aexit__(self, *args: object) -> None:
        """Async context manager exit"""
        if self.client:
            await self.client.aclose()

    async def fetch_page(self, url: str, retries: int = 3) -> str:
        """
        Download content from URL

        Args:
            url: Target URL
            retries: Retry count

        Returns:
            Content string

        Raises:
            httpx.HTTPError: HTTP request failed
        """
        if not self.client:
            raise RuntimeError("Must be used within async context manager")

        for attempt in range(retries):
            try:
                logger.info(f"Downloading: {url} (attempt {attempt + 1}/{retries})")
                response = await self.client.get(url)
                response.raise_for_status()
                return response.text
            except httpx.HTTPError as e:
                logger.warning(f"Download failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

        raise RuntimeError("Should not reach here")

    def _extract_filename_from_title(self, title: str) -> str:
        """
        Generate filename from chapter title

        Args:
            title: Chapter title

        Returns:
            Filename (with .md extension)
        """
        # Normalize title to filename
        filename = title.lower()
        filename = re.sub(r"[^\w\s-]", "", filename)  # Remove special characters
        filename = re.sub(r"[\s_-]+", "_", filename)  # Replace spaces with underscores
        filename = re.sub(r"^_|_$", "", filename)  # Remove leading/trailing underscores

        return f"{filename}.md"

    def _url_to_filename(self, url: str) -> str:
        """
        Convert URL path to filename

        Args:
            url: URL path (e.g., "/palette/fit-curve/")

        Returns:
            Filename (with .md extension)

        Note (Issue #17):
            Only `/` (path separator) is converted to `_`
            `-` (word connector) is PRESERVED

            This allows distinguishing hierarchy levels:
            - `/palette/fit-curve/` → `palette_fit-curve.md` (1 level deep)
            - `/palette/fit/curve/` → `palette_fit_curve.md` (2 levels deep)
        """
        # Remove leading/trailing slashes
        slug = url.strip("/")
        # Only replace slashes with underscores, preserve hyphens
        slug = slug.replace("/", "_")

        return f"{slug}.md"

    async def discover_page_urls(self) -> List[str]:
        """
        Discover all page URLs from the handbook homepage

        Returns:
            List of URL paths (e.g., ["/create/", "/palette/fit-curve/"])
        """
        homepage_url = f"{self.base_url}/"
        logger.info(f"Discovering page URLs from: {homepage_url}")

        html_content = await self.fetch_page(homepage_url)
        urls = extract_nav_links_from_html(html_content)

        logger.info(f"Discovered {len(urls)} page URLs")
        return urls

    async def scrape_all_pages(
        self, max_concurrent: int = 10
    ) -> Dict[str, str]:
        """
        Scrape all Handbook pages by discovering URLs and fetching each page's document.md

        Args:
            max_concurrent: Maximum number of concurrent downloads

        Returns:
            Dictionary {filename: Markdown content}
        """
        # Discover all page URLs
        urls = await self.discover_page_urls()

        if not urls:
            logger.warning("No page URLs discovered")
            return {}

        logger.info(f"Starting to scrape {len(urls)} pages (max concurrent: {max_concurrent})")

        # Create semaphore for concurrent limiting
        semaphore = asyncio.Semaphore(max_concurrent)

        async def fetch_page_with_limit(url: str) -> tuple[str, str | None]:
            """Fetch a single page with concurrency limit"""
            async with semaphore:
                md_url = f"{self.base_url}{url}document.md"
                filename = self._url_to_filename(url)
                try:
                    content = await self.fetch_page(md_url)
                    return (filename, content)
                except httpx.HTTPError as e:
                    logger.warning(f"Failed to fetch {md_url}: {e}")
                    return (filename, None)

        # Fetch all pages concurrently
        tasks = [fetch_page_with_limit(url) for url in urls]
        results = await asyncio.gather(*tasks)

        # Build result dictionary, excluding failed downloads
        chapters: Dict[str, str] = {}
        failed_count = 0
        for filename, content in results:
            if content is not None:
                chapters[filename] = content
            else:
                failed_count += 1

        logger.info(
            f"Successfully scraped {len(chapters)} pages "
            f"({failed_count} failed)"
        )
        return chapters

    def save_to_directory(
        self, chapters: Dict[str, str], output_dir: Path
    ) -> None:
        """
        Save chapters to specified directory

        Args:
            chapters: Chapter dictionary {filename: Markdown content}
            output_dir: Output directory
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        for filename, content in chapters.items():
            file_path = output_dir / filename
            file_path.write_text(content, encoding="utf-8")
            logger.info(f"Saved file: {file_path}")

        logger.info(f"Saved {len(chapters)} files to {output_dir}")

    async def fetch_single_page_content(self) -> str:
        """
        Fetch single-page version content for TOC parsing

        Returns:
            Markdown content of single-page version

        Note:
            This content is only used for TOC parsing and discarded after.
            The single-page version contains complete content but is too large
            for AI context, so we only extract the heading structure from it.
        """
        single_page_url = f"{self.base_url}/single-page/document.md"
        logger.info(f"Fetching single-page version for TOC: {single_page_url}")
        return await self.fetch_page(single_page_url)

    async def build_toc(self, cache_dir: Path) -> List[TocEntry]:
        """
        Build TOC structure from single-page version and cache files

        Args:
            cache_dir: Path to cache directory containing scraped .md files

        Returns:
            List of top-level TocEntry objects with hierarchical structure

        Note:
            1. Fetches single-page version to get heading order and levels
            2. Maps headings to cache files using first-line matching
            3. Single-page content is discarded after parsing (not stored)
        """
        # Step 1: Fetch and parse single-page headings
        single_page_content = await self.fetch_single_page_content()
        headings = parse_headings(single_page_content)
        logger.info(f"Parsed {len(headings)} headings from single-page version")

        # Step 2: Build title-to-file mapping from cache
        mapping = build_title_file_mapping(cache_dir)
        logger.info(f"Built mapping for {len(mapping)} cached files")

        # Step 3: Build hierarchical tree
        toc = build_toc_tree(headings, mapping)
        logger.info(f"Built TOC with {len(toc)} top-level entries")

        return toc


# Convenience function
async def scrape_handbook(
    output_dir: Path,
    base_url: str = "https://handbook.glyphsapp.com",
) -> Dict[str, str]:
    """
    Scrape Handbook and save to specified directory

    Args:
        output_dir: Output directory
        base_url: Handbook website URL

    Returns:
        Chapter dictionary {filename: Markdown content}
    """
    async with HandbookScraper(base_url=base_url) as scraper:
        chapters = await scraper.scrape_all_pages()
        scraper.save_to_directory(chapters, output_dir)
        return chapters
