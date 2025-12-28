"""
HandbookScraper - Glyphs Handbook automated scraping tool

Automatically scrapes from https://handbook.glyphsapp.com/ and converts to Markdown format.
"""

import asyncio
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup, Tag
from markdownify import markdownify as md

logger = logging.getLogger(__name__)


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
        Download a single page HTML

        Args:
            url: Target URL
            retries: Retry count

        Returns:
            HTML string

        Raises:
            httpx.HTTPError: HTTP request failed
        """
        if not self.client:
            raise RuntimeError("Must be used within async context manager")

        for attempt in range(retries):
            try:
                logger.info(f"Downloading page: {url} (attempt {attempt + 1}/{retries})")
                response = await self.client.get(url)
                response.raise_for_status()
                return response.text
            except httpx.HTTPError as e:
                logger.warning(f"Download failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

        raise RuntimeError("Should not reach here")

    def _extract_main_content(self, soup: BeautifulSoup) -> Optional[Tag]:
        """
        Extract main content block from HTML

        Args:
            soup: BeautifulSoup object

        Returns:
            Tag object of main content, or None if not found
        """
        # Try multiple selectors
        selectors = [
            "main",
            "article",
            ".content",
            "#content",
            ".main-content",
        ]

        for selector in selectors:
            content = soup.select_one(selector)
            if content:
                logger.debug(f"Found main content using selector: {selector}")
                return content

        # Fallback: use body
        body = soup.find("body")
        if body and isinstance(body, Tag):
            logger.warning("Cannot find main content block, using entire body")
            return body

        logger.error("Cannot find any content")
        return None

    def _clean_html(self, content: Tag) -> Tag:
        """
        Clean HTML content (remove navigation, ads, etc.)

        Args:
            content: Original content Tag

        Returns:
            Cleaned Tag
        """
        # Remove unwanted elements
        unwanted_selectors = [
            "nav",
            "header",
            "footer",
            ".navigation",
            ".sidebar",
            ".advertisement",
            "script",
            "style",
            "noscript",
        ]

        for selector in unwanted_selectors:
            for element in content.select(selector):
                element.decompose()

        return content

    def _convert_html_to_markdown(self, html_content: Tag, page_url: str) -> str:
        """
        Convert HTML to Markdown

        Args:
            html_content: HTML content Tag
            page_url: Page URL (for converting relative links)

        Returns:
            Markdown string
        """
        # Convert relative links to absolute links
        for link in html_content.find_all("a", href=True):
            href = link["href"]
            if not href.startswith(("http://", "https://", "#")):
                link["href"] = urljoin(page_url, href)

        # Convert image links
        for img in html_content.find_all("img", src=True):
            src = img["src"]
            if not src.startswith(("http://", "https://")):
                img["src"] = urljoin(page_url, src)

        # Convert to Markdown
        markdown_text = md(
            str(html_content),
            heading_style="ATX",  # Use # heading format
            bullets="-",  # Use - as list marker
            code_language="python",  # Default code language
        )

        # Clean up excess blank lines
        markdown_text = re.sub(r"\n{3,}", "\n\n", markdown_text)

        return markdown_text.strip()

    async def scrape_single_page(self) -> Dict[str, str]:
        """
        Scrape single-page version of Handbook

        Returns:
            Dictionary {filename: Markdown content}
        """
        single_page_url = f"{self.base_url}/single-page/"
        logger.info(f"Starting single-page scrape: {single_page_url}")

        html = await self.fetch_page(single_page_url)
        soup = BeautifulSoup(html, "lxml")

        main_content = self._extract_main_content(soup)
        if not main_content:
            raise ValueError("Cannot extract main content from single-page version")

        # Clean HTML
        cleaned_content = self._clean_html(main_content)

        # Split into chapters by <h2> headers
        chapters = self._split_into_chapters(cleaned_content, single_page_url)

        logger.info(f"Successfully parsed {len(chapters)} chapters")
        return chapters

    def _split_into_chapters(
        self, content: Tag, page_url: str
    ) -> Dict[str, str]:
        """
        Split content into independent chapters by <h2> headers

        Args:
            content: Main content Tag
            page_url: Page URL

        Returns:
            Dictionary {filename: Markdown content}
        """
        chapters: Dict[str, str] = {}
        current_chapter: List[Tag] = []
        current_title = None
        current_url = None

        # Find all h2 headers
        for element in content.children:
            if not isinstance(element, Tag):
                continue

            # Encountered new h2 header
            if element.name == "h2":
                # Save previous chapter
                if current_chapter and current_title:
                    chapter_content = self._build_chapter_content(
                        current_title, current_chapter, current_url or page_url
                    )
                    filename = self._extract_filename_from_title(current_title)
                    chapters[filename] = chapter_content

                # Start new chapter
                current_title = element.get_text(strip=True)
                current_url = self._extract_url_from_heading(element)
                current_chapter = [element]

            elif current_title:
                # Accumulate current chapter content
                current_chapter.append(element)

        # Save last chapter
        if current_chapter and current_title:
            chapter_content = self._build_chapter_content(
                current_title, current_chapter, current_url or page_url
            )
            filename = self._extract_filename_from_title(current_title)
            chapters[filename] = chapter_content

        return chapters

    def _extract_url_from_heading(self, heading: Tag) -> Optional[str]:
        """Extract URL from heading element"""
        link = heading.find("a", href=True)
        if link and isinstance(link, Tag):
            href = link.get("href")
            if isinstance(href, str):
                return urljoin(self.base_url, href)
        return None

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

        return f"handbook_glyphsapp_com_{filename}.md"

    def _build_chapter_content(
        self, title: str, elements: List[Tag], chapter_url: str
    ) -> str:
        """
        Build chapter Markdown content

        Args:
            title: Chapter title
            elements: Chapter content elements
            chapter_url: Chapter URL

        Returns:
            Markdown string
        """
        # Create temporary container
        temp_container = BeautifulSoup("<div></div>", "lxml").div
        if temp_container is None:
            raise ValueError("Cannot create temporary container")

        for elem in elements:
            temp_container.append(elem.__copy__())

        # Convert to Markdown
        markdown_content = self._convert_html_to_markdown(
            temp_container, chapter_url
        )

        return markdown_content

    async def scrape_all_pages(self) -> Dict[str, str]:
        """
        Scrape all Handbook pages (multi-page version)

        This method starts from the homepage and recursively scrapes all linked pages.

        Returns:
            Dictionary {filename: Markdown content}

        Note:
            Currently prefer using scrape_single_page() method,
            this method is kept as a fallback.
        """
        # TODO: Implement multi-page scraping logic (use when single-page version fails)
        logger.warning("Multi-page scraping not implemented, recommend using scrape_single_page()")
        return await self.scrape_single_page()

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
        chapters = await scraper.scrape_single_page()
        scraper.save_to_directory(chapters, output_dir)
        return chapters
