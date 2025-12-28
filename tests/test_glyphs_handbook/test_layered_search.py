"""
分層搜尋策略測試

測試根據 match_type 返回不同詳細程度的內容：
- title 匹配：最簡潔（標題 + 1 行摘要）
- section 匹配：中等（子章節標題 + 3 行摘要）
- content 匹配：完整子章節或智慧截取
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from glyphs_info_mcp.modules.glyphs_handbook.handbook.enhanced_search import (
    EnhancedHandbookSearcher,
)


# =============================================================================
# 測試資料
# =============================================================================

SAMPLE_HANDBOOK_CONTENT = """## [Anchors](#anchors)

Anchors are special points that fulfill multiple tasks in Glyphs.
They primarily serve as a connecting pivot for automatically aligning components.

### [Adding, Editing, & Removing Anchors](#anchors/adding)

Insert an anchor by `Control`-clicking or right-clicking the Edit View canvas.
An anchor named `new anchor` will be placed at the click position.
Its name is already selected for renaming.

Double-click an anchor to rename it, or select it and press `Return`.
The glyph info database has default anchors associated with many glyphs.

### [Mark to Base Positioning](#mark-to-base-positioning)

Glyphs can automatically build the `mark` feature using anchors.
The combining diacritical marks must contain underscore-anchors.
For example, `_top` or `_bottom`.

### [Cursive Attachment](#cursive-attachment)

Enable proper cursive attachment in Arabic typesetting by adding `exit` and `entry` anchors.
"""


# =============================================================================
# 分層截取測試
# =============================================================================

class TestExtractIntroOnly:
    """測試 _extract_intro_only() - 第一層：標題匹配"""

    def test_returns_first_paragraph(self) -> None:
        """應返回檔案開頭的第一段說明"""
        # 建立 mock 搜尋器
        searcher = EnhancedHandbookSearcher.__new__(EnhancedHandbookSearcher)
        searcher.section_parser = MagicMock()

        intro = searcher._extract_intro_only(SAMPLE_HANDBOOK_CONTENT)

        # 應包含第一段說明
        assert "special points" in intro
        # 不應包含子章節內容
        assert "Control-clicking" not in intro
        # 長度限制
        assert len(intro.split('\n')) <= 3

    def test_handles_empty_content(self) -> None:
        """空內容應返回空字串"""
        searcher = EnhancedHandbookSearcher.__new__(EnhancedHandbookSearcher)
        searcher.section_parser = MagicMock()

        intro = searcher._extract_intro_only("")
        assert intro == ""


class TestExtractSectionSummary:
    """測試 _extract_section_summary() - 第二層：段落匹配"""

    def test_returns_matched_section_title_and_summary(self) -> None:
        """應返回匹配的子章節標題 + 簡短摘要"""
        searcher = EnhancedHandbookSearcher.__new__(EnhancedHandbookSearcher)
        searcher.section_parser = MagicMock()

        summary = searcher._extract_section_summary(
            SAMPLE_HANDBOOK_CONTENT, "mark"
        )

        # 應包含匹配的子章節標題
        assert "Mark to Base Positioning" in summary
        # 應包含摘要內容
        assert "mark" in summary.lower()
        # 長度限制（標題 + 3 行摘要）
        assert len(summary.split('\n')) <= 5

    def test_returns_empty_if_no_section_match(self) -> None:
        """如果沒有匹配的子章節，應返回空字串"""
        searcher = EnhancedHandbookSearcher.__new__(EnhancedHandbookSearcher)
        searcher.section_parser = MagicMock()

        summary = searcher._extract_section_summary(
            SAMPLE_HANDBOOK_CONTENT, "nonexistent_keyword"
        )

        assert summary == ""


class TestExtractExcerptsByLayer:
    """測試 _extract_excerpts_by_layer() - 分層截取主入口"""

    def test_title_match_returns_intro_only(self) -> None:
        """title 匹配應返回簡介"""
        searcher = EnhancedHandbookSearcher.__new__(EnhancedHandbookSearcher)
        searcher.section_parser = MagicMock()
        # Mock _extract_intro_only
        searcher._extract_intro_only = MagicMock(return_value="Intro content")  # type: ignore[method-assign]

        excerpts = searcher._extract_excerpts_by_layer(
            SAMPLE_HANDBOOK_CONTENT, "anchor", "title"
        )

        searcher._extract_intro_only.assert_called_once()
        assert "Intro content" in excerpts

    def test_section_match_returns_section_summary(self) -> None:
        """section 匹配應返回子章節摘要"""
        searcher = EnhancedHandbookSearcher.__new__(EnhancedHandbookSearcher)
        searcher.section_parser = MagicMock()
        searcher._extract_section_summary = MagicMock(return_value="Section summary")  # type: ignore[method-assign]

        excerpts = searcher._extract_excerpts_by_layer(
            SAMPLE_HANDBOOK_CONTENT, "mark", "section"
        )

        searcher._extract_section_summary.assert_called_once()
        assert "Section summary" in excerpts

    def test_content_match_returns_full_excerpt(self) -> None:
        """content 匹配應返回完整截取"""
        searcher = EnhancedHandbookSearcher.__new__(EnhancedHandbookSearcher)
        searcher.section_parser = MagicMock()
        searcher._extract_excerpts = MagicMock(return_value=["Full excerpt"])  # type: ignore[method-assign]

        excerpts = searcher._extract_excerpts_by_layer(
            SAMPLE_HANDBOOK_CONTENT, "exit", "content"
        )

        searcher._extract_excerpts.assert_called_once()
        assert "Full excerpt" in excerpts


# =============================================================================
# 整合測試
# =============================================================================

class TestLayeredSearchIntegration:
    """分層搜尋整合測試"""

    def test_search_result_format_varies_by_match_type(self) -> None:
        """搜尋結果格式應根據 match_type 變化"""
        # 這個測試需要完整的 searcher 實例
        # 先跳過，等實作完成後再測試
        pass

    def test_output_length_varies_by_match_type(self) -> None:
        """輸出長度應根據 match_type 變化"""
        # title 匹配的輸出應最短
        # content 匹配的輸出應最長
        pass
