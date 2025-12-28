# encoding: utf-8
"""
測試本機外掛匹配功能 - Phase 3

測試範圍：
- 本機外掛路徑偵測
- 官方清單與本機外掛的匹配策略
- 安裝狀態標記
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch


class TestLocalPluginMatcher:
    """測試本機外掛匹配器"""

    def test_get_local_plugins_directory(self) -> None:
        """測試取得本機外掛目錄路徑"""
        from glyphs_info_mcp.modules.glyphs_plugins.accessors.local_matcher import LocalPluginMatcher

        matcher = LocalPluginMatcher()
        plugins_dir = matcher.get_local_plugins_directory()

        # 應該返回標準的 Glyphs 3 外掛目錄
        assert isinstance(plugins_dir, Path)
        assert "Application Support" in str(plugins_dir)
        assert "Glyphs 3" in str(plugins_dir)
        assert "Plugins" in str(plugins_dir)

    def test_scan_local_plugins_empty_directory(self, tmp_path: Path) -> None:
        """測試掃描空的外掛目錄"""
        from glyphs_info_mcp.modules.glyphs_plugins.accessors.local_matcher import LocalPluginMatcher

        matcher = LocalPluginMatcher(plugins_dir=tmp_path)
        local_plugins = matcher.scan_local_plugins()

        assert isinstance(local_plugins, list)
        assert len(local_plugins) == 0

    def test_scan_local_plugins_with_plugins(self, tmp_path: Path) -> None:
        """測試掃描包含外掛的目錄"""
        from glyphs_info_mcp.modules.glyphs_plugins.accessors.local_matcher import LocalPluginMatcher

        # 建立模擬的外掛目錄
        (tmp_path / "ShowCrosshair.glyphsReporter").mkdir()
        (tmp_path / "Risorizer.glyphsFilter").mkdir()
        (tmp_path / "not-a-plugin.txt").touch()  # 非外掛檔案

        matcher = LocalPluginMatcher(plugins_dir=tmp_path)
        local_plugins = matcher.scan_local_plugins()

        # 應該只找到 2 個外掛
        assert len(local_plugins) == 2
        assert any(p["name"] == "ShowCrosshair.glyphsReporter" for p in local_plugins)
        assert any(p["name"] == "Risorizer.glyphsFilter" for p in local_plugins)

    def test_match_by_exact_name(self) -> None:
        """測試精確名稱匹配"""
        from glyphs_info_mcp.modules.glyphs_plugins.accessors.local_matcher import LocalPluginMatcher

        matcher = LocalPluginMatcher()

        official_plugin = {
            "name": "ShowCrosshair.glyphsReporter",
            "title": "ShowCrosshair",
            "url": "https://github.com/mekkablue/ShowCrosshair"
        }

        local_plugin = {
            "name": "ShowCrosshair.glyphsReporter",
            "path": "/path/to/ShowCrosshair.glyphsReporter"
        }

        # 應該完全匹配
        assert matcher.is_match(official_plugin, local_plugin) is True

    def test_match_by_repo_name(self) -> None:
        """測試儲存庫名稱匹配"""
        from glyphs_info_mcp.modules.glyphs_plugins.accessors.local_matcher import LocalPluginMatcher

        matcher = LocalPluginMatcher()

        official_plugin = {
            "name": "ShowStems.glyphsReporter",
            "title": "Show Stems",
            "url": "https://github.com/Mark2Mark/Show-Stems",
            "owner": "Mark2Mark",
            "repo_name": "Show-Stems"
        }

        # 本機外掛目錄名稱可能是 repo_name
        local_plugin = {
            "name": "Show-Stems.glyphsReporter",  # 目錄名與 repo_name 相符
            "path": "/path/to/Show-Stems"
        }

        # 應該透過 repo_name 匹配
        assert matcher.is_match(official_plugin, local_plugin) is True

    def test_no_match_different_plugins(self) -> None:
        """測試不同外掛不匹配"""
        from glyphs_info_mcp.modules.glyphs_plugins.accessors.local_matcher import LocalPluginMatcher

        matcher = LocalPluginMatcher()

        official_plugin = {
            "name": "ShowCrosshair.glyphsReporter",
            "title": "ShowCrosshair",
            "url": "https://github.com/mekkablue/ShowCrosshair"
        }

        local_plugin = {
            "name": "Risorizer.glyphsFilter",
            "path": "/path/to/Risorizer.glyphsFilter"
        }

        # 完全不同的外掛
        assert matcher.is_match(official_plugin, local_plugin) is False

    def test_mark_installed_status(self) -> None:
        """測試標記安裝狀態"""
        from glyphs_info_mcp.modules.glyphs_plugins.accessors.local_matcher import LocalPluginMatcher

        matcher = LocalPluginMatcher()

        official_plugins = [
            {
                "name": "ShowCrosshair.glyphsReporter",
                "title": "ShowCrosshair",
                "url": "https://github.com/mekkablue/ShowCrosshair"
            },
            {
                "name": "Risorizer.glyphsFilter",
                "title": "Risorizer",
                "url": "https://github.com/mekkablue/Risorizer"
            }
        ]

        local_plugins = [
            {
                "name": "ShowCrosshair.glyphsReporter",
                "path": "/path/to/ShowCrosshair.glyphsReporter"
            }
        ]

        # 標記安裝狀態
        marked_plugins = matcher.mark_installed_status(official_plugins, local_plugins)

        # ShowCrosshair 應該標記為已安裝
        assert marked_plugins[0]["installed"] is True
        assert marked_plugins[0]["local_path"] == "/path/to/ShowCrosshair.glyphsReporter"

        # Risorizer 應該標記為未安裝
        assert marked_plugins[1]["installed"] is False
        assert "local_path" not in marked_plugins[1]

    def test_integration_with_official_registry(self, tmp_path: Path) -> None:
        """測試與 OfficialRegistry 整合"""
        from glyphs_info_mcp.modules.glyphs_plugins.accessors.local_matcher import LocalPluginMatcher
        from glyphs_info_mcp.modules.glyphs_plugins.accessors.official_registry import OfficialRegistry

        # 建立模擬的本機外掛
        (tmp_path / "ShowCrosshair.glyphsReporter").mkdir()

        matcher = LocalPluginMatcher(plugins_dir=tmp_path)
        registry = OfficialRegistry()

        # Mock official registry data
        mock_packages = [
            {
                "name": "ShowCrosshair.glyphsReporter",
                "title": "ShowCrosshair",
                "url": "https://github.com/mekkablue/ShowCrosshair",
                "owner": "mekkablue",
                "repo_name": "ShowCrosshair"
            }
        ]

        # 掃描本機外掛
        local_plugins = matcher.scan_local_plugins()

        # 標記安裝狀態
        marked_packages = matcher.mark_installed_status(mock_packages, local_plugins)

        # ShowCrosshair 應該標記為已安裝
        assert marked_packages[0]["installed"] is True


class TestPluginExtensionDetection:
    """測試外掛副檔名偵測"""

    def test_detect_reporter_plugin(self, tmp_path: Path) -> None:
        """測試偵測 Reporter 外掛"""
        from glyphs_info_mcp.modules.glyphs_plugins.accessors.local_matcher import LocalPluginMatcher

        (tmp_path / "ShowCrosshair.glyphsReporter").mkdir()

        matcher = LocalPluginMatcher(plugins_dir=tmp_path)
        local_plugins = matcher.scan_local_plugins()

        assert local_plugins[0]["type"] == "reporter"

    def test_detect_filter_plugin(self, tmp_path: Path) -> None:
        """測試偵測 Filter 外掛"""
        from glyphs_info_mcp.modules.glyphs_plugins.accessors.local_matcher import LocalPluginMatcher

        (tmp_path / "Risorizer.glyphsFilter").mkdir()

        matcher = LocalPluginMatcher(plugins_dir=tmp_path)
        local_plugins = matcher.scan_local_plugins()

        assert local_plugins[0]["type"] == "filter"

    def test_detect_tool_plugin(self, tmp_path: Path) -> None:
        """測試偵測 Tool 外掛"""
        from glyphs_info_mcp.modules.glyphs_plugins.accessors.local_matcher import LocalPluginMatcher

        (tmp_path / "SelectTool.glyphsTool").mkdir()

        matcher = LocalPluginMatcher(plugins_dir=tmp_path)
        local_plugins = matcher.scan_local_plugins()

        assert local_plugins[0]["type"] == "tool"

    def test_detect_palette_plugin(self, tmp_path: Path) -> None:
        """測試偵測 Palette 外掛"""
        from glyphs_info_mcp.modules.glyphs_plugins.accessors.local_matcher import LocalPluginMatcher

        (tmp_path / "GlyphsPalette.glyphsPalette").mkdir()

        matcher = LocalPluginMatcher(plugins_dir=tmp_path)
        local_plugins = matcher.scan_local_plugins()

        assert local_plugins[0]["type"] == "palette"

    def test_detect_generic_plugin(self, tmp_path: Path) -> None:
        """測試偵測通用外掛"""
        from glyphs_info_mcp.modules.glyphs_plugins.accessors.local_matcher import LocalPluginMatcher

        (tmp_path / "CustomPlugin.glyphsPlugin").mkdir()

        matcher = LocalPluginMatcher(plugins_dir=tmp_path)
        local_plugins = matcher.scan_local_plugins()

        assert local_plugins[0]["type"] == "plugin"
