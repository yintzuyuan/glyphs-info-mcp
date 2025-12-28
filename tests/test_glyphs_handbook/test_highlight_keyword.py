"""
測試 highlight_keyword() 關鍵字高亮功能

Issue #77: 搜尋結果中關鍵字被不當大寫加粗顯示
修復目標: 保持原始大小寫，僅加粗不改大小寫

重構：將 _highlight_keyword 提取到 query_utils.py 共用模組
"""

import pytest

from glyphs_info_mcp.shared.core.query_utils import highlight_keyword


class TestHighlightKeyword:
    """測試 highlight_keyword() 共用函式"""

    def test_preserves_original_case(self) -> None:
        """高亮應保留原始大小寫"""
        # given - 使用完整匹配的關鍵字
        text = "The Anchor is a special point."
        keyword = "anchor"

        # when
        result = highlight_keyword(text, keyword)

        # then
        assert result == "The **Anchor** is a special point."

    def test_highlights_all_occurrences_with_original_case(self) -> None:
        """應高亮所有出現的關鍵字並保留各自的大小寫"""
        # given
        text = "Anchor to anchor connection with ANCHOR support."
        keyword = "anchor"

        # when
        result = highlight_keyword(text, keyword)

        # then
        assert result == "**Anchor** to **anchor** connection with **ANCHOR** support."

    def test_partial_match_preserves_surrounding_text(self) -> None:
        """部分匹配時應保留周圍的文字"""
        # given - "anchor" 匹配 "Anchors" 中的 "Anchor" 部分
        text = "Anchors are special points."
        keyword = "anchor"

        # when
        result = highlight_keyword(text, keyword)

        # then
        assert result == "**Anchor**s are special points."

    def test_case_insensitive_matching(self) -> None:
        """應不區分大小寫進行匹配"""
        # given
        text = "The INTERPOLATION axis supports interpolation."
        keyword = "interpolation"

        # when
        result = highlight_keyword(text, keyword)

        # then
        assert result == "The **INTERPOLATION** axis supports **interpolation**."

    def test_preserves_non_matching_text(self) -> None:
        """不匹配的文字應保持不變"""
        # given
        text = "Anchors are special points that fulfill tasks."
        keyword = "anchor"

        # when
        result = highlight_keyword(text, keyword)

        # then
        assert "special points" in result
        assert "fulfill tasks" in result

    def test_handles_empty_text(self) -> None:
        """空文字應返回空字串"""
        result = highlight_keyword("", "keyword")
        assert result == ""

    def test_handles_empty_keyword(self) -> None:
        """空關鍵字應返回原文"""
        text = "Some text here."
        result = highlight_keyword(text, "")
        assert result == text

    def test_handles_no_match(self) -> None:
        """無匹配時應返回原文"""
        # given
        text = "Some text without the keyword."
        keyword = "missing"

        # when
        result = highlight_keyword(text, keyword)

        # then
        assert result == text

    def test_single_word_exact_match(self) -> None:
        """單字完全匹配"""
        result = highlight_keyword("anchor", "anchor")
        assert result == "**anchor**"

    def test_multiple_same_case_occurrences(self) -> None:
        """多個相同大小寫的出現"""
        text = "Anchor and Anchor again."
        result = highlight_keyword(text, "anchor")
        assert result == "**Anchor** and **Anchor** again."
