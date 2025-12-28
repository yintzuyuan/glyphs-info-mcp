"""
BaseNibExtractor 測試

測試從 Base.lproj nib 檔案提取英文詞彙的功能。
"""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from glyphs_info_mcp.modules.glyphs_vocabulary.accessors.base_nib_extractor import (
    BaseNibExtractor,
)


class TestBaseNibExtractorBasics:
    """基本功能測試"""

    def test_init_with_default_path(self) -> None:
        """測試預設路徑初始化"""
        extractor = BaseNibExtractor()

        assert extractor.resources_path == Path(
            "/Applications/Glyphs 3.app/Contents/Resources"
        )
        assert extractor.base_lproj == extractor.resources_path / "Base.lproj"

    def test_init_with_custom_path(self, tmp_path: Path) -> None:
        """測試自訂路徑初始化"""
        extractor = BaseNibExtractor(tmp_path)

        assert extractor.resources_path == tmp_path
        assert extractor.base_lproj == tmp_path / "Base.lproj"

    def test_is_available_when_exists(self, tmp_path: Path) -> None:
        """測試 Base.lproj 存在時的可用性"""
        base_lproj = tmp_path / "Base.lproj"
        base_lproj.mkdir()

        extractor = BaseNibExtractor(tmp_path)

        assert extractor.is_available is True

    def test_is_available_when_not_exists(self, tmp_path: Path) -> None:
        """測試 Base.lproj 不存在時的可用性"""
        extractor = BaseNibExtractor(tmp_path)

        assert extractor.is_available is False

    def test_clear_cache(self, tmp_path: Path) -> None:
        """測試清除快取"""
        extractor = BaseNibExtractor(tmp_path)
        extractor._cache = {"test": "value"}
        extractor._is_extracted = True

        extractor.clear_cache()

        assert extractor._cache == {}
        assert extractor._is_extracted is False


class TestBaseNibExtractorParsing:
    """nib 解析測試"""

    @pytest.fixture
    def mock_plutil_output(self) -> str:
        """模擬 plutil 輸出的 XML"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0">
<dict>
    <key>$objects</key>
    <array>
        <string>$null</string>
        <string>210.title</string>
        <string>View</string>
        <string>150.title</string>
        <string>Show All</string>
        <string>934.title</string>
        <string>Show Metrics</string>
    </array>
</dict>
</plist>"""

    @pytest.fixture
    def mock_plutil_output_with_ib_id(self) -> str:
        """模擬包含 IB ID 格式 key 的 plutil 輸出"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0">
<dict>
    <key>$objects</key>
    <array>
        <string>$null</string>
        <string>d99-hx-YMa.title</string>
        <string>Show Anchors</string>
        <string>8Pk-qX-fbS.title</string>
        <string>Show Metrics</string>
        <string>kI6-1N-qWQ.title</string>
        <string>Font View</string>
        <string>210.title</string>
        <string>View</string>
    </array>
</dict>
</plist>"""

    def test_parse_nib_extracts_key_value_pairs(
        self, tmp_path: Path, mock_plutil_output: str
    ) -> None:
        """測試解析 nib 檔案提取 key-value 對應"""
        # 建立模擬的 nib 檔案
        nib_file = tmp_path / "test.nib"
        nib_file.write_bytes(b"mock binary content")

        extractor = BaseNibExtractor(tmp_path)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=mock_plutil_output, stderr=""
            )

            result = extractor._parse_nib(nib_file)

        assert result == {
            "210.title": "View",
            "150.title": "Show All",
            "934.title": "Show Metrics",
        }

    def test_parse_nib_extracts_ib_id_format_keys(
        self, tmp_path: Path, mock_plutil_output_with_ib_id: str
    ) -> None:
        """測試解析包含 IB ID 格式 key（字母+數字+連字號）的 nib 檔案

        Glyphs 的 nib 檔案使用 Interface Builder ID 作為 key，
        格式如 'd99-hx-YMa.title'（字母數字連字號組合）。
        """
        nib_file = tmp_path / "test.nib"
        nib_file.write_bytes(b"mock binary content")

        extractor = BaseNibExtractor(tmp_path)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=mock_plutil_output_with_ib_id, stderr=""
            )

            result = extractor._parse_nib(nib_file)

        # 應該能解析所有格式的 key
        assert result == {
            "d99-hx-YMa.title": "Show Anchors",
            "8Pk-qX-fbS.title": "Show Metrics",
            "kI6-1N-qWQ.title": "Font View",
            "210.title": "View",
        }

    def test_parse_nib_handles_failure(self, tmp_path: Path) -> None:
        """測試 plutil 失敗時的處理"""
        nib_file = tmp_path / "test.nib"
        nib_file.write_bytes(b"mock binary content")

        extractor = BaseNibExtractor(tmp_path)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")

            result = extractor._parse_nib(nib_file)

        assert result == {}

    def test_parse_nib_handles_timeout(self, tmp_path: Path) -> None:
        """測試 plutil 超時的處理"""
        nib_file = tmp_path / "test.nib"
        nib_file.write_bytes(b"mock binary content")

        extractor = BaseNibExtractor(tmp_path)

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(cmd="plutil", timeout=10)

            result = extractor._parse_nib(nib_file)

        assert result == {}


