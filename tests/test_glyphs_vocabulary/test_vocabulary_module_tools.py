"""
測試 VocabularyModule 的公開 MCP 工具

特別測試新增的 vocab_translate_term 工具
"""

from pathlib import Path

import pytest

from glyphs_info_mcp.modules.glyphs_vocabulary.vocabulary.vocabulary_module import VocabularyModule


class TestVocabularyModuleTools:
    """測試 VocabularyModule 的公開工具"""

    @pytest.fixture
    def temp_resources(self, tmp_path: Path) -> Path:
        """建立測試用的 Glyphs resources 目錄"""
        resources_dir = tmp_path / "Resources"
        resources_dir.mkdir()

        # 建立英文資料夾
        en_dir = resources_dir / "en.lproj"
        en_dir.mkdir()

        # 建立繁體中文資料夾
        zh_hant_dir = resources_dir / "zh-Hant.lproj"
        zh_hant_dir.mkdir()

        # 建立日文資料夾
        ja_dir = resources_dir / "ja.lproj"
        ja_dir.mkdir()

        # 建立英文 Localizable.strings
        en_localizable = en_dir / "Localizable.strings"
        en_localizable.write_text(
            """/* Common UI */
"Cancel" = "Cancel";
"OK" = "OK";
"Add" = "Add";
"Remove" = "Remove";
"File" = "File";
"Edit" = "Edit";
"Has Anchors" = "Has Anchors";
"Anchors" = "Anchors";
"Anchor to Anchor" = "Anchor to Anchor";
""",
            encoding="utf-8",
        )

        # 建立繁體中文 Localizable.strings
        zh_hant_localizable = zh_hant_dir / "Localizable.strings"
        zh_hant_localizable.write_text(
            """/* Common UI */
"Cancel" = "取消";
"OK" = "好";
"Add" = "新增";
"Remove" = "移除";
"File" = "檔案";
"Edit" = "編輯";
"Has Anchors" = "包含錨點";
"Anchors" = "錨點";
"Anchor to Anchor" = "錨點間";
""",
            encoding="utf-8",
        )

        # 建立日文 Localizable.strings
        ja_localizable = ja_dir / "Localizable.strings"
        ja_localizable.write_text(
            """/* Common UI */
"Cancel" = "キャンセル";
"OK" = "OK";
"Add" = "追加";
"Remove" = "削除";
"File" = "ファイル";
"Edit" = "編集";
"Has Anchors" = "アンカーあり";
"Anchors" = "アンカー";
"Anchor to Anchor" = "アンカー間";
""",
            encoding="utf-8",
        )

        return resources_dir

    @pytest.fixture
    def vocabulary_module(self, temp_resources: Path) -> VocabularyModule:
        """建立測試用的 VocabularyModule（使用隔離的測試環境）"""
        from unittest.mock import MagicMock

        from glyphs_info_mcp.modules.glyphs_vocabulary.accessors.ui_vocabulary_native_accessor import (
            UIVocabularyNativeAccessor,
        )

        module = VocabularyModule()
        module.ui_accessor = UIVocabularyNativeAccessor(resources_path=temp_resources)

        # Mock plugins_accessor 以避免載入真實外掛詞彙
        mock_plugins_accessor = MagicMock()
        mock_plugins_accessor.get_all_terms_flat.return_value = {}
        mock_plugins_accessor.get_plugin_names.return_value = []
        module.plugins_accessor = mock_plugins_accessor

        module.initialize()
        return module

    def test_get_tools_includes_translate_term(
        self, vocabulary_module: VocabularyModule
    ) -> None:
        """測試 get_tools() 包含 vocab_translate_term"""
        tools = vocabulary_module.get_tools()

        assert "vocab_translate_term" in tools
        assert callable(tools["vocab_translate_term"])

    def test_get_tools_count(self, vocabulary_module: VocabularyModule) -> None:
        """測試工具數量（應該是 4 個）"""
        tools = vocabulary_module.get_tools()

        assert len(tools) == 4
        expected_tools = [
            "vocab_search_ui_term",
            "vocab_get_translation",
            "vocab_list_ui_categories",
            "vocab_translate_term",
        ]
        for tool_name in expected_tools:
            assert tool_name in tools

    def test_translate_term_tool_zh_to_en(self, vocabulary_module: VocabularyModule) -> None:
        """測試翻譯工具：中文到英文（auto 模式）"""
        result = vocabulary_module.translate_term_tool("取消")

        assert "## ✅" in result and ("翻譯成功" in result or "Translation Successful" in result)
        assert ("**原文:**" in result or "**Original:**" in result) and "取消" in result
        assert ("**翻譯:**" in result or "**Translation:**" in result) and "Cancel" in result
        assert "**目標語系:**" in result or "**Target Locale:**" in result

    def test_translate_term_tool_en_to_ja(self, vocabulary_module: VocabularyModule) -> None:
        """測試翻譯工具：英文到日文"""
        result = vocabulary_module.translate_term_tool("Cancel", target_locale="ja")

        assert "## ✅" in result and ("翻譯成功" in result or "Translation Successful" in result)
        assert ("**原文:**" in result or "**Original:**" in result) and "Cancel" in result
        assert ("**翻譯:**" in result or "**Translation:**" in result) and "キャンセル" in result
        assert "ja" in result

    def test_translate_term_tool_ja_to_en(self, vocabulary_module: VocabularyModule) -> None:
        """測試翻譯工具：日文到英文（auto 模式）"""
        result = vocabulary_module.translate_term_tool("キャンセル")

        assert "## ✅" in result and ("翻譯成功" in result or "Translation Successful" in result)
        assert ("**原文:**" in result or "**Original:**" in result) and "キャンセル" in result
        assert ("**翻譯:**" in result or "**Translation:**" in result) and "Cancel" in result

    def test_translate_term_tool_en_to_zh(self, vocabulary_module: VocabularyModule) -> None:
        """測試翻譯工具：英文到繁體中文"""
        result = vocabulary_module.translate_term_tool(
            "Cancel", target_locale="zh-Hant"
        )

        assert "## ✅" in result and ("翻譯成功" in result or "Translation Successful" in result)
        assert ("**原文:**" in result or "**Original:**" in result) and "Cancel" in result
        assert ("**翻譯:**" in result or "**Translation:**" in result) and "取消" in result
        assert "zh-Hant" in result

    def test_translate_term_tool_not_found(self, vocabulary_module: VocabularyModule) -> None:
        """測試翻譯工具：找不到詞彙"""
        result = vocabulary_module.translate_term_tool("NonExistentTerm")

        assert "## ⚠️ Term not found" in result
        assert "is not in Glyphs UI vocabulary" in result
        assert "not a general text translator" in result

    def test_translate_term_tool_empty_input(self, vocabulary_module: VocabularyModule) -> None:
        """測試翻譯工具：空輸入"""
        result = vocabulary_module.translate_term_tool("")

        assert "## ⚠️" in result and ("請提供要翻譯的詞彙" in result or "Please provide a term" in result)

    def test_translate_term_tool_whitespace_input(
        self, vocabulary_module: VocabularyModule
    ) -> None:
        """測試翻譯工具：只有空白的輸入"""
        result = vocabulary_module.translate_term_tool("   ")

        assert "## ⚠️" in result and ("請提供要翻譯的詞彙" in result or "Please provide a term" in result)

    def test_module_info_includes_new_tool(self, vocabulary_module: VocabularyModule) -> None:
        """測試 get_module_info() 包含新工具"""
        info = vocabulary_module.get_module_info()

        assert "tools" in info
        assert "vocab_translate_term" in info["tools"]
        assert len(info["tools"]) == 4


