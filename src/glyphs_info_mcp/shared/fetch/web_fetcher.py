#!/usr/bin/env python3
"""
Shared HTTP content fetcher with HTML to Markdown conversion
Used by all modules to avoid code duplication
"""

import logging

logger = logging.getLogger(__name__)

DEFAULT_USER_AGENT = "ModelContextProtocol/1.0 (Glyphs-WebSearch; +https://github.com/yintzuyuan/glyphs-info-mcp)"


class WebFetcher:
    """HTTP content fetcher with HTML to Markdown conversion"""

    def __init__(self, user_agent: str = DEFAULT_USER_AGENT):
        self.user_agent = user_agent

    def extract_content_from_html(self, html: str) -> str:
        """Convert HTML content to Markdown format

        Args:
            html: Raw HTML content

        Returns:
            Simplified Markdown version of the content
        """
        try:
            import markdownify
            import readabilipy.simple_json

            ret = readabilipy.simple_json.simple_json_from_html_string(
                html, use_readability=True
            )
            if not ret["content"]:
                return "<error>Page could not be simplified from HTML</error>"

            content = markdownify.markdownify(
                ret["content"],
                heading_style=markdownify.ATX,
            )
            return content
        except ImportError as e:
            logger.error(f"Missing required package: {e}")
            return f"<error>Missing required package: {e}</error>"
        except Exception as e:
            logger.error(f"HTML conversion failed: {e}")
            return f"<error>HTML conversion failed: {e}</error>"

    async def fetch_url(self, url: str, force_raw: bool = False) -> tuple[str, str]:
        """Fetch URL and return content in LLM-friendly format

        Args:
            url: URL to fetch
            force_raw: Whether to force returning raw content

        Returns:
            (content, prefix) tuple containing content and status info prefix
        """
        try:
            import httpx
        except ImportError:
            return "<error>httpx package required</error>", ""

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    follow_redirects=True,
                    headers={"User-Agent": self.user_agent},
                    timeout=30,
                )
            except httpx.HTTPError as e:
                error_msg = f"Fetch failed {url}: {e!r}"
                logger.error(error_msg)
                return f"<error>{error_msg}</error>", ""

            if response.status_code >= 400:
                error_msg = f"Fetch failed {url} - status code {response.status_code}"
                logger.error(error_msg)
                return f"<error>{error_msg}</error>", ""

            page_raw = response.text

        content_type = response.headers.get("content-type", "")
        is_page_html = (
            "<html" in page_raw[:100] or "text/html" in content_type or not content_type
        )

        if is_page_html and not force_raw:
            return self.extract_content_from_html(page_raw), ""

        return (
            page_raw,
            f"Content type {content_type} cannot be simplified to Markdown, raw content below:\n",
        )
