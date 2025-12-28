"""測試查詢處理工具模組"""

import pytest


class TestTokenizeQuery:
    """測試分詞功能"""

    def test_basic_tokenization(self) -> None:
        """基本分詞"""
        from glyphs_info_mcp.shared.core.query_utils import tokenize_query

        result = tokenize_query("python api search")
        assert result == ["python", "api", "search"]

    def test_filters_short_words_default(self) -> None:
        """預設過濾短於 2 字元的詞彙"""
        from glyphs_info_mcp.shared.core.query_utils import tokenize_query

        result = tokenize_query("a is the python api")
        # "a" 被過濾（長度 1），"is" 和 "the" 保留（長度 >= 2）
        assert "a" not in result
        assert "is" in result
        assert "the" in result
        assert "python" in result
        assert "api" in result

    def test_filters_short_words_custom_length(self) -> None:
        """自訂最小詞彙長度"""
        from glyphs_info_mcp.shared.core.query_utils import tokenize_query

        result = tokenize_query("a is the python api", min_length=3)
        # 長度 < 3 的都被過濾
        assert "a" not in result
        assert "is" not in result
        assert "the" in result
        assert "python" in result
        assert "api" in result

    def test_converts_to_lowercase(self) -> None:
        """轉換為小寫"""
        from glyphs_info_mcp.shared.core.query_utils import tokenize_query

        result = tokenize_query("Python API Search")
        assert result == ["python", "api", "search"]

    def test_empty_query(self) -> None:
        """空查詢"""
        from glyphs_info_mcp.shared.core.query_utils import tokenize_query

        result = tokenize_query("")
        assert result == []

    def test_only_short_words(self) -> None:
        """只有短詞彙"""
        from glyphs_info_mcp.shared.core.query_utils import tokenize_query

        result = tokenize_query("a b c", min_length=2)
        assert result == []


class TestNormalizeForMatching:
    """測試正規化功能"""

    def test_converts_to_lowercase(self) -> None:
        """轉換為小寫"""
        from glyphs_info_mcp.shared.core.query_utils import normalize_for_matching

        assert normalize_for_matching("GSFont") == "gsfont"

    def test_removes_hyphens(self) -> None:
        """移除連字號"""
        from glyphs_info_mcp.shared.core.query_utils import normalize_for_matching

        assert normalize_for_matching("Show-Stems") == "showstems"

    def test_removes_underscores(self) -> None:
        """移除底線"""
        from glyphs_info_mcp.shared.core.query_utils import normalize_for_matching

        assert normalize_for_matching("Show_Stems") == "showstems"

    def test_combined_normalization(self) -> None:
        """組合正規化"""
        from glyphs_info_mcp.shared.core.query_utils import normalize_for_matching

        assert normalize_for_matching("Show-Crosshair_Plugin") == "showcrosshairplugin"

    def test_already_normalized(self) -> None:
        """已正規化的字串"""
        from glyphs_info_mcp.shared.core.query_utils import normalize_for_matching

        assert normalize_for_matching("showstems") == "showstems"


class TestCaseInsensitiveContains:
    """測試大小寫不敏感包含檢查"""

    def test_exact_case_match(self) -> None:
        """完全大小寫匹配"""
        from glyphs_info_mcp.shared.core.query_utils import case_insensitive_contains

        assert case_insensitive_contains("GSFont", "GSFont") is True

    def test_lowercase_query(self) -> None:
        """小寫查詢"""
        from glyphs_info_mcp.shared.core.query_utils import case_insensitive_contains

        assert case_insensitive_contains("GSFont", "gsfont") is True

    def test_uppercase_query(self) -> None:
        """大寫查詢"""
        from glyphs_info_mcp.shared.core.query_utils import case_insensitive_contains

        assert case_insensitive_contains("GSFont", "GSFONT") is True

    def test_partial_match(self) -> None:
        """部分匹配"""
        from glyphs_info_mcp.shared.core.query_utils import case_insensitive_contains

        assert case_insensitive_contains("GSFont", "font") is True

    def test_no_match(self) -> None:
        """不匹配"""
        from glyphs_info_mcp.shared.core.query_utils import case_insensitive_contains

        assert case_insensitive_contains("GSFont", "layer") is False


class TestCalculateMatchScore:
    """測試匹配分數計算"""

    def test_exact_match_with_case(self) -> None:
        """完全匹配（含大小寫）得最高分"""
        from glyphs_info_mcp.shared.core.query_utils import calculate_match_score

        assert calculate_match_score("GSFont", "GSFont") == 1.0

    def test_exact_match_different_case(self) -> None:
        """大小寫不同的完全匹配得 0.95"""
        from glyphs_info_mcp.shared.core.query_utils import calculate_match_score

        assert calculate_match_score("gsfont", "GSFont") == 0.95
        assert calculate_match_score("GSFONT", "GSFont") == 0.95

    def test_contains_match(self) -> None:
        """包含匹配得 0.6"""
        from glyphs_info_mcp.shared.core.query_utils import calculate_match_score

        assert calculate_match_score("font", "GSFont") == 0.6

    def test_no_match(self) -> None:
        """不匹配得 0"""
        from glyphs_info_mcp.shared.core.query_utils import calculate_match_score

        assert calculate_match_score("layer", "GSFont") == 0.0

    def test_case_insensitive_contains(self) -> None:
        """大小寫不敏感的包含匹配"""
        from glyphs_info_mcp.shared.core.query_utils import calculate_match_score

        assert calculate_match_score("FONT", "GSFont") == 0.6


class TestMinWordLength:
    """測試 MIN_WORD_LENGTH 常數"""

    def test_min_word_length_is_two(self) -> None:
        """MIN_WORD_LENGTH 應為 2"""
        from glyphs_info_mcp.shared.core.query_utils import MIN_WORD_LENGTH

        assert MIN_WORD_LENGTH == 2
