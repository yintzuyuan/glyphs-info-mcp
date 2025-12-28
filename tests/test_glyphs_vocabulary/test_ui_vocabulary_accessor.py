"""
測試 UIVocabularyNativeAccessor - Glyphs UI 詞彙原生存取器

TDD 紅燈階段：先撰寫測試，預期失敗
"""

from pathlib import Path
from unittest.mock import PropertyMock, patch

import pytest

from glyphs_info_mcp.modules.glyphs_vocabulary.accessors.ui_vocabulary_native_accessor import (
    UIVocabularyNativeAccessor,
)


class TestStringsFileParser:
    """測試 .strings 檔案解析器"""

    @pytest.fixture
    def temp_strings_files(self, tmp_path: Path) -> Path:
        """建立測試用的 .strings 檔案"""
        test_dir = tmp_path / "test_resources"
        test_dir.mkdir()

        # 建立英文資料夾
        en_dir = test_dir / "en.lproj"
        en_dir.mkdir()

        # 建立繁體中文資料夾
        zh_hant_dir = test_dir / "zh-Hant.lproj"
        zh_hant_dir.mkdir()

        # 建立英文 Localizable.strings
        en_localizable = en_dir / "Localizable.strings"
        en_localizable.write_text(
            """/* UI Elements */
"Add Glyph" = "Add Glyph";
"Has Anchors" = "Has Anchors";
"Set Anchors" = "Set Anchors";

/* Menu Items */
"File" = "File";
"Edit" = "Edit";
""",
            encoding="utf-8",
        )

        # 建立繁體中文 Localizable.strings
        zh_hant_localizable = zh_hant_dir / "Localizable.strings"
        zh_hant_localizable.write_text(
            """/* UI Elements */
"Add Glyph" = "新增字符";
"Has Anchors" = "包含錨點";
"Set Anchors" = "自動設定錨點";

/* Menu Items */
"File" = "檔案";
"Edit" = "編輯";
""",
            encoding="utf-8",
        )

        # 建立另一個 .strings 檔案
        en_fontview = en_dir / "FontView.strings"
        en_fontview.write_text(
            """"Glyph Info" = "Glyph Info";
"Font Info" = "Font Info";
""",
            encoding="utf-8",
        )

        zh_hant_fontview = zh_hant_dir / "FontView.strings"
        zh_hant_fontview.write_text(
            """"Glyph Info" = "字符資訊";
"Font Info" = "字型資訊";
""",
            encoding="utf-8",
        )

        return test_dir

    def test_parse_single_strings_file(self, temp_strings_files: Path) -> None:
        """測試解析單一 .strings 檔案"""
        accessor = UIVocabularyNativeAccessor(resources_path=temp_strings_files)

        # 解析英文檔案
        en_file = temp_strings_files / "en.lproj" / "Localizable.strings"
        result = accessor._parse_strings_file(en_file)

        assert isinstance(result, dict)
        assert len(result) == 5
        assert result["Add Glyph"] == "Add Glyph"
        assert result["Has Anchors"] == "Has Anchors"
        assert result["File"] == "File"

    def test_parse_strings_file_with_comments(self, temp_strings_files: Path) -> None:
        """測試解析包含註解的 .strings 檔案"""
        accessor = UIVocabularyNativeAccessor(resources_path=temp_strings_files)

        en_file = temp_strings_files / "en.lproj" / "Localizable.strings"
        result = accessor._parse_strings_file(en_file)

        # 確保註解被正確忽略
        assert "/* UI Elements */" not in result
        assert "/* Menu Items */" not in result

    def test_parse_strings_file_chinese(self, temp_strings_files: Path) -> None:
        """測試解析繁體中文 .strings 檔案"""
        accessor = UIVocabularyNativeAccessor(resources_path=temp_strings_files)

        zh_file = temp_strings_files / "zh-Hant.lproj" / "Localizable.strings"
        result = accessor._parse_strings_file(zh_file)

        assert len(result) == 5
        assert result["Add Glyph"] == "新增字符"
        assert result["Has Anchors"] == "包含錨點"
        assert result["File"] == "檔案"

    def test_parse_nonexistent_file(self, temp_strings_files: Path) -> None:
        """測試解析不存在的檔案"""
        accessor = UIVocabularyNativeAccessor(resources_path=temp_strings_files)

        result = accessor._parse_strings_file(Path("/nonexistent/file.strings"))
        assert result == {}