class TestVocabularyModuleBackwardCompatibility:
    """測試向後相容性：確保現有方法仍然正常工作"""

    @pytest.fixture
    def temp_resources(self, tmp_path: Path) -> Path:
        """建立測試用的 Glyphs resources 目錄"""
        resources_dir = tmp_path / "Resources"
        resources_dir.mkdir()

        en_dir = resources_dir / "en.lproj"
        en_dir.mkdir()
        zh_hant_dir = resources_dir / "zh-Hant.lproj"
        zh_hant_dir.mkdir()

        en_localizable = en_dir / "Localizable.strings"
        en_localizable.write_text('"Test" = "Test";\n', encoding="utf-8")

        zh_hant_localizable = zh_hant_dir / "Localizable.strings"
        zh_hant_localizable.write_text('"Test" = "測試";\n', encoding="utf-8")

        return resources_dir

    @pytest.fixture
    def vocabulary_module(self, temp_resources: Path) -> VocabularyModule:
        """建立測試用的 VocabularyModule（使用隔離的測試環境）"""
        from unittest.mock import MagicMock

        from glyphs_info_mcp.modules.glyphs_vocabulary.accessors.ui_vocabulary_native_accessor import (
            UIVocabularyNativeAccessor,
        )

        module = VocabularyModule()
        module.ui_accessor = UIVocabularyNativeAccessor(resources_path=temp_resources)

        # Mock plugins_accessor 以避免載入真實外掛詞彙
        mock_plugins_accessor = MagicMock()
        mock_plugins_accessor.get_all_terms_flat.return_value = {}
        mock_plugins_accessor.get_plugin_names.return_value = []
        module.plugins_accessor = mock_plugins_accessor

        module.initialize()
        return module

    def test_translate_term_internal_still_works(
        self, vocabulary_module: VocabularyModule
    ) -> None:
        """測試內部 translate_term 方法仍然正常工作"""
        # 這個方法供搜尋引擎使用，必須保持向後相容
        result = vocabulary_module.translate_term("測試")
        assert result == "Test"

    def test_translate_to_english_still_works(
        self, vocabulary_module: VocabularyModule
    ) -> None:
        """測試 translate_to_english 方法仍然正常工作"""
        result = vocabulary_module.translate_to_english("測試")
        assert result == "Test"

    def test_translate_to_chinese_still_works(
        self, vocabulary_module: VocabularyModule
    ) -> None:
        """測試 translate_to_chinese 方法仍然正常工作"""
        result = vocabulary_module.translate_to_chinese("Test")
        assert result == "測試"

    def test_en_to_zh_property_still_works(self, vocabulary_module: VocabularyModule) -> None:
        """測試 en_to_zh 屬性仍然正常工作"""
        mapping = vocabulary_module.en_to_zh
        assert isinstance(mapping, dict)
        assert "Test" in mapping
        assert mapping["Test"] == "測試"


