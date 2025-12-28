"""
Tests for FrameworkVocabularyAccessor

測試 GlyphsCore.framework 詞彙存取器的功能，包括：
- .strings 檔案解析
- 多語系詞彙讀取
- 搜尋功能
- Custom Parameters 詞彙驗證

注意：此模組需要本地安裝 Glyphs 3 app 才能執行測試。
"""

import pytest
from pathlib import Path

from glyphs_info_mcp.modules.glyphs_vocabulary.accessors.framework_vocabulary_accessor import (
    FrameworkVocabularyAccessor,
)


# 整個模組需要 Glyphs 3 app
pytestmark = pytest.mark.requires_glyphs_app


class TestFrameworkVocabularyAccessor:
    """FrameworkVocabularyAccessor 測試類別"""

    @pytest.fixture
    def accessor(self) -> FrameworkVocabularyAccessor:
        """建立測試用的 accessor"""
        return FrameworkVocabularyAccessor()

    def test_framework_path_exists(self, accessor: FrameworkVocabularyAccessor) -> None:
        """測試 GlyphsCore.framework 路徑存在"""
        assert accessor.framework_path.exists()

    def test_discover_locales(self, accessor: FrameworkVocabularyAccessor) -> None:
        """測試語系發現功能"""
        locales = accessor.supported_locales

        # 應該找到多個語系
        assert len(locales) > 0

        # 應該包含主要語系
        assert "en" in locales
        assert "zh-Hant" in locales
        assert "ja" in locales

    def test_discover_strings_files(self, accessor: FrameworkVocabularyAccessor) -> None:
        """測試 .strings 檔案發現"""
        files = accessor.get_strings_files()

        # 應該找到多個檔案
        assert len(files) > 0

        # 應該包含重要檔案
        assert "Localizable.strings" in files
        assert "customParameterDescriptions.strings" in files
        assert "FeatureNames.strings" in files

    def test_get_all_terms_english(self, accessor: FrameworkVocabularyAccessor) -> None:
        """測試取得英文詞彙"""
        terms = accessor.get_all_terms("en")

        # 應該有大量詞彙
        assert len(terms) > 100

    def test_get_all_terms_chinese(self, accessor: FrameworkVocabularyAccessor) -> None:
        """測試取得繁體中文詞彙"""
        terms = accessor.get_all_terms("zh-Hant")

        # 應該有大量詞彙
        assert len(terms) > 100

    def test_get_terms_from_file(self, accessor: FrameworkVocabularyAccessor) -> None:
        """測試從特定檔案取得詞彙"""
        terms = accessor.get_terms_from_file("FeatureNames.strings", "en")

        # 應該有詞彙
        assert len(terms) > 0

        # OpenType Feature 名稱應該存在
        # 例如 "smcp" -> "Small Capitals"
        assert any("smcp" in key.lower() for key in terms.keys())

    def test_custom_parameters_terms(self, accessor: FrameworkVocabularyAccessor) -> None:
        """測試 Custom Parameters 詞彙"""
        terms = accessor.get_terms_from_file(
            "customParameterDescriptions.strings", "en"
        )

        # 應該有大量詞彙（這是最大的檔案）
        assert len(terms) > 50

    def test_search_term_english(self, accessor: FrameworkVocabularyAccessor) -> None:
        """測試英文搜尋"""
        results = accessor.search_term("ascender", locale="en")

        # 應該找到結果
        assert len(results) > 0

        # 結果應該包含必要資訊
        first_result = results[0]
        assert "key" in first_result
        assert "value" in first_result

    def test_search_term_chinese(self, accessor: FrameworkVocabularyAccessor) -> None:
        """測試繁體中文搜尋"""
        results = accessor.search_term("上升", locale="zh-Hant")

        # 應該找到結果（可能是「上升部」等）
        # 即使找不到也不應該報錯
        assert isinstance(results, list)

    def test_get_statistics(self, accessor: FrameworkVocabularyAccessor) -> None:
        """測試詞彙統計"""
        stats = accessor.get_statistics()

        # 應該有統計資訊
        assert "total_terms" in stats
        assert "files" in stats
        assert "locale_count" in stats

        # 統計數字應該大於 0
        assert stats["total_terms"] > 0
        assert stats["locale_count"] > 0

    def test_nonexistent_locale(self, accessor: FrameworkVocabularyAccessor) -> None:
        """測試不存在的語系"""
        terms = accessor.get_all_terms("xx-XX")

        # 應該返回空字典
        assert terms == {}

    def test_nonexistent_file(self, accessor: FrameworkVocabularyAccessor) -> None:
        """測試不存在的檔案"""
        terms = accessor.get_terms_from_file("NonExistent.strings", "en")

        # 應該返回空字典
        assert terms == {}

    def test_cache_functionality(self, accessor: FrameworkVocabularyAccessor) -> None:
        """測試快取功能"""
        # 第一次取得
        terms1 = accessor.get_all_terms("en")

        # 第二次取得（應該從快取）
        terms2 = accessor.get_all_terms("en")

        # 應該是同一個物件（快取）
        assert terms1 is terms2


class TestGlyphsCoreSpecificTerms:
    """專門測試 GlyphsCore.framework 特定詞彙"""

    @pytest.fixture
    def accessor(self) -> FrameworkVocabularyAccessor:
        """建立測試用的 accessor"""
        return FrameworkVocabularyAccessor()

    def test_panose_terms(self, accessor: FrameworkVocabularyAccessor) -> None:
        """測試 PANOSE 詞彙"""
        terms = accessor.get_terms_from_file("Panose.strings", "en")

        # 應該有 PANOSE 相關詞彙
        assert len(terms) > 0

    def test_language_tags_terms(self, accessor: FrameworkVocabularyAccessor) -> None:
        """測試語言標籤詞彙"""
        terms = accessor.get_terms_from_file("LanguageTags.strings", "en")

        # 應該有語言標籤詞彙
        assert len(terms) > 0

    def test_categories_terms(self, accessor: FrameworkVocabularyAccessor) -> None:
        """測試字元分類詞彙"""
        terms = accessor.get_terms_from_file("categories.strings", "en")

        # 應該有分類詞彙
        assert len(terms) > 0

    def test_scripts_terms(self, accessor: FrameworkVocabularyAccessor) -> None:
        """測試書寫系統詞彙"""
        terms = accessor.get_terms_from_file("Scripts.strings", "en")

        # 應該有書寫系統詞彙
        assert len(terms) > 0

    def test_inspector_terms(self, accessor: FrameworkVocabularyAccessor) -> None:
        """測試 Inspector 相關詞彙"""
        # 測試 Component Inspector
        terms = accessor.get_terms_from_file(
            "InspectorViewGSComponent.strings", "en"
        )

        # 應該有詞彙
        assert len(terms) > 0

    def test_feature_names_translation(self, accessor: FrameworkVocabularyAccessor) -> None:
        """測試 OpenType Feature 名稱翻譯"""
        en_terms = accessor.get_terms_from_file("FeatureNames.strings", "en")
        zh_terms = accessor.get_terms_from_file("FeatureNames.strings", "zh-Hant")

        # 英文和繁中應該都有詞彙
        assert len(en_terms) > 0
        assert len(zh_terms) > 0
