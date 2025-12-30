"""
Tests for HandbookScraper - Per-page scraping logic
"""

from glyphs_info_mcp.modules.glyphs_handbook.handbook.handbook_scraper import (
    HandbookScraper,
    extract_nav_links_from_html,
)


class TestExtractFilenameFromTitle:
    """Tests for _extract_filename_from_title method"""

    def setup_method(self) -> None:
        """Set up test fixtures"""
        self.scraper = HandbookScraper()

    def test_simple_title(self) -> None:
        """Should convert simple title to filename"""
        filename = self.scraper._extract_filename_from_title("Create")
        assert filename == "create.md"

    def test_title_with_spaces(self) -> None:
        """Should convert spaces to underscores"""
        filename = self.scraper._extract_filename_from_title("Edit View")
        assert filename == "edit_view.md"

    def test_title_with_special_characters(self) -> None:
        """Should remove special characters"""
        filename = self.scraper._extract_filename_from_title("Import & Export")
        assert filename == "import_export.md"

    def test_title_with_ampersand(self) -> None:
        """Should handle ampersand correctly"""
        filename = self.scraper._extract_filename_from_title("Spacing & Kerning")
        assert filename == "spacing_kerning.md"


class TestUrlToFilename:
    """Tests for _url_to_filename method

    New behavior (Issue #17):
    - `/` (path separator) is converted to `_`
    - `-` (word connector) is PRESERVED

    This allows distinguishing hierarchy levels:
    - `/palette/fit-curve/` → `palette_fit-curve.md` (1 level deep)
    - `/palette/fit/curve/` → `palette_fit_curve.md` (2 levels deep)
    """

    def setup_method(self) -> None:
        """Set up test fixtures"""
        self.scraper = HandbookScraper()

    def test_simple_url(self) -> None:
        """Should convert simple URL to filename"""
        filename = self.scraper._url_to_filename("/create/")
        assert filename == "create.md"

    def test_nested_url_preserves_hyphen(self) -> None:
        """Should convert / to _ but PRESERVE hyphens"""
        filename = self.scraper._url_to_filename("/palette/fit-curve/")
        assert filename == "palette_fit-curve.md"

    def test_deeply_nested_url_preserves_hyphen(self) -> None:
        """Should handle deeply nested URLs while preserving hyphens"""
        filename = self.scraper._url_to_filename("/layout/feature-code/")
        assert filename == "layout_feature-code.md"

    def test_url_with_hyphen_only(self) -> None:
        """Should preserve hyphens in single-level URLs"""
        filename = self.scraper._url_to_filename("/custom-parameter-descriptions/")
        assert filename == "custom-parameter-descriptions.md"

    def test_url_without_trailing_slash(self) -> None:
        """Should handle URLs without trailing slash"""
        filename = self.scraper._url_to_filename("/palette/fit-curve")
        assert filename == "palette_fit-curve.md"

    def test_url_without_leading_slash(self) -> None:
        """Should handle URLs without leading slash"""
        filename = self.scraper._url_to_filename("palette/fit-curve/")
        assert filename == "palette_fit-curve.md"

    def test_hierarchy_distinction(self) -> None:
        """Should allow distinguishing hierarchy levels

        This is the key test for Issue #17:
        - Underscore `_` = path separator (hierarchy)
        - Hyphen `-` = word connector (same level)
        """
        # 1 level deep: palette/fit-curve
        filename1 = self.scraper._url_to_filename("/palette/fit-curve/")
        # 2 levels deep: import-export/export
        filename2 = self.scraper._url_to_filename("/import-export/export/")

        # Different patterns should be distinguishable
        assert filename1 == "palette_fit-curve.md"
        assert filename2 == "import-export_export.md"

        # Count underscores to verify hierarchy depth
        assert filename1.count("_") == 1  # 1 level
        assert filename2.count("_") == 1  # 1 level (import-export is single segment)


class TestExtractNavLinksFromHtml:
    """Tests for extract_nav_links_from_html function"""

    def test_extract_simple_nav_links(self) -> None:
        """Should extract simple navigation links"""
        html = """
        <html>
        <nav>
            <a href="/create/">Create</a>
            <a href="/settings/">Settings</a>
        </nav>
        </html>
        """
        links = extract_nav_links_from_html(html)
        assert "/create/" in links
        assert "/settings/" in links

    def test_extract_nested_nav_links(self) -> None:
        """Should extract nested navigation links"""
        html = """
        <html>
        <nav>
            <a href="/palette/">Palette</a>
            <a href="/palette/fit-curve/">Fit Curve</a>
            <a href="/palette/dimensions/">Dimensions</a>
        </nav>
        </html>
        """
        links = extract_nav_links_from_html(html)
        assert "/palette/" in links
        assert "/palette/fit-curve/" in links
        assert "/palette/dimensions/" in links

    def test_filter_anchor_links(self) -> None:
        """Should filter out anchor-only links"""
        html = """
        <html>
        <nav>
            <a href="/create/">Create</a>
            <a href="#section1">Section 1</a>
            <a href="/settings/#anchor">Settings with anchor</a>
        </nav>
        </html>
        """
        links = extract_nav_links_from_html(html)
        assert "/create/" in links
        assert "#section1" not in links
        # Links with anchors should have anchor stripped
        assert "/settings/" in links

    def test_filter_external_links(self) -> None:
        """Should filter out external links"""
        html = """
        <html>
        <nav>
            <a href="/create/">Create</a>
            <a href="https://glyphsapp.com">External</a>
            <a href="http://example.com">Another External</a>
        </nav>
        </html>
        """
        links = extract_nav_links_from_html(html)
        assert "/create/" in links
        assert "https://glyphsapp.com" not in links
        assert "http://example.com" not in links

    def test_deduplicate_links(self) -> None:
        """Should return unique links only"""
        html = """
        <html>
        <nav>
            <a href="/create/">Create</a>
            <a href="/create/">Create Again</a>
            <a href="/settings/">Settings</a>
        </nav>
        </html>
        """
        links = extract_nav_links_from_html(html)
        assert links.count("/create/") == 1
        assert len(links) == 2

    def test_empty_html(self) -> None:
        """Should handle empty HTML gracefully"""
        links = extract_nav_links_from_html("")
        assert links == []

    def test_no_nav_links(self) -> None:
        """Should return empty list when no nav links found"""
        html = "<html><body>No navigation</body></html>"
        links = extract_nav_links_from_html(html)
        assert links == []