class TestVocabularyModuleFuzzySearch:
    """測試模糊搜尋功能"""

    @pytest.fixture
    def temp_resources(self, tmp_path: Path) -> Path:
        """建立測試用的 Glyphs resources 目錄（包含錨點相關詞彙）"""
        resources_dir = tmp_path / "Resources"
        resources_dir.mkdir()

        en_dir = resources_dir / "en.lproj"
        en_dir.mkdir()
        zh_hant_dir = resources_dir / "zh-Hant.lproj"
        zh_hant_dir.mkdir()

        # 英文詞彙
        en_localizable = en_dir / "Localizable.strings"
        en_localizable.write_text(
            """/* Anchor related */
"Has Anchors" = "Has Anchors";
"Anchors" = "Anchors";
"Anchor to Anchor" = "Anchor to Anchor";
"Show Anchors" = "Show Anchors";
"Cancel" = "Cancel";
"Export" = "Export";
"Export All" = "Export All";
""",
            encoding="utf-8",
        )

        # 繁體中文詞彙
        zh_hant_localizable = zh_hant_dir / "Localizable.strings"
        zh_hant_localizable.write_text(
            """/* Anchor related */
"Has Anchors" = "包含錨點";
"Anchors" = "錨點";
"Anchor to Anchor" = "錨點間";
"Show Anchors" = "顯示錨點";
"Cancel" = "取消";
"Export" = "匯出";
"Export All" = "全部匯出";
""",
            encoding="utf-8",
        )

        return resources_dir

    @pytest.fixture
    def vocabulary_module(self, temp_resources: Path) -> VocabularyModule:
        """建立測試用的 VocabularyModule（使用隔離的測試環境）"""
        from unittest.mock import MagicMock

        from glyphs_info_mcp.modules.glyphs_vocabulary.accessors.ui_vocabulary_native_accessor import (
            UIVocabularyNativeAccessor,
        )

        module = VocabularyModule()
        module.ui_accessor = UIVocabularyNativeAccessor(resources_path=temp_resources)

        # Mock plugins_accessor 以避免載入真實外掛詞彙
        mock_plugins_accessor = MagicMock()
        mock_plugins_accessor.get_all_terms_flat.return_value = {}
        mock_plugins_accessor.get_plugin_names.return_value = []
        module.plugins_accessor = mock_plugins_accessor

        # Mock framework_accessor 以避免載入真實 GlyphsCore.framework 詞彙
        mock_framework_accessor = MagicMock()
        mock_framework_accessor.get_all_terms.return_value = {}
        mock_framework_accessor.supported_locales = []
        module.framework_accessor = mock_framework_accessor

        module.initialize()
        return module

    def test_fuzzy_find_term_returns_list(self, vocabulary_module: VocabularyModule) -> None:
        """測試 _fuzzy_find_term 返回列表"""
        results = vocabulary_module._fuzzy_find_term("錨點")

        assert isinstance(results, list)
        assert len(results) > 0

    def test_fuzzy_find_term_result_structure(
        self, vocabulary_module: VocabularyModule
    ) -> None:
        """測試 _fuzzy_find_term 返回結果結構"""
        results = vocabulary_module._fuzzy_find_term("Anchors")

        assert len(results) > 0
        first_result = results[0]

        # 驗證結果結構
        assert "key" in first_result
        assert "value" in first_result
        assert "locale" in first_result
        assert "score" in first_result
        assert "match_type" in first_result

    def test_fuzzy_find_term_exact_match_first(
        self, vocabulary_module: VocabularyModule
    ) -> None:
        """測試精確匹配排在第一位"""
        results = vocabulary_module._fuzzy_find_term("Anchors")

        assert len(results) > 0
        # 精確匹配應該是第一個結果
        assert results[0]["value"] == "Anchors"
        assert results[0]["match_type"] == "exact"
        assert results[0]["score"] == 1.0

    def test_fuzzy_find_term_partial_match_zh(
        self, vocabulary_module: VocabularyModule
    ) -> None:
        """測試中文部分匹配：搜尋「錨點」應找到相關詞彙"""
        results = vocabulary_module._fuzzy_find_term("錨點")

        assert len(results) >= 3  # 應至少找到 3 個相關詞彙

        # 驗證找到的詞彙
        values = [r["value"] for r in results]
        assert "錨點" in values  # 精確匹配
        assert "包含錨點" in values  # 部分匹配
        assert "錨點間" in values  # 部分匹配

    def test_fuzzy_find_term_partial_match_en(
        self, vocabulary_module: VocabularyModule
    ) -> None:
        """測試英文部分匹配：搜尋「Anchor」應找到相關詞彙"""
        results = vocabulary_module._fuzzy_find_term("Anchor")

        assert len(results) >= 3  # 應至少找到 3 個相關詞彙

        # 驗證找到的詞彙包含 Anchor 相關的
        keys = [r["key"] for r in results]
        assert "Anchors" in keys
        assert "Has Anchors" in keys
        assert "Anchor to Anchor" in keys

    def test_fuzzy_find_term_sorted_by_score(
        self, vocabulary_module: VocabularyModule
    ) -> None:
        """測試結果按相關性分數排序"""
        results = vocabulary_module._fuzzy_find_term("Anchor")

        # 確保結果按分數降序排序
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_fuzzy_find_term_max_results(self, vocabulary_module: VocabularyModule) -> None:
        """測試 max_results 參數限制結果數量"""
        results = vocabulary_module._fuzzy_find_term("Anchor", max_results=2)

        assert len(results) <= 2

    def test_translate_term_tool_fuzzy_match_zh(
        self, vocabulary_module: VocabularyModule
    ) -> None:
        """測試翻譯工具：中文模糊匹配「錨點」"""
        result = vocabulary_module.translate_term_tool("錨點")

        # 應該成功翻譯（精確匹配「錨點」→「Anchors」）
        assert "## ✅" in result and ("翻譯成功" in result or "Translation Successful" in result)
        assert "Anchors" in result

    def test_translate_term_tool_fuzzy_match_partial_zh(
        self, vocabulary_module: VocabularyModule
    ) -> None:
        """測試翻譯工具：中文模糊匹配「包含」（只是部分詞彙）"""
        result = vocabulary_module.translate_term_tool("包含")

        # 應該模糊匹配到「包含錨點」
        assert "## ✅" in result and ("翻譯成功" in result or "Translation Successful" in result)
        assert "模糊匹配" in result or "Fuzzy Match" in result
        assert "Has Anchors" in result
        assert "包含錨點" in result

    def test_translate_term_tool_shows_suggestions(
        self, vocabulary_module: VocabularyModule
    ) -> None:
        """測試翻譯工具：模糊匹配時顯示其他建議"""
        result = vocabulary_module.translate_term_tool("Anchor")

        # 模糊匹配時應顯示相關建議
        assert "## ✅" in result and ("翻譯成功" in result or "Translation Successful" in result)
        # 應該有其他相關詞彙建議
        assert "其他相關詞彙" in result or "相關" in result or "Other Related" in result or "Related" in result

    def test_translate_term_tool_zh_to_en_translation(
        self, vocabulary_module: VocabularyModule
    ) -> None:
        """測試翻譯工具：中文精確匹配應正確翻譯到英文"""
        # 輸入中文「匯出」，應翻譯為英文「Export」
        result = vocabulary_module.translate_term_tool("匯出")

        assert "## ✅" in result and ("翻譯成功" in result or "Translation Successful" in result)
        assert "Export" in result  # 應翻譯為英文，而非保持中文

    def test_translate_term_tool_zh_partial_to_en(
        self, vocabulary_module: VocabularyModule
    ) -> None:
        """測試翻譯工具：中文部分匹配應正確翻譯到英文"""
        # 輸入中文「全部」（部分匹配「全部匯出」），應翻譯為英文
        result = vocabulary_module.translate_term_tool("全部")

        assert "## ✅" in result and ("翻譯成功" in result or "Translation Successful" in result)
        assert "模糊匹配" in result or "Fuzzy Match" in result
        # 翻譯結果應該是英文
        assert "Export All" in result