class TestUIVocabularyNativeAccessor:
    """測試 UIVocabularyNativeAccessor 基本功能"""

    @pytest.fixture
    def temp_resources(self, tmp_path: Path) -> Path:
        """建立完整的測試資源目錄結構"""
        test_dir = tmp_path / "test_resources"
        test_dir.mkdir()

        # 建立英文資料夾
        en_dir = test_dir / "en.lproj"
        en_dir.mkdir()

        # 建立繁體中文資料夾
        zh_hant_dir = test_dir / "zh-Hant.lproj"
        zh_hant_dir.mkdir()

        # 建立日文資料夾
        ja_dir = test_dir / "ja.lproj"
        ja_dir.mkdir()

        # 建立英文詞彙檔案
        (en_dir / "Localizable.strings").write_text(
            """"Add Glyph" = "Add Glyph";
"Delete" = "Delete";
""",
            encoding="utf-8",
        )

        (en_dir / "FontView.strings").write_text(
            """"Glyph Info" = "Glyph Info";
""",
            encoding="utf-8",
        )

        # 建立繁體中文詞彙檔案
        (zh_hant_dir / "Localizable.strings").write_text(
            """"Add Glyph" = "新增字符";
"Delete" = "刪除";
""",
            encoding="utf-8",
        )

        (zh_hant_dir / "FontView.strings").write_text(
            """"Glyph Info" = "字符資訊";
""",
            encoding="utf-8",
        )

        # 建立日文詞彙檔案
        (ja_dir / "Localizable.strings").write_text(
            """"Add Glyph" = "グリフを追加";
"Delete" = "削除";
""",
            encoding="utf-8",
        )

        return test_dir

    def test_accessor_initialization(self, temp_resources: Path) -> None:
        """測試 Accessor 初始化"""
        accessor = UIVocabularyNativeAccessor(resources_path=temp_resources)

        assert accessor.resources_path == temp_resources
        assert "en" in accessor.supported_locales
        assert "zh-Hant" in accessor.supported_locales
        assert "ja" in accessor.supported_locales

    def test_get_all_terms_english(self, temp_resources: Path) -> None:
        """測試取得所有英文詞彙"""
        accessor = UIVocabularyNativeAccessor(resources_path=temp_resources)

        result = accessor.get_all_terms(locale="en")

        assert isinstance(result, dict)
        assert len(result) == 3
        assert result["Add Glyph"] == "Add Glyph"
        assert result["Delete"] == "Delete"
        assert result["Glyph Info"] == "Glyph Info"

    def test_get_all_terms_chinese(self, temp_resources: Path) -> None:
        """測試取得所有繁體中文詞彙"""
        accessor = UIVocabularyNativeAccessor(resources_path=temp_resources)

        result = accessor.get_all_terms(locale="zh-Hant")

        assert len(result) == 3
        assert result["Add Glyph"] == "新增字符"
        assert result["Delete"] == "刪除"
        assert result["Glyph Info"] == "字符資訊"

    def test_get_all_terms_japanese(self, temp_resources: Path) -> None:
        """測試取得所有日文詞彙"""
        accessor = UIVocabularyNativeAccessor(resources_path=temp_resources)

        result = accessor.get_all_terms(locale="ja")

        assert len(result) == 2
        assert result["Add Glyph"] == "グリフを追加"
        assert result["Delete"] == "削除"

    def test_get_translation_single_locale(self, temp_resources: Path) -> None:
        """測試取得單一語系翻譯"""
        accessor = UIVocabularyNativeAccessor(resources_path=temp_resources)

        result = accessor.get_translation(
            term="Add Glyph", source_locale="en", target_locale="zh-Hant"
        )

        assert result is not None
        assert result["key"] == "Add Glyph"
        assert result["source"] == "Add Glyph"
        assert result["target"] == "新增字符"
        assert result["source_locale"] == "en"
        assert result["target_locale"] == "zh-Hant"

    def test_get_translation_multiple_locales(self, temp_resources: Path) -> None:
        """測試取得多語系翻譯"""
        accessor = UIVocabularyNativeAccessor(resources_path=temp_resources)

        result = accessor.get_translation(
            term="Add Glyph",
            source_locale="en",
            target_locales=["zh-Hant", "ja"],
        )

        assert result is not None
        assert result["key"] == "Add Glyph"
        assert result["source"] == "Add Glyph"
        assert "translations" in result
        assert len(result["translations"]) == 2
        assert result["translations"]["zh-Hant"] == "新增字符"
        assert result["translations"]["ja"] == "グリフを追加"

    def test_get_translation_by_chinese_term(self, temp_resources: Path) -> None:
        """測試使用中文詞彙查詢翻譯"""
        accessor = UIVocabularyNativeAccessor(resources_path=temp_resources)

        result = accessor.get_translation(
            term="新增字符", source_locale="zh-Hant", target_locale="en"
        )

        assert result is not None
        assert result["key"] == "Add Glyph"
        assert result["source"] == "新增字符"
        assert result["target"] == "Add Glyph"

    def test_get_translation_term_not_found(self, temp_resources: Path) -> None:
        """測試查詢不存在的詞彙"""
        accessor = UIVocabularyNativeAccessor(resources_path=temp_resources)

        result = accessor.get_translation(
            term="Nonexistent Term", source_locale="en", target_locale="zh-Hant"
        )

        assert result is None

    def test_get_term_by_key(self, temp_resources: Path) -> None:
        """測試透過 key 精確查詢"""
        accessor = UIVocabularyNativeAccessor(resources_path=temp_resources)

        result = accessor.get_term_by_key(key="Add Glyph", locale="zh-Hant")

        assert result == "新增字符"

    def test_get_term_by_key_not_found(self, temp_resources: Path) -> None:
        """測試查詢不存在的 key"""
        accessor = UIVocabularyNativeAccessor(resources_path=temp_resources)

        result = accessor.get_term_by_key(key="Nonexistent", locale="en")

        assert result is None

    def test_list_available_locales(self, temp_resources: Path) -> None:
        """測試列出可用語系"""
        accessor = UIVocabularyNativeAccessor(resources_path=temp_resources)

        locales = accessor.list_available_locales()

        assert isinstance(locales, list)
        assert len(locales) == 3
        assert "en" in locales
        assert "zh-Hant" in locales
        assert "ja" in locales