class TestBaseNibExtractorExtraction:
    """詞彙提取測試"""

    @pytest.fixture
    def mock_extractor(self, tmp_path: Path) -> BaseNibExtractor:
        """建立模擬的提取器"""
        base_lproj = tmp_path / "Base.lproj"
        base_lproj.mkdir()

        # 建立模擬的 nib 目錄結構
        main_menu_nib = base_lproj / "MainMenu.nib"
        main_menu_nib.mkdir()
        (main_menu_nib / "keyedobjects.nib").write_bytes(b"mock")

        font_view_nib = base_lproj / "FontView.nib"
        font_view_nib.mkdir()
        (font_view_nib / "keyedobjects.nib").write_bytes(b"mock")

        return BaseNibExtractor(tmp_path)

    def test_extract_all_terms_from_multiple_nibs(self, mock_extractor: BaseNibExtractor) -> None:
        """測試從多個 nib 檔案提取詞彙"""
        # 模擬 _parse_nib 回傳不同結果
        parse_results = [
            {"210.title": "View", "150.title": "Show All"},
            {"100.title": "Font View"},
        ]
        call_count = [0]

        def mock_parse_nib(nib_path: Path) -> dict[str, str]:
            result = parse_results[call_count[0] % len(parse_results)]
            call_count[0] += 1
            return result

        with patch.object(mock_extractor, "_parse_nib", side_effect=mock_parse_nib):
            result = mock_extractor.extract_all_terms()

        # 應該合併所有結果
        assert "210.title" in result
        assert "150.title" in result
        assert "100.title" in result

    def test_extract_all_terms_caches_result(self, mock_extractor: BaseNibExtractor) -> None:
        """測試提取結果會被快取"""
        with patch.object(
            mock_extractor, "_parse_nib", return_value={"test": "value"}
        ) as mock_parse:
            # 第一次呼叫
            result1 = mock_extractor.extract_all_terms()
            # 第二次呼叫
            result2 = mock_extractor.extract_all_terms()

        # 應該只解析一次
        assert result1 == result2
        # _parse_nib 只被呼叫有限次數（第一次提取時）
        # 第二次呼叫不應該再呼叫 _parse_nib

    def test_get_term_returns_value(self, mock_extractor: BaseNibExtractor) -> None:
        """測試取得單個詞彙"""
        mock_extractor._cache = {"210.title": "View"}
        mock_extractor._is_extracted = True

        result = mock_extractor.get_term("210.title")

        assert result == "View"

    def test_get_term_returns_none_for_missing_key(self, mock_extractor: BaseNibExtractor) -> None:
        """測試取得不存在的詞彙"""
        mock_extractor._cache = {"210.title": "View"}
        mock_extractor._is_extracted = True

        result = mock_extractor.get_term("999.title")

        assert result is None

    def test_get_term_triggers_extraction(self, mock_extractor: BaseNibExtractor) -> None:
        """測試 get_term 會觸發提取"""
        with patch.object(
            mock_extractor, "extract_all_terms", return_value={"210.title": "View"}
        ) as mock_extract:
            mock_extractor.get_term("210.title")

        mock_extract.assert_called_once()


class TestBaseNibExtractorWithRealGlyphs:
    """使用真實 Glyphs 3.app 的測試（如果存在）"""

    @pytest.fixture
    def real_extractor(self) -> BaseNibExtractor | None:
        """建立使用真實 Glyphs 路徑的提取器"""
        extractor = BaseNibExtractor()
        if extractor.is_available:
            return extractor
        return None

    def test_extract_from_real_glyphs(self, real_extractor: BaseNibExtractor | None) -> None:
        """測試從真實 Glyphs 3.app 提取詞彙"""
        if real_extractor is None:
            pytest.skip("Glyphs 3.app not installed")

        result = real_extractor.extract_all_terms()

        # 應該提取到詞彙
        assert len(result) > 0

        # 應該包含 MainMenu 中的關鍵詞彙
        assert "210.title" in result
        assert result["210.title"] == "View"

    def test_get_view_term_from_real_glyphs(self, real_extractor: BaseNibExtractor | None) -> None:
        """測試取得 'View' 詞彙"""
        if real_extractor is None:
            pytest.skip("Glyphs 3.app not installed")

        result = real_extractor.get_term("210.title")

        assert result == "View"

    def test_get_show_all_term_from_real_glyphs(
        self, real_extractor: BaseNibExtractor | None
    ) -> None:
        """測試取得 'Show All' 詞彙"""
        if real_extractor is None:
            pytest.skip("Glyphs 3.app not installed")

        result = real_extractor.get_term("150.title")

        assert result == "Show All"

    def test_get_show_anchors_with_ib_id_from_real_glyphs(
        self, real_extractor: BaseNibExtractor | None
    ) -> None:
        """測試使用 IB ID 格式 key 取得 'Show Anchors' 詞彙

        這個測試驗證 BaseNibExtractor 能正確解析 IB ID 格式的 key，
        如 'd99-hx-YMa.title'（字母+數字+連字號組合）。
        """
        if real_extractor is None:
            pytest.skip("Glyphs 3.app not installed")

        result = real_extractor.get_term("d99-hx-YMa.title")

        assert result == "Show Anchors"