class TestHubAndSpokeArchitecture:
    """測試 Hub-and-Spoke 架構（英文中介翻譯）

    這些測試驗證：
    1. 英文優先搜尋，避免非英文語系的翻譯錯誤影響結果
    2. 所有翻譯都經由英文 key 進行，確保一致性
    3. 修復 "Export" → "例如：" 類型的錯誤
    """

    @pytest.fixture
    def temp_resources_with_cs(self, tmp_path: Path) -> Path:
        """建立包含捷克語（模擬翻譯錯誤場景）的測試資料"""
        resources_dir = tmp_path / "Resources"
        resources_dir.mkdir()

        # 英文資料夾
        en_dir = resources_dir / "en.lproj"
        en_dir.mkdir()

        # 繁體中文資料夾
        zh_hant_dir = resources_dir / "zh-Hant.lproj"
        zh_hant_dir.mkdir()

        # 捷克語資料夾（模擬真實環境中的翻譯錯誤）
        cs_dir = resources_dir / "cs.lproj"
        cs_dir.mkdir()

        # 日文資料夾
        ja_dir = resources_dir / "ja.lproj"
        ja_dir.mkdir()

        # 英文詞彙（官方標準）
        en_localizable = en_dir / "Localizable.strings"
        en_localizable.write_text(
            """/* Common UI */
"Export" = "Export";
"Ex." = "Ex.";
"Cancel" = "Cancel";
""",
            encoding="utf-8",
        )

        # 繁體中文詞彙
        zh_hant_localizable = zh_hant_dir / "Localizable.strings"
        zh_hant_localizable.write_text(
            """/* Common UI */
"Export" = "匯出";
"Ex." = "例如：";
"Cancel" = "取消";
""",
            encoding="utf-8",
        )

        # 捷克語詞彙（模擬真實環境中的翻譯錯誤：Ex. 被錯誤翻譯為 Export）
        cs_localizable = cs_dir / "Localizable.strings"
        cs_localizable.write_text(
            """/* Common UI */
"Export" = "Exportovat";
"Ex." = "Export";
"Cancel" = "Zrušit";
""",
            encoding="utf-8",
        )

        # 日文詞彙
        ja_localizable = ja_dir / "Localizable.strings"
        ja_localizable.write_text(
            """/* Common UI */
"Export" = "書き出す";
"Ex." = "例";
"Cancel" = "キャンセル";
""",
            encoding="utf-8",
        )

        return resources_dir

    @pytest.fixture
    def vocabulary_module_with_cs(self, temp_resources_with_cs: Path) -> VocabularyModule:
        """建立包含捷克語的測試 VocabularyModule（使用隔離的測試環境）"""
        from unittest.mock import MagicMock

        from glyphs_info_mcp.modules.glyphs_vocabulary.accessors.ui_vocabulary_native_accessor import (
            UIVocabularyNativeAccessor,
        )

        module = VocabularyModule()
        module.ui_accessor = UIVocabularyNativeAccessor(resources_path=temp_resources_with_cs)

        # Mock plugins_accessor 以避免載入真實外掛詞彙
        mock_plugins_accessor = MagicMock()
        mock_plugins_accessor.get_all_terms_flat.return_value = {}
        mock_plugins_accessor.get_plugin_names.return_value = []
        module.plugins_accessor = mock_plugins_accessor

        module.initialize()
        return module

    def test_export_to_chinese_not_liru(
        self, vocabulary_module_with_cs: VocabularyModule
    ) -> None:
        """測試 Export 翻譯到中文：不應是「例如：」

        這是 Hub-and-Spoke 架構的核心測試案例。
        在舊架構中，由於捷克語 cs.lproj 的 "Ex." = "Export" 翻譯錯誤，
        搜尋 "Export" 會優先匹配到捷克語，然後使用錯誤的 key "Ex."
        翻譯到中文，得到 "例如：" 而非 "匯出"。
        """
        result = vocabulary_module_with_cs.translate_term_tool(
            "Export", target_locale="zh-Hant"
        )

        assert "## ✅" in result and ("翻譯成功" in result or "Translation Successful" in result)
        assert "匯出" in result
        # 確保不是錯誤的翻譯
        assert "例如" not in result

    def test_chinese_to_english_via_hub(
        self, vocabulary_module_with_cs: VocabularyModule
    ) -> None:
        """測試中文翻譯到英文：透過英文中介"""
        result = vocabulary_module_with_cs.translate_term_tool("匯出")

        assert "## ✅" in result and ("翻譯成功" in result or "Translation Successful" in result)
        assert "Export" in result

    def test_cross_language_translation_ja_to_zh(
        self, vocabulary_module_with_cs: VocabularyModule
    ) -> None:
        """測試跨語言翻譯：日文→中文（透過英文中介）"""
        result = vocabulary_module_with_cs.translate_term_tool(
            "キャンセル", target_locale="zh-Hant"
        )

        assert "## ✅" in result and ("翻譯成功" in result or "Translation Successful" in result)
        assert "取消" in result

    def test_find_english_key_prioritizes_english(
        self, vocabulary_module_with_cs: VocabularyModule
    ) -> None:
        """測試 _find_english_key 優先搜尋英文"""
        # 搜尋 "Export" 應該在英文中找到，而非捷克語
        key, locale, source = vocabulary_module_with_cs._find_english_key("Export")

        assert key == "Export"
        assert locale == "en"  # 應該從英文找到，不是捷克語
        assert source == "app"  # 來自主應用詞彙

    def test_find_english_key_with_non_english_input(
        self, vocabulary_module_with_cs: VocabularyModule
    ) -> None:
        """測試 _find_english_key 處理非英文輸入"""
        # 搜尋中文「匯出」，應該找到對應的英文 key
        key, locale, source = vocabulary_module_with_cs._find_english_key("匯出")

        assert key == "Export"
        assert locale == "zh-Hant"
        assert source == "app"  # 來自主應用詞彙

    def test_fuzzy_find_term_prioritizes_english(
        self, vocabulary_module_with_cs: VocabularyModule
    ) -> None:
        """測試 _fuzzy_find_term 優先搜尋英文"""
        results = vocabulary_module_with_cs._fuzzy_find_term("Export")

        assert len(results) > 0
        # 第一個結果應該來自英文
        assert results[0]["locale"] == "en"
        assert results[0]["value"] == "Export"

    def test_translate_term_method_uses_hub(
        self, vocabulary_module_with_cs: VocabularyModule
    ) -> None:
        """測試內部 translate_term 方法使用英文中介"""
        # 中文到英文
        result = vocabulary_module_with_cs.translate_term("匯出")
        assert result == "Export"

        # 英文到中文
        result = vocabulary_module_with_cs.translate_term("Export", target_locale="zh-Hant")
        assert result == "匯出"

        # 日文到英文
        result = vocabulary_module_with_cs.translate_term("キャンセル")
        assert result == "Cancel"