class TestNibTermsIntegration:
    """Test NIB terms integration in get_all_terms()

    Issue #94: Vocabulary search tools should include NIB terms.
    When locale is 'en', get_all_terms() should merge NIB terms.
    """

    @pytest.fixture
    def temp_resources_with_nib_mock(self, tmp_path: Path) -> Path:
        """Create test resources with mock NIB extractor behavior"""
        test_dir = tmp_path / "test_resources"
        test_dir.mkdir()

        # Create English folder with .strings files
        en_dir = test_dir / "en.lproj"
        en_dir.mkdir()

        (en_dir / "Localizable.strings").write_text(
            """"Cancel" = "Cancel";
"OK" = "OK";
""",
            encoding="utf-8",
        )

        # Create zh-Hant folder
        zh_hant_dir = test_dir / "zh-Hant.lproj"
        zh_hant_dir.mkdir()

        (zh_hant_dir / "Localizable.strings").write_text(
            """"Cancel" = "取消";
"OK" = "好";
""",
            encoding="utf-8",
        )

        return test_dir

    def test_get_all_terms_includes_nib_terms_for_english(
        self, temp_resources_with_nib_mock: Path
    ) -> None:
        """When locale is 'en', get_all_terms() should include NIB terms"""
        accessor = UIVocabularyNativeAccessor(
            resources_path=temp_resources_with_nib_mock
        )

        # Mock NIB extractor to return known terms
        mock_nib_terms = {
            "210.title": "View",
            "d99-hx-YMa.title": "Show Anchors",
        }

        # Use PropertyMock for the is_available property
        with patch.object(
            type(accessor._base_nib_extractor),
            "is_available",
            new_callable=PropertyMock,
            return_value=True,
        ), patch.object(
            accessor._base_nib_extractor,
            "extract_all_terms",
            return_value=mock_nib_terms,
        ):
            result = accessor.get_all_terms("en")

        # Should include .strings terms
        assert "Cancel" in result
        assert result["Cancel"] == "Cancel"

        # Should include NIB terms
        assert "210.title" in result
        assert result["210.title"] == "View"
        assert "d99-hx-YMa.title" in result
        assert result["d99-hx-YMa.title"] == "Show Anchors"

    def test_get_all_terms_strings_takes_priority_over_nib(
        self, temp_resources_with_nib_mock: Path
    ) -> None:
        """When both .strings and NIB have the same key, .strings wins"""
        accessor = UIVocabularyNativeAccessor(
            resources_path=temp_resources_with_nib_mock
        )

        # Mock NIB extractor with a conflicting key
        mock_nib_terms = {
            "Cancel": "Cancel from NIB",  # Conflicts with .strings
            "210.title": "View",
        }

        with patch.object(
            type(accessor._base_nib_extractor),
            "is_available",
            new_callable=PropertyMock,
            return_value=True,
        ), patch.object(
            accessor._base_nib_extractor,
            "extract_all_terms",
            return_value=mock_nib_terms,
        ):
            result = accessor.get_all_terms("en")

        # .strings should take priority
        assert result["Cancel"] == "Cancel"
        # NIB-only term should be included
        assert result["210.title"] == "View"

    def test_get_all_terms_excludes_nib_for_non_english(
        self, temp_resources_with_nib_mock: Path
    ) -> None:
        """Non-English locales should NOT include NIB terms"""
        accessor = UIVocabularyNativeAccessor(
            resources_path=temp_resources_with_nib_mock
        )

        # Mock NIB extractor
        mock_nib_terms = {"210.title": "View"}

        with patch.object(
            type(accessor._base_nib_extractor),
            "is_available",
            new_callable=PropertyMock,
            return_value=True,
        ), patch.object(
            accessor._base_nib_extractor,
            "extract_all_terms",
            return_value=mock_nib_terms,
        ):
            result = accessor.get_all_terms("zh-Hant")

        # Should include .strings terms
        assert "Cancel" in result
        assert result["Cancel"] == "取消"

        # Should NOT include NIB terms (NIB only has English)
        assert "210.title" not in result

    def test_search_term_finds_nib_vocabulary(
        self, temp_resources_with_nib_mock: Path
    ) -> None:
        """search_term() should find terms from NIB files"""
        accessor = UIVocabularyNativeAccessor(
            resources_path=temp_resources_with_nib_mock
        )

        mock_nib_terms = {
            "210.title": "View",
            "d99-hx-YMa.title": "Show Anchors",
        }

        with patch.object(
            type(accessor._base_nib_extractor),
            "is_available",
            new_callable=PropertyMock,
            return_value=True,
        ), patch.object(
            accessor._base_nib_extractor,
            "extract_all_terms",
            return_value=mock_nib_terms,
        ):
            # Search for "View" which only exists in NIB
            results = accessor.search_term("View", source_locale="en")

        assert len(results) > 0
        assert any(r["value"] == "View" for r in results)

    def test_search_term_finds_anchors_from_nib(
        self, temp_resources_with_nib_mock: Path
    ) -> None:
        """search_term() should find 'Show Anchors' from NIB"""
        accessor = UIVocabularyNativeAccessor(
            resources_path=temp_resources_with_nib_mock
        )

        mock_nib_terms = {
            "d99-hx-YMa.title": "Show Anchors",
        }

        with patch.object(
            type(accessor._base_nib_extractor),
            "is_available",
            new_callable=PropertyMock,
            return_value=True,
        ), patch.object(
            accessor._base_nib_extractor,
            "extract_all_terms",
            return_value=mock_nib_terms,
        ):
            results = accessor.search_term("Anchors", source_locale="en")

        assert len(results) > 0
        assert any("Show Anchors" in r["value"] for r in results)


