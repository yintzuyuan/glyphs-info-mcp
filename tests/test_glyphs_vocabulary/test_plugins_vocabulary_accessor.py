"""
Tests for PluginsVocabularyAccessor

測試外掛詞彙存取器的功能，包括：
- 外掛發現
- 詞彙解析
- 搜尋功能
- 「選取工具」翻譯驗證

注意：此模組需要本地 Repositories 目錄才能執行測試。
"""

import pytest
from pathlib import Path

from glyphs_info_mcp.modules.glyphs_vocabulary.accessors.plugins_vocabulary_accessor import (
    PluginsVocabularyAccessor,
)


# 整個模組需要 Repositories 目錄
pytestmark = pytest.mark.requires_repositories


class TestPluginsVocabularyAccessor:
    """PluginsVocabularyAccessor 測試類別"""

    @pytest.fixture
    def accessor(self) -> PluginsVocabularyAccessor:
        """建立測試用的 accessor"""
        return PluginsVocabularyAccessor()

    def test_discover_plugins(self, accessor: PluginsVocabularyAccessor) -> None:
        """測試外掛發現功能"""
        plugins = accessor.get_plugin_names()

        # 應該找到多個外掛
        assert len(plugins) > 0

        # 應該包含 SelectTool
        assert "SelectTool.glyphsTool" in plugins

    def test_get_plugin_terms_english(self, accessor: PluginsVocabularyAccessor) -> None:
        """測試取得外掛英文詞彙"""
        terms = accessor.get_plugin_terms("SelectTool.glyphsTool", "en")

        # SelectTool 應該有詞彙
        assert len(terms) > 0

        # 應該包含 "Select" 詞彙
        assert "Select" in terms
        assert terms["Select"] == "Select"

    def test_get_plugin_terms_chinese(self, accessor: PluginsVocabularyAccessor) -> None:
        """測試取得外掛繁體中文詞彙"""
        terms = accessor.get_plugin_terms("SelectTool.glyphsTool", "zh-Hant")

        # SelectTool 應該有繁體中文詞彙
        assert len(terms) > 0

        # "Select" 應該翻譯為「選取工具」
        assert "Select" in terms
        assert terms["Select"] == "選取工具"

    def test_get_all_terms_with_prefix(self, accessor: PluginsVocabularyAccessor) -> None:
        """測試取得所有詞彙（含外掛前綴）"""
        all_terms = accessor.get_all_terms("en")

        # 應該有多個詞彙
        assert len(all_terms) > 0

        # Key 應該包含外掛前綴
        select_key = "SelectTool.glyphsTool/Select"
        assert select_key in all_terms

    def test_get_all_terms_flat(self, accessor: PluginsVocabularyAccessor) -> None:
        """測試取得所有詞彙（扁平化）"""
        all_terms = accessor.get_all_terms_flat("en")

        # 應該有多個詞彙
        assert len(all_terms) > 0

        # Key 不應該包含外掛前綴
        assert "Select" in all_terms

    def test_search_term_english(self, accessor: PluginsVocabularyAccessor) -> None:
        """測試英文搜尋"""
        results = accessor.search_term("Select", locale="en")

        # 應該找到結果
        assert len(results) > 0

        # 結果應該包含 plugin 資訊
        first_result = results[0]
        assert "key" in first_result
        assert "value" in first_result
        assert "plugin" in first_result

    def test_search_term_chinese(self, accessor: PluginsVocabularyAccessor) -> None:
        """測試繁體中文搜尋"""
        results = accessor.search_term("選取工具", locale="zh-Hant")

        # 應該找到結果
        assert len(results) > 0

        # 應該找到 SelectTool 的詞彙
        found_select_tool = False
        for result in results:
            if result["plugin"] == "SelectTool.glyphsTool":
                found_select_tool = True
                break
        assert found_select_tool

    def test_get_statistics(self, accessor: PluginsVocabularyAccessor) -> None:
        """測試詞彙統計"""
        stats = accessor.get_statistics()

        # 應該有統計資訊
        assert "plugin_count" in stats
        assert "total_terms" in stats
        assert "plugins" in stats

        # 統計數字應該大於 0
        assert stats["plugin_count"] > 0
        assert stats["total_terms"] > 0

    def test_nonexistent_plugin(self, accessor: PluginsVocabularyAccessor) -> None:
        """測試不存在的外掛"""
        terms = accessor.get_plugin_terms("NonExistent.glyphsTool", "en")

        # 應該返回空字典
        assert terms == {}

    def test_nonexistent_locale(self, accessor: PluginsVocabularyAccessor) -> None:
        """測試不存在的語系"""
        terms = accessor.get_plugin_terms("SelectTool.glyphsTool", "xx-XX")

        # 應該返回空字典
        assert terms == {}

    def test_cache_functionality(self, accessor: PluginsVocabularyAccessor) -> None:
        """測試快取功能"""
        # 第一次取得
        terms1 = accessor.get_all_terms("en")

        # 第二次取得（應該從快取）
        terms2 = accessor.get_all_terms("en")

        # 應該是同一個物件（快取）
        assert terms1 is terms2


class TestSelectToolTranslation:
    """專門測試「選取工具」翻譯的測試類別"""

    @pytest.fixture
    def accessor(self) -> PluginsVocabularyAccessor:
        """建立測試用的 accessor"""
        return PluginsVocabularyAccessor()

    def test_select_tool_en_to_zh(self, accessor: PluginsVocabularyAccessor) -> None:
        """測試 Select → 選取工具 翻譯"""
        en_terms = accessor.get_plugin_terms("SelectTool.glyphsTool", "en")
        zh_terms = accessor.get_plugin_terms("SelectTool.glyphsTool", "zh-Hant")

        # 英文有 "Select"
        assert "Select" in en_terms

        # 繁中翻譯為「選取工具」
        assert zh_terms.get("Select") == "選取工具"

    def test_select_all_layers_translation(self, accessor: PluginsVocabularyAccessor) -> None:
        """測試 Select All Layers → 選取所有圖層工具 翻譯"""
        en_terms = accessor.get_plugin_terms("SelectTool.glyphsTool", "en")
        zh_terms = accessor.get_plugin_terms("SelectTool.glyphsTool", "zh-Hant")

        # 英文有 "Select All Layers"
        assert "Select All Layers" in en_terms

        # 繁中翻譯
        assert zh_terms.get("Select All Layers") == "選取所有圖層工具"

    def test_lasso_tool_translation(self, accessor: PluginsVocabularyAccessor) -> None:
        """測試 Lasso 翻譯"""
        en_terms = accessor.get_plugin_terms("SelectTool.glyphsTool", "en")
        zh_terms = accessor.get_plugin_terms("SelectTool.glyphsTool", "zh-Hant")

        # 英文有 "Lasso"
        assert "Lasso" in en_terms

        # 繁中可能沒有翻譯（保留英文）
        # 根據實際檔案內容檢查
        assert "Lasso" in zh_terms