class TestBaseNibFallback:
    """測試 Base.lproj nib 回退機制

    這些測試驗證：
    1. 當英文 .strings 缺少詞彙時，會從 Base.lproj nib 檔案取得
    2. 中文「顯示」能正確翻譯為英文「View」
    3. 混合來源的翻譯正常運作
    """

    @pytest.fixture
    def temp_resources_with_nib(self, tmp_path: Path) -> Path:
        """建立包含 Base.lproj nib 模擬的測試資料"""
        resources_dir = tmp_path / "Resources"
        resources_dir.mkdir()

        # 英文資料夾（缺少 MainMenu.strings）
        en_dir = resources_dir / "en.lproj"
        en_dir.mkdir()
        en_localizable = en_dir / "Localizable.strings"
        en_localizable.write_text(
            """/* Common UI */
"Export" = "Export";
"Cancel" = "Cancel";
""",
            encoding="utf-8",
        )

        # 繁體中文資料夾（包含 MainMenu.strings）
        zh_hant_dir = resources_dir / "zh-Hant.lproj"
        zh_hant_dir.mkdir()
        zh_hant_localizable = zh_hant_dir / "Localizable.strings"
        zh_hant_localizable.write_text(
            """/* Common UI */
"Export" = "匯出";
"Cancel" = "取消";
""",
            encoding="utf-8",
        )
        # 中文有 MainMenu.strings
        zh_hant_mainmenu = zh_hant_dir / "MainMenu.strings"
        zh_hant_mainmenu.write_text(
            """/* Menu Items */
"210.title" = "顯示";
"150.title" = "顯示全部";
""",
            encoding="utf-8",
        )

        # Base.lproj（包含 nib 檔案）
        # 注意：這裡我們不模擬真實的 nib 解析，而是透過 mock

        return resources_dir

    def test_translate_term_with_nib_fallback_real_glyphs(self) -> None:
        """測試使用真實 Glyphs 3.app 的 nib 回退"""
        # 這個測試需要真實的 Glyphs 3.app
        glyphs_path = Path("/Applications/Glyphs 3.app/Contents/Resources")
        if not glyphs_path.exists():
            pytest.skip("Glyphs 3.app not installed")

        from glyphs_info_mcp.modules.glyphs_vocabulary.accessors.ui_vocabulary_native_accessor import (
            UIVocabularyNativeAccessor,
        )

        accessor = UIVocabularyNativeAccessor(glyphs_path)

        # 測試 210.title 能從 Base.lproj nib 取得英文 (View 或 Show)
        result = accessor.get_term_by_key("210.title", "en")

        assert result == "View" or result == "Show"

    def test_translate_xianshi_to_english_real_glyphs(self) -> None:
        """測試「顯示」翻譯為英文（使用真實 Glyphs）"""
        glyphs_path = Path("/Applications/Glyphs 3.app/Contents/Resources")
        if not glyphs_path.exists():
            pytest.skip("Glyphs 3.app not installed")

        from glyphs_info_mcp.modules.glyphs_vocabulary.vocabulary.vocabulary_module import (
            VocabularyModule,
        )

        module = VocabularyModule()
        module.initialize()

        if not module.is_initialized:
            pytest.skip("VocabularyModule failed to initialize")

        # 翻譯「顯示」到英文
        result = module.translate_term_tool("顯示")

        assert "## ✅" in result and ("翻譯成功" in result or "Translation Successful" in result)
        # 翻譯結果應該包含英文（View 或其他相關詞彙）
        # 不應該是中文回退
        assert "View" in result or "Show" in result

    def test_translate_chuangkou_to_english_real_glyphs(self) -> None:
        """測試「視窗」翻譯為英文（使用真實 Glyphs）"""
        glyphs_path = Path("/Applications/Glyphs 3.app/Contents/Resources")
        if not glyphs_path.exists():
            pytest.skip("Glyphs 3.app not installed")

        from glyphs_info_mcp.modules.glyphs_vocabulary.vocabulary.vocabulary_module import (
            VocabularyModule,
        )

        module = VocabularyModule()
        module.initialize()

        if not module.is_initialized:
            pytest.skip("VocabularyModule failed to initialize")

        # 翻譯「視窗」到英文
        result = module.translate_term_tool("視窗")

        assert "## ✅" in result and ("翻譯成功" in result or "Translation Successful" in result)
        # 翻譯結果應該包含英文
        assert "Window" in result


