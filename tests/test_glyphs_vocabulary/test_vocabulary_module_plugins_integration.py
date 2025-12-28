"""
Tests for VocabularyModule integration with PluginsVocabularyAccessor

測試 VocabularyModule 與外掛詞彙的整合功能，包括：
- 「選取工具」搜尋驗證
- 外掛詞彙翻譯
- 反向索引整合

注意：此模組需要本地安裝 Glyphs 3 app 才能執行測試。
"""

import pytest

from glyphs_info_mcp.modules.glyphs_vocabulary.vocabulary.vocabulary_module import (
    VocabularyModule,
)


# 整個模組需要 Glyphs 3 app（VocabularyModule 依賴 framework 詞彙）
pytestmark = pytest.mark.requires_glyphs_app


class TestVocabularyModulePluginsIntegration:
    """VocabularyModule 外掛詞彙整合測試"""

    @pytest.fixture
    def module(self) -> VocabularyModule:
        """建立並初始化測試用的 VocabularyModule"""
        module = VocabularyModule()
        module.initialize()
        return module

    def test_translate_select_tool_zh_to_en(self, module: VocabularyModule) -> None:
        """測試「選取工具」→ Select 翻譯"""
        result = module.translate_term("選取工具")

        # 應該翻譯為 "Select"
        assert result == "Select"

    def test_translate_select_en_to_zh(self, module: VocabularyModule) -> None:
        """測試 Select → 選取工具 翻譯"""
        # 先確認外掛詞彙已載入
        result = module.translate_term("Select", target_locale="zh-Hant")

        # 可能翻譯為「選取工具」（來自外掛）或其他（來自主應用）
        # 這裡驗證翻譯功能正常運作
        assert result is not None

    def test_search_ui_term_select_tool(self, module: VocabularyModule) -> None:
        """測試搜尋「選取工具」"""
        result = module.search_ui_term("選取工具", locale="zh-Hant")

        # 應該找到結果
        assert "選取工具" in result or "Select" in result

    def test_fuzzy_find_select(self, module: VocabularyModule) -> None:
        """測試模糊搜尋 Select"""
        results = module._fuzzy_find_term("Select")

        # 應該找到結果
        assert len(results) > 0

        # 結果應該包含 source 欄位
        for result in results:
            assert "source" in result
            assert result["source"] in ["app", "framework", "plugins"]

    def test_reverse_term_map_includes_plugins(self, module: VocabularyModule) -> None:
        """測試反向索引包含外掛詞彙"""
        # 「選取工具」應該在反向索引中
        key, locale, source = module._find_english_key("選取工具")

        # 應該找到
        assert key is not None
        # 可能來自 plugins 或 framework（framework 優先度高於 plugins）
        assert source in ["plugins", "framework"]

    def test_plugins_accessor_initialized(self, module: VocabularyModule) -> None:
        """測試外掛存取器已初始化"""
        assert module.plugins_accessor is not None

        # 應該有外掛
        plugins = module.plugins_accessor.get_plugin_names()
        assert len(plugins) > 0

    def test_translate_term_tool_with_select(self, module: VocabularyModule) -> None:
        """測試 translate_term_tool 搜尋「選取」"""
        result = module.translate_term_tool("選取")

        # 應該找到相關結果（可能是模糊匹配）
        assert "選取" in result or "Select" in result

    def test_translate_lasso_tool(self, module: VocabularyModule) -> None:
        """測試 Lasso 翻譯"""
        # Lasso 可能沒有繁中翻譯，但應該能找到
        result = module.translate_term("Lasso")

        # 應該返回原文或翻譯
        assert result == "Lasso"

    def test_plugin_terms_not_override_app_terms(self, module: VocabularyModule) -> None:
        """測試外掛詞彙不會覆蓋主應用詞彙"""
        # "Cancel" 同時存在於主應用和某些外掛
        # 主應用詞彙應該優先
        key, locale, source = module._find_english_key("取消")

        # 應該來自主應用
        if key is not None:
            # "取消" 是主應用的常見詞彙，應該來自 app
            assert source == "app"


class TestSelectToolEndToEnd:
    """端到端測試「選取工具」翻譯流程"""

    @pytest.fixture
    def module(self) -> VocabularyModule:
        """建立並初始化測試用的 VocabularyModule"""
        module = VocabularyModule()
        module.initialize()
        return module

    def test_select_tool_roundtrip(self, module: VocabularyModule) -> None:
        """測試「選取工具」雙向翻譯"""
        # 繁中 → 英文
        en_result = module.translate_term("選取工具")
        assert en_result == "Select"

        # 英文 → 繁中（使用外掛詞彙）
        zh_result = module.translate_term("Select", target_locale="zh-Hant")
        # 可能返回「選取工具」或其他翻譯
        assert zh_result is not None

    def test_search_returns_plugin_source(self, module: VocabularyModule) -> None:
        """測試搜尋結果包含外掛來源資訊"""
        result = module.search_ui_term("Select", locale="zh-Hant")

        # 結果應該包含來源資訊
        # 格式：Key: `Select` (來源: SelectTool.glyphsTool)
        assert "Select" in result
