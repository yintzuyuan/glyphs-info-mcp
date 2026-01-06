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

    # Issue #43: Objective-C API proxy methods tests
    def test_api_router_search_objc_action(self) -> None:
        """Test api router dispatches search_objc action correctly (Issue #43)"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        mock_module = MagicMock()
        mock_module.search_objc_headers.return_value = "objc search results"

        router = UnifiedToolsRouter()
        router.set_module("api", mock_module)

        result = router.api(action="search_objc", query="insertText", max_results=10)

        mock_module.search_objc_headers.assert_called_once_with(
            query="insertText", max_results=10
        )
        assert result == "objc search results"

    def test_api_router_get_header_action(self) -> None:
        """Test api router dispatches get_header action correctly (Issue #43)"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        mock_module = MagicMock()
        mock_module.get_objc_header.return_value = "header content"

        router = UnifiedToolsRouter()
        router.set_module("api", mock_module)

        result = router.api(action="get_header", header_query="GSLayer")

        mock_module.get_objc_header.assert_called_once_with(header_query="GSLayer")
        assert result == "header content"

    def test_api_router_list_protocols_action(self) -> None:
        """Test api router dispatches list_protocols action correctly (Issue #43)"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        mock_module = MagicMock()
        mock_module.list_plugin_protocols.return_value = "protocol list"

        router = UnifiedToolsRouter()
        router.set_module("api", mock_module)

        result = router.api(action="list_protocols", show_details=True)

        mock_module.list_plugin_protocols.assert_called_once_with(show_details=True)
        assert result == "protocol list"

    def test_api_router_get_protocol_action(self) -> None:
        """Test api router dispatches get_protocol action correctly (Issue #43)"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        mock_module = MagicMock()
        mock_module.get_protocol_methods.return_value = "protocol methods"

        router = UnifiedToolsRouter()
        router.set_module("api", mock_module)

        result = router.api(
            action="get_protocol",
            protocol_name="GlyphsReporter",
            show_deprecated=False,
            show_optional_only=True,
        )

        mock_module.get_protocol_methods.assert_called_once_with(
            protocol_name="GlyphsReporter",
            show_deprecated=False,
            show_optional_only=True,
        )
        assert result == "protocol methods"

    def test_api_router_convert_objc_action(self) -> None:
        """Test api router dispatches convert_objc action correctly (Issue #43)"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        mock_module = MagicMock()
        mock_module.convert_objc_to_python.return_value = "python_name"

        router = UnifiedToolsRouter()
        router.set_module("api", mock_module)

        result = router.api(action="convert_objc", objc_signature="setWidth:")

        mock_module.convert_objc_to_python.assert_called_once_with(
            objc_signature="setWidth:"
        )
        assert result == "python_name"

    def test_api_router_convert_python_action(self) -> None:
        """Test api router dispatches convert_python action correctly (Issue #43)"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        mock_module = MagicMock()
        mock_module.convert_python_to_objc.return_value = "objc_signature"

        router = UnifiedToolsRouter()
        router.set_module("api", mock_module)

        result = router.api(action="convert_python", python_name="width")

        mock_module.convert_python_to_objc.assert_called_once_with(python_name="width")
        assert result == "objc_signature"

    def test_api_router_identify_method_action(self) -> None:
        """Test api router dispatches identify_method action correctly (Issue #43)"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        mock_module = MagicMock()
        mock_module.identify_method_type.return_value = "method info"

        router = UnifiedToolsRouter()
        router.set_module("api", mock_module)

        result = router.api(
            action="identify_method", method_name="drawBackground", plugin_type="filter"
        )

        mock_module.identify_method_type.assert_called_once_with(
            method_name="drawBackground", plugin_type="filter"
        )
        assert result == "method info"

    def test_api_router_get_template_action(self) -> None:
        """Test api router dispatches get_template action correctly (Issue #43)"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        mock_module = MagicMock()
        mock_module.get_method_template.return_value = "template code"

        router = UnifiedToolsRouter()
        router.set_module("api", mock_module)

        result = router.api(
            action="get_template", method_name="foreground", plugin_type="reporter"
        )

        mock_module.get_method_template.assert_called_once_with(
            method_name="foreground", plugin_type="reporter"
        )
        assert result == "template code"

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

    def test_sdk_router_list_python_templates_action(self) -> None:
        """Test sdk router dispatches list_python_templates action correctly (Issue #33)"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        mock_module = MagicMock()
        mock_module._list_python_templates_tool.return_value = "template list"

        router = UnifiedToolsRouter()
        router.set_module("glyphs_sdk", mock_module)

        result = router.sdk(action="list_python_templates")

        mock_module._list_python_templates_tool.assert_called_once_with(template_type=None)
        assert result == "template list"

    def test_sdk_router_list_python_templates_with_type(self) -> None:
        """Test sdk router dispatches list_python_templates with type filter (Issue #33)"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        mock_module = MagicMock()
        mock_module._list_python_templates_tool.return_value = "filtered templates"

        router = UnifiedToolsRouter()
        router.set_module("glyphs_sdk", mock_module)

        result = router.sdk(action="list_python_templates", template_type="filter")

        mock_module._list_python_templates_tool.assert_called_once_with(template_type="filter")
        assert result == "filtered templates"

    def test_sdk_router_get_python_template_action(self) -> None:
        """Test sdk router dispatches get_python_template action correctly (Issue #33)"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        mock_module = MagicMock()
        mock_module._get_python_template_tool.return_value = "template details"

        router = UnifiedToolsRouter()
        router.set_module("glyphs_sdk", mock_module)

        result = router.sdk(action="get_python_template", template_id="filter_without_dialog")

        mock_module._get_python_template_tool.assert_called_once_with(template_id="filter_without_dialog")
        assert result == "template details"

    def test_sdk_router_invalid_action(self) -> None:
        """Test sdk router returns error for invalid action"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        router = UnifiedToolsRouter()
        router.set_module("glyphs_sdk", MagicMock())

        result = router.sdk(action="invalid_action")

        assert "Invalid" in result or "invalid" in result.lower()

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
        """Test that get_unified_tools returns exactly 8 tools when all modules are loaded"""
        from glyphs_info_mcp.config import VALID_MODULE_NAMES
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        router = UnifiedToolsRouter()

        # Mock loading all 8 modules
        class MockModule:
            def __init__(self, name: str):
                self.name = name

        for module_name in VALID_MODULE_NAMES:
            router.set_module(module_name, MockModule(module_name))

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