class TestChineseToEnglishTranslation:
    """測試中文詞彙翻譯到英文的 Bug 修復

    這些測試驗證：
    1. 中文詞彙能正確翻譯為英文（而非回退到中文）
    2. 使用官方 IB ID 格式的 key（如 "d99-hx-YMa.title"）跨語系查詢

    真實資料格式：
    - zh-Hant.lproj/MainMenu.strings: "d99-hx-YMa.title" = "顯示錨點";
    - Base.lproj/MainMenu.nib: "d99-hx-YMa.title" = "Show Anchors";
    - en.lproj/MainMenu.strings: 不存在（英文直接用 Base.lproj nib）
    """

    @pytest.fixture
    def temp_resources_with_ib_id_keys(self, tmp_path: Path) -> Path:
        """建立使用真實 IB ID 格式的測試資料

        模擬真實的 Glyphs .strings 和 nib 檔案結構：
        - Key 是 Interface Builder ID（如 "d99-hx-YMa.title"）
        - 英文值來自 Base.lproj/nib 檔案
        - 其他語系值來自對應的 .strings 檔案
        """
        from unittest.mock import MagicMock, patch

        resources_dir = tmp_path / "Resources"
        resources_dir.mkdir()

        # Base.lproj（英文 UI 來源）- 建立 nib 目錄結構
        base_lproj = resources_dir / "Base.lproj"
        base_lproj.mkdir()
        main_menu_nib = base_lproj / "MainMenu.nib"
        main_menu_nib.mkdir()
        # 建立模擬的 nib 檔案（實際解析由 mock 處理）
        (main_menu_nib / "keyedobjects.nib").write_bytes(b"mock binary")

        # 英文資料夾（部分詞彙有 .strings，但主要依賴 Base.lproj）
        en_dir = resources_dir / "en.lproj"
        en_dir.mkdir()
        en_localizable = en_dir / "Localizable.strings"
        en_localizable.write_text(
            """/* 部分詞彙（MainMenu 相關的不在這裡） */
"abc-12-xyz.title" = "Anchors";
""",
            encoding="utf-8",
        )

        # 繁體中文資料夾（使用 IB ID 格式的 key）
        zh_hant_dir = resources_dir / "zh-Hant.lproj"
        zh_hant_dir.mkdir()
        zh_hant_localizable = zh_hant_dir / "MainMenu.strings"
        zh_hant_localizable.write_text(
            """/* MainMenu items - 使用 IB ID 格式 */
"d99-hx-YMa.title" = "顯示錨點";
"abc-12-xyz.title" = "錨點";
"JNn-NA-XpS.title" = "顯示錨點";
""",
            encoding="utf-8",
        )

        return resources_dir

    @pytest.fixture
    def vocabulary_module_with_ib_id_keys(
        self, temp_resources_with_ib_id_keys: Path
    ) -> VocabularyModule:
        """建立使用 IB ID 格式 key 的測試 VocabularyModule

        使用 mock 來模擬 BaseNibExtractor 的 plutil 輸出，
        避免實際執行 plutil 命令。
        """
        from unittest.mock import MagicMock, patch

        from glyphs_info_mcp.modules.glyphs_vocabulary.accessors.ui_vocabulary_native_accessor import (
            UIVocabularyNativeAccessor,
        )

        # 模擬 plutil 輸出的 XML（包含 IB ID 格式的英文詞彙）
        mock_plutil_xml = """<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0">
<dict>
    <key>$objects</key>
    <array>
        <string>$null</string>
        <string>d99-hx-YMa.title</string>
        <string>Show Anchors</string>
        <string>JNn-NA-XpS.title</string>
        <string>Show Anchors</string>
    </array>
</dict>
</plist>"""

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=mock_plutil_xml, stderr=""
            )

            module = VocabularyModule()
            module.ui_accessor = UIVocabularyNativeAccessor(
                resources_path=temp_resources_with_ib_id_keys
            )
            module.initialize()

            # 預先觸發 BaseNibExtractor 的提取（在 mock 環境下）
            module.ui_accessor._base_nib_extractor.extract_all_terms()

        return module

    def test_translate_xianshi_maodian_to_english(
        self, vocabulary_module_with_ib_id_keys: VocabularyModule
    ) -> None:
        """測試「顯示錨點」翻譯為英文

        這是核心 Bug 測試。修復前的問題：
        - BaseNibExtractor 的正則只匹配純數字 key（如 "210.title"）
        - 無法匹配 IB ID 格式的 key（如 "d99-hx-YMa.title"）
        - get_term_by_key("d99-hx-YMa.title", "en") 回退到 Base.lproj 但找不到
        - 最終回退到中文

        修復後：
        - 正則表達式支援 IB ID 格式
        - Base.lproj 回退成功返回 "Show Anchors"
        """
        result = vocabulary_module_with_ib_id_keys.translate_term_tool(
            "顯示錨點", target_locale="en"
        )

        assert "## ✅" in result and ("翻譯成功" in result or "Translation Successful" in result)
        assert "Show Anchors" in result
        # 確保翻譯結果不是中文回退
        assert "**翻譯:** 顯示錨點" not in result and "**Translation:** 顯示錨點" not in result

    def test_translate_maodian_to_english(
        self, vocabulary_module_with_ib_id_keys: VocabularyModule
    ) -> None:
        """測試「錨點」翻譯為英文"""
        result = vocabulary_module_with_ib_id_keys.translate_term_tool(
            "錨點", target_locale="en"
        )

        assert "## ✅" in result and ("翻譯成功" in result or "Translation Successful" in result)
        # 應該翻譯為英文
        assert "Anchors" in result
        # 確保翻譯結果不是中文回退
        assert "**翻譯:** 錨點" not in result and "**Translation:** 錨點" not in result

    def test_fuzzy_find_term_uses_ib_id_keys(
        self, vocabulary_module_with_ib_id_keys: VocabularyModule
    ) -> None:
        """測試 _fuzzy_find_term 使用 IB ID 格式的 key"""
        results = vocabulary_module_with_ib_id_keys._fuzzy_find_term("顯示錨點")

        assert len(results) > 0
        # 所有結果的 key 都應該是 IB ID 格式
        for result in results:
            key = result["key"]
            # IB ID 格式：字母數字連字號 + .title/.label
            assert "." in key, f"Key '{key}' is not in IB ID format"
            # 應該能透過 Base.lproj 回退找到英文值
            en_value = vocabulary_module_with_ib_id_keys.ui_accessor.get_term_by_key(
                key, "en"
            )
            assert en_value is not None, f"Key '{key}' not found in English"


