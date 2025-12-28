"""
測試 _extract_title() 方法

Issue #76: handbook_search_content 返回「未命名章節」而非正確標題
根本原因：_extract_title 只查找一級標題，但 handbook 檔案使用二級標題格式
"""

from glyphs_info_mcp.modules.glyphs_handbook.handbook.enhanced_search import (
    EnhancedHandbookSearcher,
)


class TestExtractTitle:
    """測試 _extract_title() 靜態方法"""

    def test_extracts_h1_title(self) -> None:
        """應正確提取一級標題"""
        content = "# Main Title\n\nContent here"
        title = EnhancedHandbookSearcher._extract_title(content)
        assert title == "Main Title"

    def test_extracts_h2_title_when_no_h1(self) -> None:
        """無一級標題時，應提取二級標題"""
        content = "## [Anchors](#anchors)\n\nAnchors are special points."
        title = EnhancedHandbookSearcher._extract_title(content)
        assert title == "Anchors"

    def test_extracts_h2_with_markdown_link(self) -> None:
        """應正確處理 Markdown 連結語法（含空格的標題）"""
        content = "## [Mark to Base Positioning](#mark-positioning)\n\nContent"
        title = EnhancedHandbookSearcher._extract_title(content)
        assert title == "Mark to Base Positioning"

    def test_prefers_h1_over_h2(self) -> None:
        """同時存在時，應優先使用一級標題"""
        content = "# Main Title\n## Sub Section\nContent"
        title = EnhancedHandbookSearcher._extract_title(content)
        assert title == "Main Title"

    def test_returns_fallback_when_no_heading(self) -> None:
        """無任何標題時，返回預設值"""
        content = "Just some content without headings"
        title = EnhancedHandbookSearcher._extract_title(content)
        assert title == "Unnamed chapter"

    def test_handles_empty_content(self) -> None:
        """空內容應返回預設值"""
        title = EnhancedHandbookSearcher._extract_title("")
        assert title == "Unnamed chapter"

    def test_handles_h2_without_link_syntax(self) -> None:
        """應處理不含連結語法的二級標題"""
        content = "## Simple Heading\n\nContent here"
        title = EnhancedHandbookSearcher._extract_title(content)
        assert title == "Simple Heading"

    def test_real_handbook_format(self) -> None:
        """測試真實 handbook 檔案格式"""
        content = """## [Anchors](#anchors)

Anchors are special points that fulfill multiple tasks in Glyphs.
They primarily serve as a connecting pivot for automatically aligning components.

### [Adding, Editing, & Removing Anchors](#anchors/adding)

Insert an anchor by `Control`-clicking.
"""
        title = EnhancedHandbookSearcher._extract_title(content)
        assert title == "Anchors"

    def test_strips_whitespace(self) -> None:
        """應移除標題前後的空白"""
        content = "##   [Spaced Title](#anchor)  \n\nContent"
        title = EnhancedHandbookSearcher._extract_title(content)
        assert title == "Spaced Title"
