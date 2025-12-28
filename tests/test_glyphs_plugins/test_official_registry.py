"""
測試 OfficialRegistry - 官方 packages.plist 解析器

測試與實作 API 同步版本
"""

import json
import plistlib
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from glyphs_info_mcp.modules.glyphs_plugins.accessors.official_registry import OfficialRegistry


class TestOfficialRegistry:
    """測試 OfficialRegistry 類別"""

    @pytest.fixture
    def mock_packages_data(self) -> list:
        """建立模擬的外掛資料（統一格式，用於快取驗證）"""
        return [
            {
                "name": "ShowCrosshair",
                "title": "ShowCrosshair",
                "url": "https://github.com/mekkablue/ShowCrosshair",
                "description": "Shows a crosshair at the center of your viewport",
                "owner": "mekkablue",
                "repo_name": "ShowCrosshair",
            },
            {
                "name": "MakeCorner",
                "title": "MakeCorner",
                "url": "https://github.com/mekkablue/MakeCorner",
                "description": "Quickly turn selected nodes into corners",
                "owner": "mekkablue",
                "repo_name": "MakeCorner",
            },
            {
                "name": "Insert-Glyph-to-Background",
                "title": "Insert-Glyph-to-Background",
                "url": "https://github.com/guidoferreyra/Insert-Glyph-to-Background",
                "description": "Insert any glyph to the background layer",
                "owner": "guidoferreyra",
                "repo_name": "Insert-Glyph-to-Background",
            },
        ]

    @pytest.fixture
    def mock_plist_data(self) -> dict:
        """建立模擬的官方 plist 資料結構（用於 subprocess mock）"""
        return {
            "packages": {
                "plugins": [
                    {
                        "path": "ShowCrosshair",
                        "titles": {"en": "ShowCrosshair"},
                        "url": "https://github.com/mekkablue/ShowCrosshair",
                        "descriptions": {"en": "Shows a crosshair at the center of your viewport"},
                    },
                    {
                        "path": "MakeCorner",
                        "titles": {"en": "MakeCorner"},
                        "url": "https://github.com/mekkablue/MakeCorner",
                        "descriptions": {"en": "Quickly turn selected nodes into corners"},
                    },
                    {
                        "path": "Insert-Glyph-to-Background",
                        "titles": {"en": "Insert-Glyph-to-Background"},
                        "url": "https://github.com/guidoferreyra/Insert-Glyph-to-Background",
                        "descriptions": {"en": "Insert any glyph to the background layer"},
                    },
                ]
            }
        }

    @pytest.fixture
    def mock_xml_plist_bytes(self, mock_plist_data: dict) -> bytes:
        """建立模擬的 XML plist 資料（供 subprocess mock 返回）"""
        return plistlib.dumps(mock_plist_data)

    @pytest.fixture
    def cache_dir(self, tmp_path: Path) -> Path:
        """建立臨時快取目錄"""
        cache = tmp_path / "cache"
        cache.mkdir()
        return cache

    @pytest.fixture
    def registry(self, cache_dir: Path) -> OfficialRegistry:
        """建立 OfficialRegistry 實例"""
        return OfficialRegistry(cache_dir=cache_dir)

    # ===== 測試：基本初始化 =====
    def test_initialization(self, registry: OfficialRegistry) -> None:
        """測試：正確初始化 OfficialRegistry"""
        # 驗證類別常數
        assert (
            OfficialRegistry.OFFICIAL_PACKAGES_URL
            == "https://raw.githubusercontent.com/schriftgestalt/glyphs-packages/glyphs3/packages.plist"
        )
        assert OfficialRegistry.CACHE_TTL_HOURS == 24
        # 驗證實例屬性
        assert registry.cache_path.name == "packages_cache.json"

    # ===== 測試：下載和解析 packages.plist =====
    @patch("glyphs_info_mcp.modules.glyphs_plugins.accessors.official_registry.subprocess.run")
    @patch("glyphs_info_mcp.modules.glyphs_plugins.accessors.official_registry.httpx.get")
    def test_fetch_packages_from_network(
        self,
        mock_get: Mock,
        mock_subprocess: Mock,
        registry: OfficialRegistry,
        mock_xml_plist_bytes: bytes,
    ) -> None:
        """測試：從網路下載並解析 packages.plist"""
        # 模擬 HTTP 回應
        mock_response = Mock()
        mock_response.content = b"ascii plist content"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # 模擬 subprocess（plutil 轉換）
        mock_result = Mock()
        mock_result.stdout = mock_xml_plist_bytes
        mock_subprocess.return_value = mock_result

        # 執行
        packages = registry.fetch_packages()

        # 驗證
        assert len(packages) == 3
        assert packages[0]["name"] == "ShowCrosshair"
        assert "crosshair" in packages[0]["description"].lower()
        mock_get.assert_called_once()

    # ===== 測試：快取機制 =====
    def test_cache_is_created_after_fetch(
        self, registry: OfficialRegistry, mock_xml_plist_bytes: bytes
    ) -> None:
        """測試：fetch 後建立快取檔案"""
        with patch("glyphs_info_mcp.modules.glyphs_plugins.accessors.official_registry.httpx.get") as mock_get, \
             patch("glyphs_info_mcp.modules.glyphs_plugins.accessors.official_registry.subprocess.run") as mock_subprocess:
            # 模擬 HTTP 回應
            mock_response = Mock()
            mock_response.content = b"ascii plist content"
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            # 模擬 subprocess（plutil 轉換）
            mock_result = Mock()
            mock_result.stdout = mock_xml_plist_bytes
            mock_subprocess.return_value = mock_result

            registry.fetch_packages()

            # 驗證快取檔案存在
            assert registry.cache_path.exists()

    def test_use_cache_if_valid(
        self, registry: OfficialRegistry, mock_packages_data: list[dict[str, str]]
    ) -> None:
        """測試：快取有效時使用快取，不發起網路請求"""
        # 建立有效的快取（使用正確的快取格式）
        cache_data = {
            "cache_version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "packages": mock_packages_data,
        }
        registry.cache_path.write_text(json.dumps(cache_data, ensure_ascii=False))

        with patch("glyphs_info_mcp.modules.glyphs_plugins.accessors.official_registry.httpx.get") as mock_get:
            packages = registry.fetch_packages()

            # 驗證：使用快取，未發起網路請求
            mock_get.assert_not_called()
            assert len(packages) == 3

    def test_refresh_cache_if_expired(
        self,
        registry: OfficialRegistry,
        mock_packages_data: list[dict[str, str]],
        mock_xml_plist_bytes: bytes,
    ) -> None:
        """測試：快取過期時重新下載"""
        # 建立過期的快取（25 小時前）
        expired_time = datetime.now() - timedelta(hours=25)
        cache_data = {
            "cache_version": "2.0",
            "timestamp": expired_time.isoformat(),
            "packages": mock_packages_data,
        }
        registry.cache_path.write_text(json.dumps(cache_data, ensure_ascii=False))

        with patch("glyphs_info_mcp.modules.glyphs_plugins.accessors.official_registry.httpx.get") as mock_get, \
             patch("glyphs_info_mcp.modules.glyphs_plugins.accessors.official_registry.subprocess.run") as mock_subprocess:
            # 模擬 HTTP 回應
            mock_response = Mock()
            mock_response.content = b"ascii plist content"
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            # 模擬 subprocess（plutil 轉換）
            mock_result = Mock()
            mock_result.stdout = mock_xml_plist_bytes
            mock_subprocess.return_value = mock_result

            packages = registry.fetch_packages()

            # 驗證：快取過期，發起網路請求
            mock_get.assert_called_once()
            assert len(packages) == 3

    # ===== 測試：搜尋功能 =====
    def test_search_by_name(self, registry: OfficialRegistry, mock_packages_data: list) -> None:
        """測試：按名稱搜尋外掛"""
        # 建立快取
        cache_data = {
            "cache_version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "packages": mock_packages_data,
        }
        registry.cache_path.write_text(json.dumps(cache_data, ensure_ascii=False))

        # 執行搜尋（使用 core_search 方法）
        results = registry.core_search("crosshair")

        # 驗證（core_search 返回 title 欄位）
        assert len(results) == 1
        assert results[0]["title"] == "ShowCrosshair"

    def test_search_by_description(
        self, registry: OfficialRegistry, mock_packages_data: list[dict[str, str]]
    ) -> None:
        """測試：按描述搜尋外掛"""
        cache_data = {
            "cache_version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "packages": mock_packages_data,
        }
        registry.cache_path.write_text(json.dumps(cache_data, ensure_ascii=False))

        # 執行搜尋
        results = registry.core_search("background")

        # 驗證
        assert len(results) == 1
        assert results[0]["title"] == "Insert-Glyph-to-Background"

    def test_search_case_insensitive(
        self, registry: OfficialRegistry, mock_packages_data: list[dict[str, str]]
    ) -> None:
        """測試：搜尋不區分大小寫"""
        cache_data = {
            "cache_version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "packages": mock_packages_data,
        }
        registry.cache_path.write_text(json.dumps(cache_data, ensure_ascii=False))

        # 執行搜尋（大小寫混合）
        results = registry.core_search("CROSSHAIR")

        # 驗證
        assert len(results) == 1
        assert results[0]["title"] == "ShowCrosshair"

    def test_search_returns_empty_if_no_match(
        self, registry: OfficialRegistry, mock_packages_data: list[dict[str, str]]
    ) -> None:
        """測試：搜尋無結果時返回空列表"""
        cache_data = {
            "cache_version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "packages": mock_packages_data,
        }
        registry.cache_path.write_text(json.dumps(cache_data, ensure_ascii=False))

        # 執行搜尋
        results = registry.core_search("nonexistent")

        # 驗證
        assert results == []

    # ===== 測試：錯誤處理 =====
    def test_corrupted_cache_triggers_refetch(
        self, registry: OfficialRegistry, mock_xml_plist_bytes: bytes
    ) -> None:
        """測試：快取檔案損壞時觸發重新下載"""
        # 建立損壞的快取檔案（無效 JSON）
        registry.cache_path.write_text("{ invalid json content }")

        with patch("glyphs_info_mcp.modules.glyphs_plugins.accessors.official_registry.httpx.get") as mock_get, \
             patch("glyphs_info_mcp.modules.glyphs_plugins.accessors.official_registry.subprocess.run") as mock_subprocess:
            # 模擬 HTTP 回應
            mock_response = Mock()
            mock_response.content = b"ascii plist content"
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            # 模擬 subprocess（plutil 轉換）
            mock_result = Mock()
            mock_result.stdout = mock_xml_plist_bytes
            mock_subprocess.return_value = mock_result

            # 執行
            packages = registry.fetch_packages()

            # 驗證：快取損壞，發起網路請求
            mock_get.assert_called_once()
            assert len(packages) == 3

    @patch("glyphs_info_mcp.modules.glyphs_plugins.accessors.official_registry.httpx.get")
    def test_handle_network_error(self, mock_get: Mock, registry: OfficialRegistry) -> None:
        """測試：處理網路錯誤"""
        mock_get.side_effect = Exception("Network error")

        with pytest.raises(Exception, match="Network error"):
            registry.fetch_packages()

    @patch("glyphs_info_mcp.modules.glyphs_plugins.accessors.official_registry.subprocess.run")
    @patch("glyphs_info_mcp.modules.glyphs_plugins.accessors.official_registry.httpx.get")
    def test_handle_invalid_plist_format(
        self, mock_get: Mock, mock_subprocess: Mock, registry: OfficialRegistry
    ) -> None:
        """測試：處理無效的 plist 格式（拋出例外）"""
        # 模擬 HTTP 回應
        mock_response = Mock()
        mock_response.content = b"invalid plist data"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # plutil 轉換失敗
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "plutil")

        # 實作會重新拋出 CalledProcessError 例外
        with pytest.raises(subprocess.CalledProcessError):
            registry.fetch_packages()

    @patch("glyphs_info_mcp.modules.glyphs_plugins.accessors.official_registry.subprocess.run")
    @patch("glyphs_info_mcp.modules.glyphs_plugins.accessors.official_registry.httpx.get")
    def test_title_field_priority(
        self, mock_get: Mock, mock_subprocess: Mock, registry: OfficialRegistry
    ) -> None:
        """測試：title 欄位處理邏輯（titles.en 優先於 path）"""
        # 建立測試資料：使用官方 plist 格式
        plist_data = {
            "packages": {
                "plugins": [
                    {
                        "path": "PluginA.glyphsPlugin",
                        "titles": {"en": "Plugin A Title"},
                        "url": "https://example.com/a",
                        "descriptions": {"en": "Has both path and title"},
                    },
                    {
                        "path": "PluginB.glyphsPlugin",
                        # 無 titles 欄位
                        "url": "https://example.com/b",
                        "descriptions": {"en": "Has only path"},
                    },
                ]
            }
        }

        # 模擬 HTTP 回應
        mock_response = Mock()
        mock_response.content = b"ascii plist content"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # 模擬 subprocess（plutil 轉換）
        mock_result = Mock()
        mock_result.stdout = plistlib.dumps(plist_data)
        mock_subprocess.return_value = mock_result

        packages = registry.fetch_packages()

        # 驗證：有 titles.en 時使用 title
        assert len(packages) == 2
        assert packages[0]["name"] == "PluginA.glyphsPlugin"
        assert packages[0]["title"] == "Plugin A Title"

        # 驗證：沒有 titles 時，title 為空字串（實作行為）
        assert packages[1]["name"] == "PluginB.glyphsPlugin"
        assert packages[1]["title"] == ""