class TestGetUiTranslationCaseInsensitive:
    """測試 get_ui_translation 大小寫不敏感和多來源搜尋

    這些測試驗證：
    1. 大小寫不敏感匹配（修復 Categories vs CATEGORIES 問題）
    2. Framework 詞彙可被正確查詢
    3. Plugins 詞彙可被正確查詢
    """

    @pytest.fixture
    def temp_resources_with_case_variants(self, tmp_path: Path) -> Path:
        """建立包含大小寫變體的測試資料"""
        resources_dir = tmp_path / "Resources"
        resources_dir.mkdir()

        en_dir = resources_dir / "en.lproj"
        en_dir.mkdir()
        zh_hant_dir = resources_dir / "zh-Hant.lproj"
        zh_hant_dir.mkdir()

        # 英文詞彙（包含大寫詞彙）
        en_localizable = en_dir / "Localizable.strings"
        en_localizable.write_text(
            """"UPPERCASE_TERM" = "UPPERCASE_TERM";
"Lowercase term" = "Lowercase term";
"MixedCase" = "MixedCase";
"Cancel" = "Cancel";
""",
            encoding="utf-8",
        )

        # 繁體中文詞彙
        zh_hant_localizable = zh_hant_dir / "Localizable.strings"
        zh_hant_localizable.write_text(
            """"UPPERCASE_TERM" = "大寫詞彙";
"Lowercase term" = "小寫詞彙";
"MixedCase" = "混合大小寫";
"Cancel" = "取消";
""",
            encoding="utf-8",
        )

        return resources_dir

    @pytest.fixture
    def vocabulary_module_with_case_variants(
        self, temp_resources_with_case_variants: Path
    ) -> VocabularyModule:
        """建立測試用的 VocabularyModule（包含大小寫變體）"""
        from unittest.mock import MagicMock

        from glyphs_info_mcp.modules.glyphs_vocabulary.accessors.ui_vocabulary_native_accessor import (
            UIVocabularyNativeAccessor,
        )

        module = VocabularyModule()
        module.ui_accessor = UIVocabularyNativeAccessor(
            resources_path=temp_resources_with_case_variants
        )

        # Mock framework_accessor（包含大寫詞彙）
        mock_framework_accessor = MagicMock()
        mock_framework_accessor.get_all_terms.side_effect = lambda locale: {
            "CATEGORIES": "CATEGORIES" if locale == "en" else "類型",
            "LANGUAGES": "LANGUAGES" if locale == "en" else "語系",
        }
        mock_framework_accessor.supported_locales = ["en", "zh-Hant"]
        module.framework_accessor = mock_framework_accessor

        # Mock plugins_accessor
        mock_plugins_accessor = MagicMock()
        mock_plugins_accessor.get_all_terms_flat.return_value = {}
        mock_plugins_accessor.get_plugin_names.return_value = []
        module.plugins_accessor = mock_plugins_accessor

        module.initialize()
        return module

    def test_get_ui_translation_case_insensitive_uppercase(
        self, vocabulary_module_with_case_variants: VocabularyModule
    ) -> None:
        """測試大小寫不敏感：查詢小寫可匹配大寫詞彙"""
        result = vocabulary_module_with_case_variants.get_ui_translation(
            "uppercase_term", target_locales="zh-Hant"
        )

        assert ("⚠️ 未找到詞彙" not in result) and ("⚠️ Term not found" not in result)
        assert "大寫詞彙" in result

    def test_get_ui_translation_case_insensitive_lowercase(
        self, vocabulary_module_with_case_variants: VocabularyModule
    ) -> None:
        """測試大小寫不敏感：查詢大寫可匹配小寫詞彙"""
        result = vocabulary_module_with_case_variants.get_ui_translation(
            "LOWERCASE TERM", target_locales="zh-Hant"
        )

        assert ("⚠️ 未找到詞彙" not in result) and ("⚠️ Term not found" not in result)
        assert "小寫詞彙" in result

    def test_get_ui_translation_case_insensitive_mixed(
        self, vocabulary_module_with_case_variants: VocabularyModule
    ) -> None:
        """測試大小寫不敏感：查詢混合大小寫"""
        result = vocabulary_module_with_case_variants.get_ui_translation(
            "mixedcase", target_locales="zh-Hant"
        )

        assert ("⚠️ 未找到詞彙" not in result) and ("⚠️ Term not found" not in result)
        assert "混合大小寫" in result

    def test_get_ui_translation_searches_framework(
        self, vocabulary_module_with_case_variants: VocabularyModule
    ) -> None:
        """測試搜尋範圍：可找到 Framework 詞彙"""
        result = vocabulary_module_with_case_variants.get_ui_translation(
            "CATEGORIES", target_locales="zh-Hant"
        )

        assert ("⚠️ 未找到詞彙" not in result) and ("⚠️ Term not found" not in result)
        assert "類型" in result
        assert "GlyphsCore.framework" in result

    def test_get_ui_translation_searches_framework_case_insensitive(
        self, vocabulary_module_with_case_variants: VocabularyModule
    ) -> None:
        """測試搜尋範圍：Framework 詞彙也支援大小寫不敏感"""
        result = vocabulary_module_with_case_variants.get_ui_translation(
            "Categories", target_locales="zh-Hant"
        )

        assert ("⚠️ 未找到詞彙" not in result) and ("⚠️ Term not found" not in result)
        assert "類型" in result

    def test_get_ui_translation_searches_framework_languages(
        self, vocabulary_module_with_case_variants: VocabularyModule
    ) -> None:
        """測試搜尋範圍：可找到 Framework 的 LANGUAGES 詞彙"""
        result = vocabulary_module_with_case_variants.get_ui_translation(
            "Languages", target_locales="zh-Hant"
        )

        assert ("⚠️ 未找到詞彙" not in result) and ("⚠️ Term not found" not in result)
        assert "語系" in result
