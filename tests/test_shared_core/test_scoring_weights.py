"""測試統一評分權重模組"""

import pytest


class TestMatchTypeWeights:
    """測試匹配類型權重常數"""

    def test_exact_is_highest(self) -> None:
        """完全匹配應有最高分數 1.0"""
        from glyphs_info_mcp.shared.core.scoring_weights import MatchTypeWeights

        assert MatchTypeWeights.EXACT == 1.0

    def test_prefix_higher_than_contains(self) -> None:
        """前綴匹配應高於包含匹配"""
        from glyphs_info_mcp.shared.core.scoring_weights import MatchTypeWeights

        assert MatchTypeWeights.PREFIX > MatchTypeWeights.CONTAINS

    def test_all_weights_in_valid_range(self) -> None:
        """所有權重應在 0.0-1.0 範圍內"""
        from glyphs_info_mcp.shared.core.scoring_weights import MatchTypeWeights

        for attr in ["EXACT", "PREFIX", "CONTAINS"]:
            value = getattr(MatchTypeWeights, attr)
            assert 0.0 <= value <= 1.0, f"{attr} = {value} 超出範圍"


class TestFieldWeights:
    """測試欄位權重常數"""

    def test_title_higher_than_description(self) -> None:
        """標題權重應高於描述"""
        from glyphs_info_mcp.shared.core.scoring_weights import FieldWeights

        assert FieldWeights.TITLE > FieldWeights.DESCRIPTION

    def test_name_higher_than_content(self) -> None:
        """名稱權重應高於內容"""
        from glyphs_info_mcp.shared.core.scoring_weights import FieldWeights

        assert FieldWeights.NAME > FieldWeights.CONTENT

    def test_owner_equals_author(self) -> None:
        """OWNER 和 AUTHOR 應有相同權重"""
        from glyphs_info_mcp.shared.core.scoring_weights import FieldWeights

        assert FieldWeights.OWNER == FieldWeights.AUTHOR

    def test_all_weights_in_valid_range(self) -> None:
        """所有權重應在 0.0-1.0 範圍內"""
        from glyphs_info_mcp.shared.core.scoring_weights import FieldWeights

        for attr in ["TITLE", "NAME", "OWNER", "AUTHOR", "DESCRIPTION", "CONTENT", "PATH"]:
            value = getattr(FieldWeights, attr)
            assert 0.0 <= value <= 1.0, f"{attr} = {value} 超出範圍"


class TestBackwardsCompatibility:
    """測試向後相容別名"""

    def test_score_exact_match_equals_exact(self) -> None:
        """SCORE_EXACT_MATCH 應等於 MatchTypeWeights.EXACT"""
        from glyphs_info_mcp.shared.core.scoring_weights import (
            SCORE_EXACT_MATCH,
            MatchTypeWeights,
        )

        assert SCORE_EXACT_MATCH == MatchTypeWeights.EXACT

    def test_score_title_match_equals_title(self) -> None:
        """SCORE_TITLE_MATCH 應等於 FieldWeights.TITLE"""
        from glyphs_info_mcp.shared.core.scoring_weights import SCORE_TITLE_MATCH, FieldWeights

        assert SCORE_TITLE_MATCH == FieldWeights.TITLE

    def test_score_name_match_equals_name(self) -> None:
        """SCORE_NAME_MATCH 應等於 FieldWeights.NAME"""
        from glyphs_info_mcp.shared.core.scoring_weights import SCORE_NAME_MATCH, FieldWeights

        assert SCORE_NAME_MATCH == FieldWeights.NAME

    def test_score_owner_match_equals_owner(self) -> None:
        """SCORE_OWNER_MATCH 應等於 FieldWeights.OWNER"""
        from glyphs_info_mcp.shared.core.scoring_weights import SCORE_OWNER_MATCH, FieldWeights

        assert SCORE_OWNER_MATCH == FieldWeights.OWNER

    def test_score_desc_match_equals_description(self) -> None:
        """SCORE_DESC_MATCH 應等於 FieldWeights.DESCRIPTION"""
        from glyphs_info_mcp.shared.core.scoring_weights import SCORE_DESC_MATCH, FieldWeights

        assert SCORE_DESC_MATCH == FieldWeights.DESCRIPTION


class TestCodeStructureWeights:
    """測試程式碼結構權重常數"""

    def test_class_exact_higher_than_contains(self) -> None:
        """類別精確匹配應高於包含匹配"""
        from glyphs_info_mcp.shared.core.scoring_weights import CodeStructureWeights

        assert CodeStructureWeights.CLASS_EXACT > CodeStructureWeights.CLASS_CONTAINS

    def test_method_weights_exist(self) -> None:
        """方法權重應存在"""
        from glyphs_info_mcp.shared.core.scoring_weights import CodeStructureWeights

        assert hasattr(CodeStructureWeights, "METHOD_EXACT")
        assert hasattr(CodeStructureWeights, "METHOD_CONTAINS")


class TestMultiWordWeights:
    """測試多詞搜尋權重常數"""

    def test_multi_word_bonus_exists(self) -> None:
        """多詞匹配加分應存在"""
        from glyphs_info_mcp.shared.core.scoring_weights import MultiWordWeights

        assert hasattr(MultiWordWeights, "MULTI_WORD_BONUS")
        assert MultiWordWeights.MULTI_WORD_BONUS == 0.3

    def test_partial_word_exists(self) -> None:
        """部分詞彙匹配權重應存在"""
        from glyphs_info_mcp.shared.core.scoring_weights import MultiWordWeights

        assert hasattr(MultiWordWeights, "PARTIAL_WORD")
        assert MultiWordWeights.PARTIAL_WORD == 0.1

    def test_all_weights_in_valid_range(self) -> None:
        """所有權重應在 0.0-1.0 範圍內"""
        from glyphs_info_mcp.shared.core.scoring_weights import MultiWordWeights

        for attr in [
            "HIGH_MATCH_THRESHOLD",
            "MEDIUM_MATCH_THRESHOLD",
            "HIGH_MATCH_BASE",
            "MEDIUM_MATCH_BASE",
            "QUALITY_BONUS_MAX",
            "DENSITY_BONUS_MAX",
            "MULTI_WORD_BONUS",
            "PARTIAL_WORD",
        ]:
            value = getattr(MultiWordWeights, attr)
            assert 0.0 <= value <= 1.0, f"{attr} = {value} 超出範圍"