class TestNibTermsIntegrationRealGlyphs:
    """Integration tests with real Glyphs 3.app

    These tests verify NIB term integration works with actual Glyphs data.
    Skipped if Glyphs 3.app is not installed.
    """

    @pytest.fixture
    def glyphs_accessor(self) -> UIVocabularyNativeAccessor | None:
        """Create accessor with real Glyphs path if available"""
        glyphs_path = Path("/Applications/Glyphs 3.app/Contents/Resources")
        if not glyphs_path.exists():
            return None
        return UIVocabularyNativeAccessor(resources_path=glyphs_path)

    def test_get_all_terms_includes_view_menu_item(
        self, glyphs_accessor: UIVocabularyNativeAccessor | None
    ) -> None:
        """get_all_terms('en') should include 'View' menu from MainMenu.nib"""
        if glyphs_accessor is None:
            pytest.skip("Glyphs 3.app not installed")

        result = glyphs_accessor.get_all_terms("en")

        # "210.title" is the View menu item in MainMenu.nib
        assert "210.title" in result
        assert result["210.title"] == "View"

    def test_search_term_finds_view_menu(
        self, glyphs_accessor: UIVocabularyNativeAccessor | None
    ) -> None:
        """search_term() should find 'View' from MainMenu.nib"""
        if glyphs_accessor is None:
            pytest.skip("Glyphs 3.app not installed")

        results = glyphs_accessor.search_term("View", source_locale="en")

        # Should find the View menu item from NIB
        assert len(results) > 0
        assert any(r["value"] == "View" for r in results)

    def test_search_term_finds_show_anchors_menu(
        self, glyphs_accessor: UIVocabularyNativeAccessor | None
    ) -> None:
        """search_term() should find 'Show Anchors' menu item from NIB"""
        if glyphs_accessor is None:
            pytest.skip("Glyphs 3.app not installed")

        results = glyphs_accessor.search_term("Show Anchors", source_locale="en")

        # Should find Show Anchors from NIB (IB ID format key like "d99-hx-YMa.title")
        assert len(results) > 0
        assert any("Show Anchors" in r["value"] for r in results)


