# encoding: utf-8
"""
測試 GlyphsPluginsModule - Phase 2 SearchEngine 整合

測試範圍：
- 模組初始化
- 搜尋工具註冊
- 基本搜尋功能
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from glyphs_info_mcp.modules.glyphs_plugins.accessors.official_registry import OfficialRegistry


class TestGlyphsPluginsModule:
    """測試 GlyphsPluginsModule 基本功能"""

    def test_module_initialization(self) -> None:
        """測試模組初始化"""
        from glyphs_info_mcp.modules.glyphs_plugins.glyphs_plugins_module import GlyphsPluginsModule

        module = GlyphsPluginsModule()
        assert module.name == "glyphs-plugins"
        assert not module.is_initialized

        # 初始化模組
        result = module.initialize()
        assert result is True
        assert module.is_initialized

    def test_module_has_official_registry(self) -> None:
        """測試模組包含 OfficialRegistry"""
        from glyphs_info_mcp.modules.glyphs_plugins.glyphs_plugins_module import GlyphsPluginsModule

        module = GlyphsPluginsModule()
        module.initialize()

        assert hasattr(module, 'official_registry')
        assert module.official_registry is not None

    def test_get_tools_returns_search_tool(self) -> None:
        """測試 get_tools() 返回搜尋工具"""
        from glyphs_info_mcp.modules.glyphs_plugins.glyphs_plugins_module import GlyphsPluginsModule

        module = GlyphsPluginsModule()
        module.initialize()

        tools = module.get_tools()
        assert isinstance(tools, dict)
        assert 'plugins_search_official' in tools
        assert callable(tools['plugins_search_official'])

    def test_search_tool_basic_functionality(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """測試搜尋工具基本功能"""
        from glyphs_info_mcp.modules.glyphs_plugins.glyphs_plugins_module import GlyphsPluginsModule

        # Mock OfficialRegistry.core_search
        mock_results = [
            {
                "title": "ShowCrosshair",
                "description": "Shows a crosshair",
                "url": "https://github.com/mekkablue/ShowCrosshair",
                "owner": "mekkablue",
                "repo_name": "ShowCrosshair",
                "score": 1.0,
                "type": "plugin",
                "source": "official_registry"
            }
        ]

        def mock_fetch_packages(self: OfficialRegistry) -> list[dict[str, str]]:
            return [{
                "name": "ShowCrosshair.glyphsReporter",
                "title": "ShowCrosshair",
                "url": "https://github.com/mekkablue/ShowCrosshair",
                "description": "Shows a crosshair",
                "owner": "mekkablue",
                "repo_name": "ShowCrosshair"
            }]

        from glyphs_info_mcp.modules.glyphs_plugins.accessors import official_registry
        monkeypatch.setattr(
            official_registry.OfficialRegistry,
            'fetch_packages',
            mock_fetch_packages
        )

        module = GlyphsPluginsModule()
        module.initialize()

        tools = module.get_tools()
        search_tool = tools['plugins_search_official']

        result = search_tool(query="crosshair")
        assert isinstance(result, str)
        assert "ShowCrosshair" in result

    def test_search_tool_shows_all_results(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """測試搜尋工具顯示所有結果（精簡格式）"""
        from glyphs_info_mcp.modules.glyphs_plugins.glyphs_plugins_module import GlyphsPluginsModule

        # Mock 多個結果
        def mock_fetch_packages(self: OfficialRegistry) -> list[dict[str, str]]:
            return [
                {"name": f"Plugin{i}", "title": f"Plugin{i}",
                 "url": f"https://github.com/test/plugin{i}",
                 "description": "Test plugin",
                 "owner": "test", "repo_name": f"plugin{i}"}
                for i in range(20)
            ]

        from glyphs_info_mcp.modules.glyphs_plugins.accessors import official_registry
        monkeypatch.setattr(
            official_registry.OfficialRegistry,
            'fetch_packages',
            mock_fetch_packages
        )

        module = GlyphsPluginsModule()
        module.initialize()

        tools = module.get_tools()
        search_tool = tools['plugins_search_official']

        # 測試顯示所有結果（無數量限制，使用精簡格式）
        result = search_tool(query="plugin")
        assert isinstance(result, str)
        # 應該使用精簡表格格式
        assert "| #" in result or "Found" in result

    def test_module_not_initialized_error(self) -> None:
        """測試模組未初始化時的錯誤處理"""
        from glyphs_info_mcp.modules.glyphs_plugins.glyphs_plugins_module import GlyphsPluginsModule

        module = GlyphsPluginsModule()
        # 不初始化模組

        tools = module.get_tools()
        search_tool = tools['plugins_search_official']

        result = search_tool(query="test")
        assert "not initialized" in result.lower() or "未初始化" in result

    def test_get_module_info(self) -> None:
        """測試 get_module_info() 方法"""
        from glyphs_info_mcp.modules.glyphs_plugins.glyphs_plugins_module import GlyphsPluginsModule

        module = GlyphsPluginsModule()
        module.initialize()

        info = module.get_module_info()
        assert isinstance(info, dict)
        assert 'name' in info
        assert 'tools' in info
        assert info['name'] == 'glyphs-plugins'
        assert 'plugins_search_official' in info['tools']

    def test_search_tool_with_author_filter(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """測試搜尋工具支援作者篩選 (Phase 4)"""
        from glyphs_info_mcp.modules.glyphs_plugins.glyphs_plugins_module import GlyphsPluginsModule

        # Mock 多個作者的外掛
        def mock_fetch_packages(self: OfficialRegistry) -> list[dict[str, str]]:
            return [
                {
                    "name": "ShowCrosshair.glyphsReporter",
                    "title": "ShowCrosshair",
                    "url": "https://github.com/mekkablue/ShowCrosshair",
                    "description": "Shows a crosshair",
                    "owner": "mekkablue",
                    "repo_name": "ShowCrosshair"
                },
                {
                    "name": "Risorizer.glyphsFilter",
                    "title": "Risorizer",
                    "url": "https://github.com/mekkablue/Risorizer",
                    "description": "Resizes glyphs",
                    "owner": "mekkablue",
                    "repo_name": "Risorizer"
                },
                {
                    "name": "ShowStems.glyphsReporter",
                    "title": "Show Stems",
                    "url": "https://github.com/Mark2Mark/Show-Stems",
                    "description": "Shows stems",
                    "owner": "Mark2Mark",
                    "repo_name": "Show-Stems"
                }
            ]

        from glyphs_info_mcp.modules.glyphs_plugins.accessors import official_registry
        monkeypatch.setattr(
            official_registry.OfficialRegistry,
            'fetch_packages',
            mock_fetch_packages
        )

        module = GlyphsPluginsModule()
        module.initialize()

        tools = module.get_tools()
        search_tool = tools['plugins_search_official']

        # 測試作者篩選：只返回 mekkablue 的外掛
        result = search_tool(query="show", filter_by_author="mekkablue")
        assert isinstance(result, str)
        assert "ShowCrosshair" in result
        # Mark2Mark 的外掛不應出現
        assert "Show Stems" not in result or "Mark2Mark" not in result
