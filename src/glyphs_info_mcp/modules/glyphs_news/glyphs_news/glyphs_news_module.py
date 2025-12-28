#!/usr/bin/env python3
"""
Glyphs News module for official news, forum discussions, and tutorial search
"""

import logging
import re
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

# Use shared core library
# From modules/glyphs-news/src/modules/glyphs_news/glyphs_news_module.py to project root requires 6 levels
project_root = Path(__file__).parent.parent.parent.parent
shared_core_path = str(project_root / "src" / "shared")
if shared_core_path not in sys.path:
    sys.path.insert(0, shared_core_path)

from glyphs_info_mcp.shared.core.base_module import BaseMCPModule  # noqa: E402
from glyphs_info_mcp.shared.fetch.web_fetcher import WebFetcher  # noqa: E402

logger = logging.getLogger(__name__)


class GlyphsNewsModule(BaseMCPModule):
    """Glyphs News module for official news, forum discussions, and tutorials"""

    def __init__(self, name: str = "glyphs-news", data_path: Path | None = None):
        if data_path is None:
            # Get the module root directory (4 levels up from this file)
            module_root = Path(__file__).parent.parent
            data_path = module_root / "data"

        super().__init__(name, data_path)
        self.web_fetcher = WebFetcher()
        self.search_engine = None  # Will be injected by server.py unified search engine

    def set_search_engine(self, search_engine: Any) -> None:
        """Set unified search engine (called by server.py)"""
        self.search_engine = search_engine

    def initialize(self) -> bool:
        """Initialize the web search module"""
        try:
            # Create data directory if it doesn't exist
            self.data_path.mkdir(parents=True, exist_ok=True)

            self.is_initialized = True
            logger.info("Glyphs News module initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Glyphs News module: {e}")
            return False

    def core_search(self, query: str, max_results: int = 5, **kwargs: Any) -> list[dict[str, Any]]:
        """Core search function - for unified search engine use only

        Returns structured search results without vocabulary processing or formatting

        Args:
            query: Search query (already preprocessed)
            max_results: Maximum number of results

        Returns:
            List of structured search results
        """
        if not self.is_initialized:
            return []

        results = []

        try:
            # Search forum discussions
            forum_results = self._search_forum_core(query, max_results // 2)
            results.extend(forum_results)

            # Search official news
            news_results = self._search_news_core(query, max_results // 2)
            results.extend(news_results)

        except Exception as e:
            logger.error(f"News core search failed: {e}")

        return results[:max_results]

    def _search_forum_core(self, query: str, max_results: int) -> list[dict[str, Any]]:
        """Forum search core function"""
        results = []

        try:
            # Should implement real forum search logic here
            # Currently using simplified version
            results.append({
                'title': f"Forum discussion: {query}",
                'content': f"Community discussion about {query}...",
                'source': 'news',
                'type': 'forum',
                'url': f"https://forum.glyphsapp.com/search?q={query}",
                'score': 0.6
            })
        except Exception as e:
            logger.debug(f"Forum search failed: {e}")

        return results[:max_results]

    def _search_news_core(self, query: str, max_results: int) -> list[dict[str, Any]]:
        """News search core function"""
        results = []

        try:
            # Should implement real news search logic here
            # Currently using simplified version
            results.append({
                'title': f"Official news: {query}",
                'content': f"Latest updates about {query}...",
                'source': 'news',
                'type': 'news',
                'url': "https://glyphsapp.com/news",
                'score': 0.7
            })
        except Exception as e:
            logger.debug(f"News search failed: {e}")

        return results[:max_results]

    async def _parse_search_results(
        self, search_content: str, query: str
    ) -> list[tuple[str, str, str]]:
        """Parse search result page and extract tutorial article links

        Args:
            search_content: HTML/Markdown content of search result page
            query: Original search query

        Returns:
            List of [(title, url, description), ...]
        """
        tutorials = []

        # First try to parse links from raw HTML
        # Search results may be in raw HTML format
        if "<html" in search_content and "href=" in search_content:
            tutorials = self._parse_html_search_results(search_content)

        # If no results found, try Markdown format
        if not tutorials:
            base_url = "https://glyphsapp.com"
            # Look for patterns like [Tutorial Title](relative-url)
            link_pattern = r"\[([^\]]+)\]\((/learn/[^)]+)\)"
            matches = re.findall(link_pattern, search_content)

            for title, relative_url in matches:
                full_url = urljoin(base_url, relative_url)
                tutorials.append((title.strip(), full_url, ""))

        # If no search results, return empty list (removed hardcoded fallback)

        # Return all search results (using original page order, removed custom scoring)
        # Can adjust filter count, currently keeping 30 results limit
        return tutorials[:30]  # Keep more results for further processing

    def _parse_html_search_results(
        self, html_content: str
    ) -> list[tuple[str, str, str]]:
        """Parse tutorial article links from HTML content

        Args:
            html_content: Raw HTML content

        Returns:
            List of [(title, url, description), ...]
        """
        tutorials = []

        # Parse tutorial links from HTML
        # Look for href="https://glyphsapp.com/learn/..." and corresponding titles
        link_pattern = r'href="(https://glyphsapp\.com/learn/[^"]+)"[^>]*>([^<]+)</a>'
        matches = re.findall(link_pattern, html_content)

        for url, title in matches:
            # Clean title text
            clean_title = re.sub(r"<[^>]+>", "", title).strip()
            if clean_title and url:
                tutorials.append((clean_title, url, ""))

        # Also try to parse from bookmark button data attributes
        bookmark_pattern = (
            r'data-bookmark-button=\'{"id":"[^"]+","title":"([^"]+)","url":"([^"]+)"}\''
        )
        bookmark_matches = re.findall(bookmark_pattern, html_content)

        for title, url in bookmark_matches:
            if (title, url, "") not in tutorials:
                tutorials.append((title, url, ""))

        return tutorials

    async def _parse_forum_search_results(
        self, search_content: str, query: str
    ) -> list[tuple[str, str, str, int, str, str]]:
        """Parse forum search result JSON data and extract discussion info

        Args:
            search_content: JSON content returned by forum search API
            query: Original search query

        Returns:
            List of [(title, topic_url, author, replies_count, created_at, last_posted_at), ...]
        """
        import json
        from datetime import datetime

        # query parameter kept for API consistency, not used in current implementation
        _ = query
        discussions = []

        try:
            # Parse JSON data
            data = json.loads(search_content)

            # Build topics dict for quick lookup
            topics_dict = {}
            if "topics" in data:
                for topic in data["topics"]:
                    topics_dict[topic["id"]] = topic

            # Extract info from posts and associate with corresponding topic
            if "posts" in data:
                processed_topics = set()  # Avoid processing same topic twice

                for post in data["posts"][:30]:  # Limit processing count
                    topic_id = post.get("topic_id")

                    # Avoid processing same discussion topic twice
                    if topic_id in processed_topics or topic_id not in topics_dict:
                        continue

                    processed_topics.add(topic_id)
                    topic = topics_dict[topic_id]

                    # Extract discussion info
                    title = topic.get("title", "Untitled")
                    slug = topic.get("slug", "")
                    replies_count = topic.get("posts_count", 1) - 1  # Subtract original post
                    created_at = topic.get("created_at", "")
                    last_posted_at = topic.get("last_posted_at", created_at)
                    author = post.get("name", "Unknown")

                    # Build forum discussion URL
                    if slug and topic_id:
                        topic_url = f"https://forum.glyphsapp.com/t/{slug}/{topic_id}"
                    else:
                        topic_url = f"https://forum.glyphsapp.com/t/{topic_id}"

                    # Format timestamps
                    try:
                        created_time = datetime.fromisoformat(
                            created_at.replace("Z", "+00:00")
                        ).strftime("%Y-%m-%d")
                        if last_posted_at != created_at:
                            last_time = datetime.fromisoformat(
                                last_posted_at.replace("Z", "+00:00")
                            ).strftime("%Y-%m-%d")
                        else:
                            last_time = created_time
                    except (ValueError, TypeError):
                        created_time = (
                            created_at[:10] if len(created_at) >= 10 else created_at
                        )
                        last_time = (
                            last_posted_at[:10]
                            if len(last_posted_at) >= 10
                            else last_posted_at
                        )

                    discussions.append(
                        (
                            title,
                            topic_url,
                            author,
                            replies_count,
                            created_time,
                            last_time,
                        )
                    )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse forum search JSON: {e}")
        except Exception as e:
            logger.error(f"Error processing forum search results: {e}")

        # Sort by latest reply time (JSON API should already be sorted by order:latest)
        return discussions

    def _consolidate_search_results(
        self, tutorials: list[tuple[str, str, str]], query: str
    ) -> str:
        """Consolidate search result list for AI to evaluate from titles

        Args:
            tutorials: List of [(title, url, description), ...]
            query: Original search query

        Returns:
            Formatted search result list
        """
        if not tutorials:
            return "No related tutorial content found."

        consolidated = []
        consolidated.append(f"## 🔍 Glyphs Tutorial Search Results: \"{query}\"\n")
        consolidated.append(f"**Found {len(tutorials)} related results** (in original page order)\n")

        for i, (title, url, description) in enumerate(tutorials, 1):
            consolidated.append(f"### {i}. {title}")
            consolidated.append(f"**Link**: {url}")
            if description.strip():
                consolidated.append(f"**Description**: {description}")
            consolidated.append("")

        consolidated.append("\n---\n")
        consolidated.append(
            "**Note**: These are all search results. AI should determine the most relevant resources based on titles and URLs."
        )
        consolidated.append(
            "To view specific content, use `news_fetch_tutorial` or `WebFetch` tool to get individual page content."
        )

        return "\n".join(consolidated)

    def _consolidate_forum_search_results(
        self, discussions: list[tuple[str, str, str, int, str, str]], query: str
    ) -> str:
        """Consolidate forum discussion results, showing community discussion overview

        Args:
            discussions: List of [(title, topic_url, author, replies_count, created_at, last_posted_at), ...]
            query: Original search query

        Returns:
            Formatted forum discussion overview
        """
        if not discussions:
            return "No related forum discussions found."

        consolidated = []
        consolidated.append(f"## 💬 Glyphs Forum Discussion Search Results: \"{query}\"\n")
        consolidated.append(
            f"**Found {len(discussions)} related discussions** (sorted by latest reply)\n"
        )

        for i, (
            title,
            topic_url,
            author,
            replies_count,
            created_at,
            last_posted_at,
        ) in enumerate(discussions, 1):
            consolidated.append(f"### {i}. {title}")
            consolidated.append(f"**Link**: {topic_url}")
            consolidated.append(f"**Author**: {author}")
            consolidated.append(f"**Replies**: {replies_count} replies")
            consolidated.append(f"**Posted**: {created_at}")

            if last_posted_at != created_at:
                consolidated.append(f"**Latest reply**: {last_posted_at}")

            # Show discussion activity based on reply count
            if replies_count >= 10:
                consolidated.append("🔥 **Hot discussion**")
            elif replies_count >= 5:
                consolidated.append("📈 **Active discussion**")
            elif replies_count == 0:
                consolidated.append("❓ **Awaiting reply**")

            consolidated.append("")

        consolidated.append("\n---\n")
        consolidated.append(
            "**Note**: This is a forum discussion overview, including community activity and timeline info."
        )
        consolidated.append(
            "To view specific discussion content, use `news_fetch_forum_post` tool to get detailed content of a specific discussion,"
        )
        consolidated.append("or use `WebFetch` tool to directly access discussion links.")

        return "\n".join(consolidated)

    def _consolidate_content(
        self, tutorial_contents: list[tuple[str, str, str]]
    ) -> str:
        """Consolidate multiple article contents

        Args:
            tutorial_contents: List of [(title, url, content), ...]

        Returns:
            Consolidated content string
        """
        if not tutorial_contents:
            return "No related tutorial content found."

        consolidated = []
        consolidated.append("## 🎯 Glyphs Tutorial Content Summary\n")

        for i, (title, url, content) in enumerate(tutorial_contents, 1):
            consolidated.append(f"### {i}. {title}")
            consolidated.append(f"**Source**: {url}")
            consolidated.append("")

            # Clean and truncate content
            if content:
                # Remove possible error tags
                clean_content = content.replace("<error>", "").replace("</error>", "")

                # If content is too long, keep first n characters
                if len(clean_content) > 300:
                    clean_content = (
                        clean_content[:300]
                        + "\n\n[Content truncated, click link above for full content]"
                    )

                consolidated.append(clean_content)
            else:
                consolidated.append("*[Unable to fetch content, please visit link directly]*")

            consolidated.append("\n" + "─" * 50 + "\n")

        return "\n".join(consolidated)

    def get_tools(self) -> dict[str, Callable]:
        """Get available tools as dictionary

        Wrap bound methods as standalone async functions to ensure FastMCP/MCP clients
        properly handle async calls. This fixes issues where coroutine objects weren't
        being properly awaited.
        """
        # Wrap async bound methods as standalone async functions
        async def search_forum_wrapper(query: str) -> str:
            return await self.web_search_forum(query)

        async def search_tutorials_wrapper(
            query: str, topic: str = "all", collection: str = "all"
        ) -> str:
            return await self.web_search_tutorials(query, topic, collection)

        async def fetch_tutorial_wrapper(url: str) -> str:
            return await self.web_get_tutorial_content(url)

        async def fetch_forum_post_wrapper(
            url: str, post_number: int | None = None, start_position: int = 0
        ) -> str:
            return await self.web_get_forum_post_content(url, post_number, start_position)

        async def search_posts_wrapper(query: str) -> str:
            return await self.web_search_news_posts(query)

        async def fetch_content_wrapper(url: str) -> str:
            return await self.web_fetch_news_content(url)

        return {
            "news_search_forum": search_forum_wrapper,
            "news_search_tutorials": search_tutorials_wrapper,
            "news_fetch_tutorial": fetch_tutorial_wrapper,
            "news_fetch_forum_post": fetch_forum_post_wrapper,
            "news_search_posts": search_posts_wrapper,
            "news_fetch_content": fetch_content_wrapper,
        }

    async def web_search_forum(self, query: str) -> str:
        """
        [WEB SEARCH] Search Glyphs official forum for latest information and discussions

        Features: Gets latest community discussions, Q&A, and official responses. Shows discussion popularity, participants, and timeline.
        Purpose: Check for similar issues, view official replies, and understand trending topics.

        Important note: Statements from developers Georg Seifert, Florian Pircher, and Rainer Erich Scheichelbauer (mekkablue) carry the same weight as official documentation and API. Pay special attention to responses from these development team members.

        Args:
            query: Search keyword

        Returns:
            Forum discussion overview including title, author, reply count, and timestamps
        """
        if not self.is_initialized:
            return "Glyphs News module not initialized"

        if not query.strip():
            return "Please provide search keywords"

        # Use query processor for preprocessing
        if self.search_engine and self.search_engine.query_processor:
            processed_query, user_language = self.search_engine.query_processor.preprocess_query(query)
        else:
            processed_query = query
            user_language = 'en'

        try:
            # Use forum JSON API for search, automatically add order:latest sorting
            search_url = f"https://forum.glyphsapp.com/search.json?q={processed_query.replace(' ', '+') + '+order:latest'}"
            logger.info(f"Searching forum discussions: {search_url}")

            # Get structured data using raw JSON format
            search_content, _ = await self.web_fetcher.fetch_url(
                search_url, force_raw=True
            )

            if "<error>" in search_content:
                return f"""Error occurred while searching forum discussions:
{search_content}

**Alternative**:
Forum domain: https://forum.glyphsapp.com/
Suggestion: Please manually visit the URL above to search for "{query}" related discussions"""

            # Parse forum search results
            forum_discussions = await self._parse_forum_search_results(
                search_content, query
            )

            if not forum_discussions:
                return f"""No forum discussions related to "{query}" found.

**Possible reasons**:
- Keywords may need adjustment (English keywords recommended)
- The topic may have few discussions

**Suggestions**:
- Try related English keywords
- Visit https://forum.glyphsapp.com/ to search manually
- Use news_search_tutorials tool to check for related tutorials"""

            # Consolidate forum discussion overview
            consolidated_content = self._consolidate_forum_search_results(
                forum_discussions, query
            )

            # Use query processor for postprocessing
            if self.search_engine and self.search_engine.query_processor:
                return self.search_engine.query_processor.postprocess_output(consolidated_content, user_language)
            else:
                return consolidated_content

        except Exception as e:
            logger.error(f"Error occurred during forum search: {e}")
            return f"""Error occurred during forum search: {e}

**Alternative**:
Forum domain: https://forum.glyphsapp.com/
Suggestion: Please use WebSearch tool to search for "{query}" related discussions on the domain above"""

    async def web_search_tutorials(
        self, query: str, topic: str = "all", collection: str = "all"
    ) -> str:
        """
        [WEB SEARCH] Search Glyphs official tutorial resources

        Features: Automatically searches the official tutorial website, listing all relevant results in original page order.
        Purpose: Let AI determine the most suitable articles from titles, then use existing tools to get content.

        Args:
            query: Search keyword
            topic: Topic filter (kept for compatibility, currently unused)
            collection: Collection filter (kept for compatibility, currently unused)

        Returns:
            Formatted list of all search results for AI to evaluate, then use WebFetch or news_fetch_tutorial to get content
        """
        if not self.is_initialized:
            return "Glyphs News module not initialized"

        if not query.strip():
            return "Please provide search keywords"

        # Parameters not used yet, kept for API compatibility
        _ = topic, collection

        # Use query processor for preprocessing
        if self.search_engine and self.search_engine.query_processor:
            processed_query, user_language = self.search_engine.query_processor.preprocess_query(query)
        else:
            processed_query = query
            user_language = 'en'

        try:
            # Step 1: Search tutorial pages
            search_url = f"https://glyphsapp.com/learn?q={processed_query.replace(' ', '+')}"
            logger.info(f"Searching tutorial content: {search_url}")

            # Use raw HTML format for parsing, don't convert to Markdown
            search_content, _ = await self.web_fetcher.fetch_url(
                search_url, force_raw=True
            )

            if "<error>" in search_content:
                return f"""Error occurred while searching tutorial content:
{search_content}

**Alternative**:
Tutorial resources: https://glyphsapp.com/learn/
Suggestion: Please manually visit the URL above to search for "{query}" related content"""

            # Step 2: Parse search results
            tutorials = await self._parse_search_results(search_content, query)

            if not tutorials:
                return f"""No tutorial content related to "{query}" found.

**Possible reasons**:
- Keywords may need adjustment (English keywords recommended)
- Content may be in other sections

**Suggestions**:
- Try related English keywords
- Visit https://glyphsapp.com/learn/ to search manually
- Use news_search_forum tool to search community discussions"""

            # Step 3: List all search results for AI to determine most suitable articles
            # AI will judge relevance from titles, then use existing tools to get content
            consolidated_content = self._consolidate_search_results(tutorials, query)

            # Use query processor for postprocessing
            if self.search_engine and self.search_engine.query_processor:
                return self.search_engine.query_processor.postprocess_output(consolidated_content, user_language)
            else:
                return consolidated_content

        except Exception as e:
            logger.error(f"Error occurred during tutorial search: {e}")
            return f"""Error occurred during tutorial search: {e}

**Alternative**:
Tutorial resources: https://glyphsapp.com/learn/
Suggestion: Please use WebSearch tool to search for "{query}" related content on the domain above"""

    async def web_get_tutorial_content(self, url: str) -> str:
        """
        Directly fetches tutorial content using built-in fetch functionality

        Args:
            url: URL to fetch content from

        Returns:
            Fetched tutorial content
        """
        if not self.is_initialized:
            return "Glyphs News module not initialized"

        if not url.strip():
            return "Please provide a URL to fetch"

        if not url.startswith(("http://", "https://")):
            return "Please provide a complete URL (including http:// or https://)"

        try:
            logger.info(f"Fetching tutorial content: {url}")
            content, prefix = await self.web_fetcher.fetch_url(url)

            if "<error>" in content:
                return f"""Error occurred while fetching tutorial content:
{content}

**Alternative**:
Please try visiting directly: {url}"""

            # Format content output
            result = f"## 📖 Tutorial Content\n**Source**: {url}\n\n"
            if prefix:
                result += f"{prefix}\n"
            result += content

            return result

        except Exception as e:
            logger.error(f"Failed to fetch tutorial content {url}: {e}")
            return f"""Error occurred while fetching tutorial content: {e}

**Alternative**:
Please try visiting directly: {url}"""

    async def web_get_forum_post_content(
        self, url: str, post_number: int | None = None, start_position: int = 0
    ) -> str:
        """
        Fetches forum discussion content, supports getting entire thread or specific reply with progressive fetching

        Args:
            url: Forum discussion URL
            post_number: Specific reply number (optional), if not specified returns discussion overview
            start_position: Start fetching from specified character position (supports continue reading)

        Returns:
            Forum discussion content or specific reply content, including position info and continue reading hints
        """
        if not self.is_initialized:
            return "Glyphs News module not initialized"

        if not url.strip():
            return "Please provide a forum discussion URL to fetch"

        if not url.startswith(("http://", "https://")):
            return "Please provide a complete URL (including http:// or https://)"

        if "forum.glyphsapp.com" not in url:
            return "Please provide a Glyphs official forum URL"

        try:
            # If specific reply number is specified, modify URL to navigate directly to that reply
            target_url = url
            if post_number is not None:
                if not target_url.endswith("/"):
                    target_url += "/"
                target_url += str(post_number)

            logger.info(f"Fetching forum discussion content: {target_url}")
            content, _ = await self.web_fetcher.fetch_url(target_url)

            if "<error>" in content:
                return f"""Error occurred while fetching forum discussion content:
{content}

**Alternative**:
Please try visiting directly: {target_url}"""

            # Special handling for forum content, supporting progressive fetching
            if post_number is not None:
                # Fetch complete content of specific reply
                result = f"## 📝 Forum Reply Content (Post #{post_number})\n**Source**: {target_url}\n\n"

                # Use progressive fetching to process specific reply
                processed_content, position_info = (
                    self._extract_specific_post_content_progressive(
                        content, post_number, start_position
                    )
                )
                result += processed_content
                if position_info:
                    result += f"\n\n{position_info}"
            else:
                # Fetch overview of entire discussion thread
                result = f"## 💬 Forum Discussion Content\n**Source**: {target_url}\n\n"

                # Use progressive fetching to process discussion thread overview
                processed_content, position_info = (
                    self._extract_discussion_overview_progressive(
                        content, start_position
                    )
                )
                result += processed_content
                if position_info:
                    result += f"\n\n{position_info}"

            return result

        except Exception as e:
            logger.error(f"Failed to fetch forum discussion content {url}: {e}")
            return f"""Error occurred while fetching forum discussion content: {e}

**Alternative**:
Please try visiting directly: {url}"""

    def _extract_specific_post_content(self, content: str, post_number: int) -> str:
        """Extract specific reply content from forum page content

        Args:
            content: Complete content of forum page
            post_number: Reply number to extract

        Returns:
            Extracted specific reply content, or empty string if unable to extract
        """
        # post_number parameter kept for API consistency, not used in current implementation
        _ = post_number

        # More precise reply content extraction logic can be implemented here
        # For now, return reasonable truncation of original content
        if len(content) > 2500:
            return content[:2500] + "\n\n[Content truncated, visit link directly for full content]"
        return content

    def _extract_discussion_overview(self, content: str) -> str:
        """Extract discussion overview from forum discussion page

        Args:
            content: Complete content of forum discussion page

        Returns:
            Formatted discussion overview
        """
        # Truncate content to reasonable length for overview
        if len(content) > 2500:
            overview = (
                content[:2500] + "\n\n[Discussion content truncated, visit original link for full discussion]"
            )
        else:
            overview = content

        return overview

    def _extract_specific_post_content_progressive(
        self, content: str, post_number: int, start_position: int = 0
    ) -> tuple[str, str]:
        """Progressive extraction of specific reply content, supporting continue reading

        Args:
            content: Complete content of forum page
            post_number: Reply number to extract
            start_position: Starting position for extraction

        Returns:
            (extracted_content, position_info) tuple
            - extracted_content: Extracted content
            - position_info: Position info and continue reading hint, empty string if content is complete
        """
        # post_number parameter kept for API consistency, not used in current implementation
        _ = post_number

        total_length = len(content)
        chunk_size = 2500  # Characters to extract per chunk

        # Ensure start_position is within valid range
        start_position = max(0, min(start_position, total_length))

        # Calculate end position
        end_position = min(start_position + chunk_size, total_length)

        # Extract content from specified range
        extracted_content = content[start_position:end_position]

        # Generate position info
        position_info = ""
        if total_length > chunk_size:  # Only show position info when content is long enough
            position_info = f"📍 **Content position**: Characters {start_position + 1} - {end_position} (total {total_length} characters)"

            if end_position < total_length:
                # More content available for continue reading
                remaining = total_length - end_position
                position_info += f"\n\n📖 **Continue reading**: {remaining} characters remaining."
                position_info += f"\nTo continue reading, use the same tool with `start_position={end_position}`"
            else:
                position_info += "\n\n✅ **Content fully displayed**"

        return extracted_content, position_info

    def _extract_discussion_overview_progressive(
        self, content: str, start_position: int = 0
    ) -> tuple[str, str]:
        """Progressive extraction of discussion overview, supporting continue reading

        Args:
            content: Complete content of forum discussion page
            start_position: Starting position for extraction

        Returns:
            (extracted_content, position_info) tuple
            - extracted_content: Extracted content
            - position_info: Position info and continue reading hint, empty string if content is complete
        """
        total_length = len(content)
        chunk_size = 2500  # Characters to extract per chunk

        # Ensure start_position is within valid range
        start_position = max(0, min(start_position, total_length))

        # Calculate end position
        end_position = min(start_position + chunk_size, total_length)

        # Extract content from specified range
        extracted_content = content[start_position:end_position]

        # Generate position info
        position_info = ""
        if total_length > chunk_size:  # Only show position info when content is long enough
            position_info = f"📍 **Content position**: Characters {start_position + 1} - {end_position} (total {total_length} characters)"

            if end_position < total_length:
                # More content available for continue reading
                remaining = total_length - end_position
                position_info += f"\n\n📖 **Continue reading**: {remaining} characters remaining."
                position_info += f"\nTo continue reading, use the same tool with `start_position={end_position}`"
            else:
                position_info += "\n\n✅ **Content fully displayed**"

        return extracted_content, position_info

    def _preprocess_news_query(self, original_query: str) -> tuple[str, str]:
        """Preprocess news query, using only 'released' as search keyword

        Args:
            original_query: Original query

        Returns:
            (search_query, original_query) tuple
            - search_query: Fixed to 'released'
            - original_query: Keep original query for subsequent title matching
        """
        # Use only 'released' for search to avoid keyword interference
        search_query = "released"
        logger.info(
            f"Simplified search strategy: original query '{original_query}' -> search keyword '{search_query}'"
        )
        return search_query, original_query.strip()

    async def _search_posts_only(self, search_query: str, original_query: str) -> str:
        """Execute search for post list only, without fetching detailed content

        Args:
            search_query: Fixed to 'released'
            original_query: Original query, used for title matching

        Returns:
            Formatted post list (without detailed content)
        """
        try:
            # Get raw HTML of news page
            news_page_content, _ = await self.web_fetcher.fetch_url(
                "https://glyphsapp.com/news", force_raw=True
            )

            if "<error>" in news_page_content:
                return self._provide_manual_search_options(
                    original_query, "Unable to fetch news page"
                )

            # Parse all news links containing 'released'
            all_released_links = await self._find_all_released_links(news_page_content)

            if not all_released_links:
                return self._provide_manual_search_options(
                    original_query, "No release-related links found"
                )

            # Sort by release time (newest first)
            def is_newer_article(link: dict[str, str]) -> int:
                """Determine if article is newer"""
                url = link["url"].lower()
                if "lttrink-1-4-released" in url:
                    return 2025050900
                elif "glyphs-3-3-released" in url:
                    return 2024120000
                elif "glyphs-3-2-released" in url:
                    return 2024100000
                else:
                    return 0

            sorted_links = sorted(
                all_released_links, key=is_newer_article, reverse=True
            )

            # Filter most relevant results based on original query
            relevant_links = self._filter_by_original_query(
                sorted_links, original_query
            )

            # Only return post list, without fetching detailed content
            return self._consolidate_posts_list(relevant_links[:15], original_query)

        except Exception as e:
            logger.error(f"Failed to search post list: {e}")
            return self._provide_manual_search_options(
                original_query, f"Error occurred during search: {e}"
            )

    async def _find_all_released_links(self, web_content: str) -> list[dict[str, str]]:
        """Find all news links containing 'released'

        Args:
            web_content: Webpage HTML content

        Returns:
            List of all release-related links
        """
        import asyncio
        import re

        released_links = []

        # Find all news URLs
        url_patterns = [r'https://glyphsapp\.com/news/[^"\s]+', r'/news/[^"\s]+']

        found_urls = set()
        for url_pattern in url_patterns:
            matches = re.findall(url_pattern, web_content)
            for match in matches:
                if match.startswith("https://glyphsapp.com/news/"):
                    found_urls.add(match)
                elif match.startswith("/news/"):
                    found_urls.add(f"https://glyphsapp.com{match}")

        # Strategy 1: URL contains 'released' (quick filter)
        strategy1_links = []
        strategy2_candidates = []

        for full_url in found_urls:
            if full_url.endswith("/feed"):  # Skip RSS feed
                continue

            # Skip media files (images, videos, etc.)
            if any(
                ext in full_url.lower()
                for ext in [".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".pdf"]
            ):
                continue

            relative_url = full_url.replace("https://glyphsapp.com", "")
            path_part = relative_url.split("/news/")[-1]

            if "released" in full_url.lower():
                if path_part:
                    title_words = path_part.replace("-", " ").replace("_", " ")
                    title = " ".join(word.capitalize() for word in title_words.split())

                    strategy1_links.append(
                        {"title": title, "url": full_url, "path": relative_url}
                    )
            # Improved strategy 2 candidate conditions: more precise pattern matching
            elif any(
                pattern in full_url.lower()
                for pattern in ["plugin", "tool", "script", "extension"]
            ):
                # Exclude obviously unrelated patterns
                if not any(
                    exclude in full_url.lower()
                    for exclude in ["tutorial", "guide", "tip", "interview", "showcase"]
                ):
                    strategy2_candidates.append((full_url, relative_url, path_part))

        # Add strategy 1 results first
        released_links.extend(strategy1_links)

        # Strategy 2: Parallel content check (limited concurrency)
        if strategy2_candidates:
            logger.info(
                f"Strategy 1 found {len(strategy1_links)} links, parallel checking {len(strategy2_candidates)} candidates"
            )

            # Limit concurrency to avoid overload
            semaphore = asyncio.Semaphore(5)  # Max 5 parallel requests

            async def check_article_content(
                url_data: tuple[str, str, str],
            ) -> dict[str, str] | None:
                full_url, relative_url, path_part = url_data
                async with semaphore:
                    try:
                        # Use lightweight check: force_raw=True, shorter timeout
                        article_content, _ = await self._fetch_url_with_timeout(
                            full_url, timeout=10
                        )

                        # Only check first 2000 chars to determine if contains 'released'
                        content_preview = article_content[:2000].lower()
                        if "released" in content_preview:
                            if path_part:
                                title_words = path_part.replace("-", " ").replace(
                                    "_", " "
                                )
                                title = " ".join(
                                    word.capitalize() for word in title_words.split()
                                )

                                return {
                                    "title": title,
                                    "url": full_url,
                                    "path": relative_url,
                                }
                    except Exception as e:
                        logger.debug(f"Error during parallel article content check {full_url}: {e}")
                    return None

            # Execute all content checks in parallel, with overall timeout
            try:
                results = await asyncio.wait_for(
                    asyncio.gather(
                        *[
                            check_article_content(candidate)
                            for candidate in strategy2_candidates
                        ],
                        return_exceptions=True,
                    ),
                    timeout=30,  # Overall timeout 30 seconds
                )

                # Collect valid results
                strategy2_links = [
                    result
                    for result in results
                    if isinstance(result, dict) and result is not None
                ]
                released_links.extend(strategy2_links)

                logger.info(f"Strategy 2 parallel check completed, added {len(strategy2_links)} links")

            except asyncio.TimeoutError:
                logger.warning("Strategy 2 parallel check timed out, using strategy 1 results")

        logger.info(f"Total found {len(released_links)} news links containing 'released'")
        return released_links

    async def _fetch_url_with_timeout(
        self, url: str, timeout: int = 10
    ) -> tuple[str, str]:
        """Lightweight URL content fetching, for quick content checking

        Args:
            url: URL to fetch
            timeout: Timeout in seconds

        Returns:
            (content, prefix) tuple
        """
        try:
            import asyncio

            import httpx

            async with httpx.AsyncClient() as client:
                response = await asyncio.wait_for(
                    client.get(
                        url,
                        follow_redirects=True,
                        headers={"User-Agent": self.web_fetcher.user_agent},
                        timeout=timeout,
                    ),
                    timeout=timeout,
                )

                if response.status_code >= 400:
                    return f"<error>Status code {response.status_code}</error>", ""

                # Return raw text directly, without HTML→Markdown conversion
                return response.text, ""

        except (httpx.HTTPError, asyncio.TimeoutError) as e:
            return f"<error>Fetch failed: {e!r}</error>", ""
        except Exception as e:
            return f"<error>Unexpected error: {e!r}</error>", ""

    def _sort_by_version_time(
        self, released_links: list[dict[str, str]]
    ) -> list[dict[str, str]]:
        """Sort by version number/time (newest first)

        Args:
            released_links: List of release links

        Returns:
            Sorted list of links
        """

        def extract_version_key(link: dict[str, str]) -> tuple[int, int, int]:
            """Extract version number from link path for sorting"""
            path = link["path"].lower()
            import re

            # Match glyphs-X-Y-Z-released format
            version_match = re.search(r"glyphs-(\d+)-(\d+)(?:-(\d+))?-released", path)
            if version_match:
                major = int(version_match.group(1))
                minor = int(version_match.group(2))
                patch = int(version_match.group(3)) if version_match.group(3) else 0
                return (major, minor, patch)

            # Match version numbers of other tools
            tool_version_match = re.search(r"-(\d+)-(\d+)(?:-(\d+))?-released", path)
            if tool_version_match:
                major = int(tool_version_match.group(1))
                minor = int(tool_version_match.group(2))
                patch = (
                    int(tool_version_match.group(3))
                    if tool_version_match.group(3)
                    else 0
                )
                return (major, minor, patch)

            # Items without version number go last
            return (0, 0, 0)

        # Sort by version number (newest version first)
        return sorted(released_links, key=extract_version_key, reverse=True)

    def _filter_by_original_query(
        self, sorted_links: list[dict[str, str]], original_query: str
    ) -> list[dict[str, str]]:
        """Return all sorted release articles, let AI determine relevance from titles

        Args:
            sorted_links: Sorted list of links
            original_query: Original query (for logging)

        Returns:
            All found release links (time-sorted), let AI determine relevance
        """
        # Per user request: list all found release articles, let AI determine relevance from titles
        # No keyword filtering here, avoiding over-filtering
        logger.info(
            f"Returning all {len(sorted_links)} release articles for AI to determine relevance to query '{original_query}'"
        )
        return sorted_links[:20]  # Return top 20 newest release articles, providing more options

    def _consolidate_posts_list(
        self, relevant_links: list[dict[str, str]], original_query: str
    ) -> str:
        """Consolidate post list, showing only titles and URLs (without detailed content)

        Args:
            relevant_links: List of relevant links
            original_query: Original query

        Returns:
            Formatted post list
        """
        if not relevant_links:
            return self._no_match_response(original_query)

        consolidated = []
        consolidated.append(f"## 🔍 News Post List for \"{original_query}\"")
        consolidated.append("*(Sorted by newest version, without detailed content)*\n")
        consolidated.append(f"**Found {len(relevant_links)} related posts**\n")

        for i, link in enumerate(relevant_links, 1):
            consolidated.append(f"### {i}. {link['title']}")
            consolidated.append(f"**Link**: {link['url']}")

            # Derive brief description from URL
            if "glyphs-" in link["url"] and "-released" in link["url"]:
                consolidated.append("**Type**: Glyphs official version release")
            elif "released" in link["url"]:
                consolidated.append("**Type**: Tool/plugin release info")
            else:
                consolidated.append("**Type**: Related news")
            consolidated.append("")

        consolidated.append("\n---\n")
        consolidated.append(
            "**Next step**: Use `news_fetch_content(url)` tool to fetch detailed content of a specific post"
        )
        consolidated.append(
            "**Note**: This is only a post list, use fetch tool to view specific content"
        )

        return "\n".join(consolidated)

    async def _parse_rss_feed(self, rss_content: str) -> list[dict[str, Any]]:
        """Parse RSS feed XML content and extract news items

        Args:
            rss_content: XML content of RSS feed

        Returns:
            List of dicts containing news items, each with title, link, description, pub_date
        """
        import xml.etree.ElementTree as ET
        from datetime import datetime

        news_items = []

        try:
            # Parse XML
            root = ET.fromstring(rss_content)

            # Find all item elements
            for item in root.findall(".//item"):
                title_elem = item.find("title")
                link_elem = item.find("link")
                description_elem = item.find("description")
                pub_date_elem = item.find("pubDate")

                # Extract text content
                title = title_elem.text if title_elem is not None else ""
                link = link_elem.text if link_elem is not None else ""
                description = (
                    description_elem.text if description_elem is not None else ""
                )
                pub_date = pub_date_elem.text if pub_date_elem is not None else ""

                # Clean HTML tags (description may contain HTML)
                if description:
                    import re

                    description = re.sub(r"<[^>]+>", "", description).strip()

                # Standardize date format
                formatted_date = ""
                if pub_date:
                    try:
                        # RSS date format example: "Fri, 01 Aug 2025 00:00:00 +0200"
                        parsed_date = datetime.strptime(
                            pub_date[:25], "%a, %d %b %Y %H:%M:%S"
                        )
                        formatted_date = parsed_date.strftime("%Y-%m-%d")
                    except (ValueError, TypeError):
                        # If parsing fails, keep original date
                        formatted_date = (
                            pub_date[:10] if len(pub_date) >= 10 else pub_date
                        )

                if title and link:  # Only keep items with title and link
                    news_items.append(
                        {
                            "title": title.strip(),
                            "link": link.strip(),
                            "description": description,
                            "pub_date": formatted_date,
                            "raw_pub_date": pub_date,
                        }
                    )

        except ET.ParseError as e:
            logger.error(f"RSS XML parsing failed: {e}")
        except Exception as e:
            logger.error(f"Error processing RSS feed: {e}")

        return news_items

    async def _search_in_rss(
        self, news_items: list[dict[str, Any]], query: str
    ) -> list[dict[str, Any]]:
        """Search for related content in RSS news items

        Args:
            news_items: List of news items
            query: Search query

        Returns:
            List of news items matching query, sorted by time (newest first)
        """
        if not news_items or not query.strip():
            return []

        relevant_items = []
        search_terms = query.lower().split()

        for item in news_items:
            # Build search text (title + description)
            search_text = f"{item['title']} {item['description']}".lower()

            # Calculate match score
            match_score = 0
            matched_terms = []

            for term in search_terms:
                if term in search_text:
                    match_score += 1
                    matched_terms.append(term)

                    # Extra points for title match
                    if term in item["title"].lower():
                        match_score += 1

            # If there's a match, add to results
            if match_score > 0:
                item_copy = item.copy()
                item_copy["match_score"] = match_score
                item_copy["matched_terms"] = matched_terms
                relevant_items.append(item_copy)

        # Sort by match score and date (higher score first, then newer first)
        relevant_items.sort(
            key=lambda x: (x["match_score"], x["raw_pub_date"]), reverse=True
        )

        return relevant_items

    def _consolidate_news_search_results(
        self, relevant_items: list[dict[str, Any]], query: str
    ) -> str:
        """Consolidate news search results and format output

        Args:
            relevant_items: List of relevant news items
            query: Original search query

        Returns:
            Formatted search result string
        """
        if not relevant_items:
            return self._no_match_response(query)

        consolidated = []
        consolidated.append(f"## 🔍 Latest Information Search Results for \"{query}\"\n")
        consolidated.append(
            f"**Found {len(relevant_items)} related results** (sorted by relevance and time)\n"
        )

        for i, item in enumerate(relevant_items[:10], 1):  # Limit to top 10 results
            consolidated.append(f"### {i}. {item['title']}")
            consolidated.append(f"**Published**: {item['pub_date']}")
            consolidated.append(f"**Link**: {item['link']}")

            if item["description"]:
                # Limit description length and highlight matched keywords
                description = item["description"]
                if len(description) > 200:
                    description = description[:200] + "..."

                consolidated.append(f"**Summary**: {description}")

            # Display matched keywords (for debugging)
            if "matched_terms" in item and item["matched_terms"]:
                matched_text = ", ".join(item["matched_terms"])
                consolidated.append(f"*Matched keywords: {matched_text}*")

            consolidated.append("")

        consolidated.append("\n---\n")
        consolidated.append("**Note**: These are the most relevant official news for your query.")
        consolidated.append("To view full content, click the links above to visit the official pages.")

        return "\n".join(consolidated)

    def _no_match_response(self, query: str) -> str:
        """Response when no matching results are found

        Args:
            query: Original search query

        Returns:
            Explanation and suggestions for no matches
        """
        return f"""## 🔍 Latest Information Search Results for "{query}"

No related information for "{query}" found in latest news.

**Possible reasons**:
- This feature may already exist in earlier versions
- Different query keywords may be needed
- The tool/feature may not be official Glyphs content

**Alternative suggestions**:
- Handbook search: web_search_handbook("{query}")
- Tutorial search: news_search_tutorials("{query}")
- Forum search: news_search_forum("{query}")

**Manual search**:
- Official news: https://glyphsapp.com/news
- Suggest using WebSearch tool to search related content on the domain above"""

    # Removed unused fallback search methods, unified search logic in SearchEngine

    # Cleaned up unused fallback web search related methods, using SearchEngine uniformly

    def _provide_manual_search_options(self, query: str, reason: str) -> str:
        """Provide manual search options

        Args:
            query: Original query
            reason: Failure reason

        Returns:
            Manual search suggestions
        """
        return f"""## ⚠️ Automatic Search Failed

**Reason**: {reason}

**Manual search suggestions**:
- Official news: https://glyphsapp.com/news
- Suggest using WebSearch tool to search for "{query}"

**Other search options**:
- Handbook search: web_search_handbook("{query}")
- Tutorial search: news_search_tutorials("{query}")
- Forum search: news_search_forum("{query}")

**Common release pages**:
- Glyphs 3.3: https://glyphsapp.com/news/glyphs-3-3-released
- Glyphs 3.2: https://glyphsapp.com/news/glyphs-3-2-released
- Glyphs 3.1: https://glyphsapp.com/news/glyphs-3-1-released"""

    async def web_search_news_posts(self, query: str) -> str:
        """
        [SEARCH] Search Glyphs official news for related posts without fetching detailed content

        Features: Quickly searches and lists related news posts, providing title, URL, and brief description.
        Purpose: Browse all related posts first, then use news_fetch_content tool to fetch detailed content of specific posts.

        Args:
            query: Search keyword (tool name, feature name, version number, etc.)

        Returns:
            Formatted list of news posts including title, URL, and brief description
        """
        if not self.is_initialized:
            return "Glyphs News module not initialized"

        if not query.strip():
            return "Please provide search keywords"

        # Use query processor for preprocessing
        if self.search_engine and self.search_engine.query_processor:
            processed_query, user_language = self.search_engine.query_processor.preprocess_query(query)
        else:
            processed_query = query
            user_language = 'en'

        try:
            # Preprocess query, use only 'released' for search
            search_query, original_query = self._preprocess_news_query(processed_query)

            # Execute search without fetching detailed content
            logger.info(
                f"Searching news post list only: search '{search_query}', original query '{original_query}'"
            )
            result = await self._search_posts_only(search_query, original_query)

            # Use query processor for postprocessing
            if self.search_engine and self.search_engine.query_processor:
                return self.search_engine.query_processor.postprocess_output(result, user_language)
            else:
                return result

        except Exception as e:
            logger.error(f"Error occurred during news post search: {e}")
            return f"""Error occurred during news post search: {e}

**Alternative**:
News domain: https://glyphsapp.com/news
Suggestion: Please use WebSearch to search for "{query}" related news on the domain above"""

    async def web_fetch_news_content(self, url: str) -> str:
        """
        [FETCH] Fetch complete content of a single news post based on provided URL

        Features: Fetches detailed content of specified news post URL.
        Purpose: After finding related posts using news_search_posts tool, get complete information of a specific post.

        Args:
            url: News post URL to fetch (must be from glyphsapp.com/news domain)

        Returns:
            Formatted detailed content of the news post
        """
        if not self.is_initialized:
            return "Glyphs News module not initialized"

        if not url.strip():
            return "Please provide a news post URL to fetch"

        # Validate URL format
        if not url.startswith(("http://", "https://")):
            return "Please provide a complete URL (including http:// or https://)"

        # Validate if it's a Glyphs official news URL
        if "glyphsapp.com/news" not in url:
            return "Please provide a Glyphs official news URL (glyphsapp.com/news)"

        try:
            logger.info(f"Fetching news post content: {url}")
            content, prefix = await self.web_fetcher.fetch_url(url)

            if "<error>" in content:
                return f"""Error occurred while fetching news post content:
{content}

**Alternative**:
Please try visiting directly: {url}"""

            # Format content output
            result = f"## 📰 News Post Content\n**Source**: {url}\n\n"
            if prefix:
                result += f"{prefix}\n"
            result += content

            # Add related tool suggestions
            result += "\n\n---\n"
            result += "**Related tools**:\n"
            result += "- Search more posts: `news_search_posts(query)`\n"
            result += "- Search forum discussions: `news_search_forum(query)`\n"
            result += "- Search tutorials: `news_search_tutorials(query)`"

            return result

        except Exception as e:
            logger.error(f"Failed to fetch news post content {url}: {e}")
            return f"""Error occurred while fetching news post content: {e}

**Alternative**:
Please try visiting directly: {url}"""

    def get_module_info(self) -> dict[str, Any]:
        """Get module information"""
        return {
            "name": self.name,
            "type": "glyphs-news",
            "title": "Glyphs News & Content Module",
            "description": "Real-time search and content fetching for Glyphs.app official news, forum discussions, and tutorials",
            "initialized": self.is_initialized,
            "tools": [
                "news_search_forum",
                "news_search_tutorials",
                "news_fetch_tutorial",
                "news_fetch_forum_post",
                "news_search_posts",
                "news_fetch_content",
            ],
        }

    def get_resources(self) -> dict[str, Any]:
        """Get MCP resources provided by this module"""
        return {"glyphs-news://guide": self._glyphs_news_guide_resource}

    def _glyphs_news_guide_resource(self) -> str:
        """Glyphs News & Content Guide - Real-time content fetching for official resources"""
        return """Glyphs News & Content Module - Real-time Content Fetching

Core Purpose: Real-time search and content fetching for official news, forum discussions, and tutorial resources

Main Domains:
- Tutorial resources: https://glyphsapp.com/learn/
- Community forum: https://forum.glyphsapp.com/
- Official news: https://glyphsapp.com/news

Core Tools:
- news_search_forum: Smart forum search, showing discussion activity and timeline
- news_search_tutorials: Smart search and fetch tutorial content
- news_fetch_tutorial: Directly fetch tutorial content
- news_fetch_forum_post: Precisely fetch forum discussion or specific reply content
- news_search_posts: Search news post list (without fetching detailed content)
- news_fetch_content: Fetch detailed content of specified news post URL

Special Features:
- news_search_forum uses JSON API for smart search, showing discussion activity, reply counts, participants, etc.
- news_search_tutorials integrates official search functionality, auto-parsing and consolidating related tutorial content
- news_fetch_forum_post supports fetching specific reply content and progressive reading, ideal for code suggestions and official responses
- news_search_posts sorts official release info by time, prioritizing newest versions and updates
- Smart relevance sorting, prioritizing most matching results
- Supports mixed Chinese/English queries

Design Features:
- Real-time: Prioritizes fetching latest official resources and community discussions
- Official Focus: Focuses on officially published news, tutorials, and forum content
- Community Interaction: Provides forum discussion activity analysis and progressive content fetching

Notes:
※ API documentation and local cache features have been moved to other specialized modules
※ This module focuses on real-time web content search and fetching
※ Module renamed from websearch to glyphs-news to better reflect its functionality
"""
