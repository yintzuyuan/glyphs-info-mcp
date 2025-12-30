#!/usr/bin/env python3
"""
Tests for unified tool entry points

Issue #19: Consolidate 60 tools into 8 unified entry points
"""

import pytest
from unittest.mock import MagicMock, AsyncMock


class TestUnifiedToolsRouter:
    """Test unified tools routing logic"""

    def test_handbook_router_search_action(self) -> None:
        """Test handbook router dispatches search action correctly"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        # Mock module
        mock_module = MagicMock()
        mock_module.handbook_search.return_value = "search results"

        router = UnifiedToolsRouter()
        router.set_module("handbook", mock_module)

        result = router.handbook(action="search", query="anchor")

        mock_module.handbook_search.assert_called_once_with(
            query="anchor", search_scope="all", max_results=5
        )
        assert result == "search results"

    def test_handbook_router_get_action(self) -> None:
        """Test handbook router dispatches get action correctly"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        mock_module = MagicMock()
        mock_module.handbook_fetch.return_value = "chapter content"

        router = UnifiedToolsRouter()
        router.set_module("handbook", mock_module)

        result = router.handbook(action="get", filename="anchors.md")

        mock_module.handbook_fetch.assert_called_once_with(filename="anchors.md")
        assert result == "chapter content"

    def test_handbook_router_toc_action(self) -> None:
        """Test handbook router dispatches toc action correctly"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        mock_module = MagicMock()
        mock_module.get_toc.return_value = "toc content"

        router = UnifiedToolsRouter()
        router.set_module("handbook", mock_module)

        result = router.handbook(action="toc", chapter="Interpolation")

        mock_module.get_toc.assert_called_once_with(chapter="Interpolation")
        assert result == "toc content"

    def test_handbook_router_parameter_action(self) -> None:
        """Test handbook router dispatches parameter action correctly"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        mock_module = MagicMock()
        mock_module.fetch_custom_parameter.return_value = "parameter info"

        router = UnifiedToolsRouter()
        router.set_module("handbook", mock_module)

        result = router.handbook(action="parameter", name="ascender")

        mock_module.fetch_custom_parameter.assert_called_once_with(
            parameter_name="ascender"
        )
        assert result == "parameter info"

    def test_handbook_router_invalid_action(self) -> None:
        """Test handbook router returns error for invalid action"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        router = UnifiedToolsRouter()
        router.set_module("handbook", MagicMock())

        result = router.handbook(action="invalid_action")

        assert "Invalid action" in result or "invalid" in result.lower()

    def test_vocabulary_router_translate_action(self) -> None:
        """Test vocabulary router dispatches translate action correctly"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        mock_module = MagicMock()
        mock_module.translate_term_tool.return_value = "Cancel"

        router = UnifiedToolsRouter()
        router.set_module("vocabulary", mock_module)

        result = router.vocabulary(action="translate", term="取消", target="en")

        mock_module.translate_term_tool.assert_called_once_with(
            term="取消", target_locale="en"
        )
        assert result == "Cancel"

    def test_vocabulary_router_search_action(self) -> None:
        """Test vocabulary router dispatches search action correctly"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        mock_module = MagicMock()
        mock_module.search_ui_term.return_value = "search results"

        router = UnifiedToolsRouter()
        router.set_module("vocabulary", mock_module)

        result = router.vocabulary(action="search", term="Cancel", locale="zh-Hant")

        mock_module.search_ui_term.assert_called_once_with(
            term="Cancel", locale="zh-Hant"
        )
        assert result == "search results"

    def test_api_router_search_python_action(self) -> None:
        """Test api router dispatches search_python action correctly"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        mock_module = MagicMock()
        mock_module.python_api_search.return_value = "api results"

        router = UnifiedToolsRouter()
        router.set_module("api", mock_module)

        result = router.api(action="search_python", query="GSLayer")

        mock_module.python_api_search.assert_called_once_with(
            query="GSLayer", scope="auto", max_results=5
        )
        assert result == "api results"

    def test_plugins_router_search_local_action(self) -> None:
        """Test plugins router dispatches search_local action correctly"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        mock_module = MagicMock()
        mock_module._search_local_tool.return_value = "local plugins"

        router = UnifiedToolsRouter()
        router.set_module("glyphs_plugins", mock_module)

        result = router.plugins(action="search_local", query="reporter")

        mock_module._search_local_tool.assert_called_once()
        assert result == "local plugins"

    def test_scripts_router_search_action(self) -> None:
        """Test scripts router dispatches search action correctly"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        mock_module = MagicMock()
        mock_module._search_scripts_tool.return_value = "script results"

        router = UnifiedToolsRouter()
        router.set_module("mekkablue_scripts", mock_module)

        result = router.scripts(action="search", query="anchor")

        mock_module._search_scripts_tool.assert_called_once()
        assert result == "script results"

    def test_sdk_router_search_action(self) -> None:
        """Test sdk router dispatches search action correctly"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        mock_module = MagicMock()
        mock_module._sdk_search_tool.return_value = "sdk results"

        router = UnifiedToolsRouter()
        router.set_module("glyphs_sdk", mock_module)

        result = router.sdk(action="search", query="reporter")

        mock_module._sdk_search_tool.assert_called_once()
        assert result == "sdk results"

    @pytest.mark.asyncio
    async def test_news_router_search_forum_action(self) -> None:
        """Test news router dispatches search_forum action correctly"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        mock_module = MagicMock()
        # News module uses async methods
        mock_module.web_search_forum = AsyncMock(return_value="forum results")

        router = UnifiedToolsRouter()
        router.set_module("glyphs_news", mock_module)

        result = await router.news(action="search_forum", query="variable font")

        mock_module.web_search_forum.assert_called_once_with(query="variable font")
        assert result == "forum results"

    def test_lighttable_router_search_action(self) -> None:
        """Test lighttable router dispatches search action correctly"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        mock_module = MagicMock()
        mock_module._search_api_tool.return_value = "lighttable results"

        router = UnifiedToolsRouter()
        router.set_module("light_table_api", mock_module)

        result = router.lighttable(action="search", query="DocumentState")

        mock_module._search_api_tool.assert_called_once()
        assert result == "lighttable results"


class TestUnifiedToolsModuleNotInitialized:
    """Test error handling when module not initialized"""

    def test_handbook_module_not_set(self) -> None:
        """Test handbook returns error when module not set"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        router = UnifiedToolsRouter()
        result = router.handbook(action="search", query="test")

        assert "not initialized" in result.lower() or "not available" in result.lower()

    def test_vocabulary_module_not_set(self) -> None:
        """Test vocabulary returns error when module not set"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        router = UnifiedToolsRouter()
        result = router.vocabulary(action="translate", term="test")

        assert "not initialized" in result.lower() or "not available" in result.lower()


class TestUnifiedToolsGetTools:
    """Test get_unified_tools function"""

    def test_get_unified_tools_returns_8_tools(self) -> None:
        """Test that get_unified_tools returns exactly 8 tools"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        router = UnifiedToolsRouter()
        tools = router.get_tools()

        assert len(tools) == 8
        assert "handbook" in tools
        assert "vocabulary" in tools
        assert "api" in tools
        assert "plugins" in tools
        assert "scripts" in tools
        assert "sdk" in tools
        assert "news" in tools
        assert "lighttable" in tools