class TestUIVocabularySearch:
    """測試 UIVocabularyNativeAccessor 搜尋功能"""

    @pytest.fixture
    def temp_resources(self, tmp_path: Path) -> Path:
        """建立測試資源"""
        test_dir = tmp_path / "test_resources"
        test_dir.mkdir()

        en_dir = test_dir / "en.lproj"
        en_dir.mkdir()

        zh_hant_dir = test_dir / "zh-Hant.lproj"
        zh_hant_dir.mkdir()

        (en_dir / "Localizable.strings").write_text(
            """"Add Glyph" = "Add Glyph";
"Add Anchor" = "Add Anchor";
"Delete Glyph" = "Delete Glyph";
"Glyph Info" = "Glyph Info";
"Font Info" = "Font Info";
""",
            encoding="utf-8",
        )

        (zh_hant_dir / "Localizable.strings").write_text(
            """"Add Glyph" = "新增字符";
"Add Anchor" = "新增錨點";
"Delete Glyph" = "刪除字符";
"Glyph Info" = "字符資訊";
"Font Info" = "字型資訊";
""",
            encoding="utf-8",
        )

        return test_dir

    def test_search_term_exact_match(self, temp_resources: Path) -> None:
        """測試精確匹配搜尋"""
        accessor = UIVocabularyNativeAccessor(resources_path=temp_resources)

        results = accessor.search_term(term="Add Glyph", source_locale="en")

        assert len(results) > 0
        assert any(r["key"] == "Add Glyph" for r in results)

    def test_search_term_partial_match(self, temp_resources: Path) -> None:
        """測試部分匹配搜尋"""
        accessor = UIVocabularyNativeAccessor(resources_path=temp_resources)

        results = accessor.search_term(term="Glyph", source_locale="en")

        assert len(results) >= 3
        keys = [r["key"] for r in results]
        assert "Add Glyph" in keys
        assert "Delete Glyph" in keys
        assert "Glyph Info" in keys

    def test_search_term_case_insensitive(self, temp_resources: Path) -> None:
        """測試不區分大小寫搜尋"""
        accessor = UIVocabularyNativeAccessor(resources_path=temp_resources)

        results = accessor.search_term(term="add glyph", source_locale="en")

        assert len(results) > 0
        assert any(r["key"] == "Add Glyph" for r in results)

    def test_search_term_chinese(self, temp_resources: Path) -> None:
        """測試中文搜尋"""
        accessor = UIVocabularyNativeAccessor(resources_path=temp_resources)

        results = accessor.search_term(term="字符", source_locale="zh-Hant")

        assert len(results) >= 2
        values = [r["value"] for r in results]
        assert "新增字符" in values
        assert "刪除字符" in values
        assert "字符資訊" in values

    def test_search_term_no_results(self, temp_resources: Path) -> None:
        """測試無結果的搜尋"""
        accessor = UIVocabularyNativeAccessor(resources_path=temp_resources)

        results = accessor.search_term(term="Nonexistent Term", source_locale="en")

        assert len(results) == 0
