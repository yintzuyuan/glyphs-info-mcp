"""測試模組啟用/禁用功能

Issue #29: 讓使用者可以啟用或關閉部分模組
"""

import logging
import os
from unittest.mock import patch

import pytest


class TestValidModuleNames:
    """VALID_MODULE_NAMES 常數測試"""

    def test_contains_all_eight_modules(self) -> None:
        """包含所有 8 個模組"""
        from glyphs_info_mcp.config import VALID_MODULE_NAMES

        expected = {
            "vocabulary",
            "handbook",
            "api",
            "glyphs_plugins",
            "glyphs_news",
            "glyphs_sdk",
            "light_table_api",
            "mekkablue_scripts",
        }
        assert VALID_MODULE_NAMES == expected


class TestParseModuleList:
    """parse_module_list() 函式測試"""

    def test_empty_string_returns_empty_set(self) -> None:
        """空字串回傳空集合"""
        from glyphs_info_mcp.config import parse_module_list

        assert parse_module_list("") == set()

    def test_whitespace_only_returns_empty_set(self) -> None:
        """只有空白回傳空集合"""
        from glyphs_info_mcp.config import parse_module_list

        assert parse_module_list("   ") == set()

    def test_single_module(self) -> None:
        """單一模組"""
        from glyphs_info_mcp.config import parse_module_list

        assert parse_module_list("handbook") == {"handbook"}

    def test_multiple_modules(self) -> None:
        """多個模組用逗號分隔"""
        from glyphs_info_mcp.config import parse_module_list

        result = parse_module_list("handbook,api,vocabulary")
        assert result == {"handbook", "api", "vocabulary"}

    def test_whitespace_around_names(self) -> None:
        """名稱周圍有空白"""
        from glyphs_info_mcp.config import parse_module_list

        result = parse_module_list(" handbook , api ")
        assert result == {"handbook", "api"}

    def test_duplicate_names_deduplicated(self) -> None:
        """重複名稱會去重"""
        from glyphs_info_mcp.config import parse_module_list

        result = parse_module_list("handbook,handbook,api")
        assert result == {"handbook", "api"}

    def test_invalid_name_ignored_with_warning(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """無效名稱會被忽略並記錄警告"""
        from glyphs_info_mcp.config import parse_module_list

        result = parse_module_list("handbook,invalid_module,api")
        assert result == {"handbook", "api"}
        assert "invalid_module" in caplog.text
        assert "Unknown module" in caplog.text

    def test_empty_segments_ignored(self) -> None:
        """空白段落被忽略"""
        from glyphs_info_mcp.config import parse_module_list

        result = parse_module_list("handbook,,api,")
        assert result == {"handbook", "api"}


class TestIsModuleEnabled:
    """is_module_enabled() 函式測試"""

    def test_no_env_vars_all_enabled(self) -> None:
        """未設定任何環境變數時，所有模組皆啟用"""
        from glyphs_info_mcp.config import (
            DISABLED_MODULES_ENV,
            ENABLED_MODULES_ENV,
            is_module_enabled,
        )

        with patch.dict(
            os.environ,
            {ENABLED_MODULES_ENV: "", DISABLED_MODULES_ENV: ""},
            clear=False,
        ):
            # 確保環境變數被清空
            os.environ.pop(ENABLED_MODULES_ENV, None)
            os.environ.pop(DISABLED_MODULES_ENV, None)

            assert is_module_enabled("handbook") is True
            assert is_module_enabled("api") is True
            assert is_module_enabled("glyphs_news") is True

    def test_whitelist_only_enables_listed_modules(self) -> None:
        """白名單模式：只啟用列出的模組"""
        from glyphs_info_mcp.config import ENABLED_MODULES_ENV, is_module_enabled

        with patch.dict(os.environ, {ENABLED_MODULES_ENV: "handbook,api"}):
            assert is_module_enabled("handbook") is True
            assert is_module_enabled("api") is True
            assert is_module_enabled("glyphs_news") is False
            assert is_module_enabled("vocabulary") is False

    def test_blacklist_disables_listed_modules(self) -> None:
        """黑名單模式：排除列出的模組"""
        from glyphs_info_mcp.config import DISABLED_MODULES_ENV, is_module_enabled

        with patch.dict(os.environ, {DISABLED_MODULES_ENV: "glyphs_news,glyphs_plugins"}):
            assert is_module_enabled("handbook") is True
            assert is_module_enabled("api") is True
            assert is_module_enabled("glyphs_news") is False
            assert is_module_enabled("glyphs_plugins") is False

    def test_whitelist_takes_precedence_over_blacklist(self) -> None:
        """白名單優先於黑名單"""
        from glyphs_info_mcp.config import (
            DISABLED_MODULES_ENV,
            ENABLED_MODULES_ENV,
            is_module_enabled,
        )

        with patch.dict(
            os.environ,
            {
                ENABLED_MODULES_ENV: "handbook,api",
                DISABLED_MODULES_ENV: "api,glyphs_news",
            },
        ):
            # 白名單優先，api 應該啟用
            assert is_module_enabled("handbook") is True
            assert is_module_enabled("api") is True
            # 不在白名單中的模組被禁用
            assert is_module_enabled("glyphs_news") is False
            assert is_module_enabled("vocabulary") is False

    def test_empty_whitelist_enables_all(self) -> None:
        """空白名單等同於未設定，全部啟用"""
        from glyphs_info_mcp.config import ENABLED_MODULES_ENV, is_module_enabled

        with patch.dict(os.environ, {ENABLED_MODULES_ENV: ""}):
            assert is_module_enabled("handbook") is True
            assert is_module_enabled("glyphs_news") is True

    def test_empty_blacklist_enables_all(self) -> None:
        """空黑名單等同於未設定，全部啟用"""
        from glyphs_info_mcp.config import DISABLED_MODULES_ENV, is_module_enabled

        with patch.dict(os.environ, {DISABLED_MODULES_ENV: ""}):
            assert is_module_enabled("handbook") is True
            assert is_module_enabled("glyphs_news") is True

    def test_invalid_module_name_returns_false(self) -> None:
        """無效模組名稱回傳 False"""
        from glyphs_info_mcp.config import is_module_enabled

        assert is_module_enabled("nonexistent_module") is False

    def test_logs_info_when_both_set(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """同時設定白名單和黑名單時記錄 INFO 日誌（首次呼叫時）"""
        import glyphs_info_mcp.config as config_module
        from glyphs_info_mcp.config import (
            DISABLED_MODULES_ENV,
            ENABLED_MODULES_ENV,
            is_module_enabled,
        )

        # 重置全域狀態以確保日誌會被記錄
        config_module._whitelist_precedence_logged = False

        with patch.dict(
            os.environ,
            {
                ENABLED_MODULES_ENV: "handbook",
                DISABLED_MODULES_ENV: "api",
            },
        ):
            with caplog.at_level(logging.INFO):
                is_module_enabled("handbook")
                assert "whitelist" in caplog.text.lower() or "enabled" in caplog.text.lower()


class MockModule:
    """Mock module for testing"""

    def __init__(self, name: str):
        self.name = name


class TestUnifiedToolsDynamicRegistration:
    """測試統一工具動態註冊機制"""

    def test_all_modules_enabled_registers_all_tools(self) -> None:
        """所有模組啟用時註冊 8 個工具"""
        from glyphs_info_mcp.config import VALID_MODULE_NAMES
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        router = UnifiedToolsRouter()
        # 模擬載入所有 8 個模組
        for module_name in VALID_MODULE_NAMES:
            router.set_module(module_name, MockModule(module_name))

        tools = router.get_tools()
        assert len(tools) == 8
        assert set(tools.keys()) == {
            "handbook",
            "vocabulary",
            "api",
            "plugins",
            "scripts",
            "sdk",
            "news",
            "lighttable",
        }

    def test_whitelist_filters_tools(self) -> None:
        """白名單模式只註冊對應工具"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        router = UnifiedToolsRouter()
        router.set_module("handbook", MockModule("handbook"))
        router.set_module("api", MockModule("api"))

        tools = router.get_tools()
        assert len(tools) == 2
        assert set(tools.keys()) == {"handbook", "api"}

    def test_blacklist_excludes_tools(self) -> None:
        """黑名單模式排除指定工具"""
        from glyphs_info_mcp.config import VALID_MODULE_NAMES
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        router = UnifiedToolsRouter()
        # 載入除了 news 和 plugins 外的所有模組
        for module_name in VALID_MODULE_NAMES:
            if module_name not in ["glyphs_news", "glyphs_plugins"]:
                router.set_module(module_name, MockModule(module_name))

        tools = router.get_tools()
        assert len(tools) == 6
        assert "news" not in tools
        assert "plugins" not in tools

    def test_empty_modules_returns_empty_tools(self) -> None:
        """無模組時不註冊任何工具"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        router = UnifiedToolsRouter()
        tools = router.get_tools()
        assert len(tools) == 0

    def test_module_tool_mapping_consistency(self) -> None:
        """驗證模組與工具對應表的一致性"""
        from glyphs_info_mcp.config import VALID_MODULE_NAMES
        from glyphs_info_mcp.unified_tools import MODULE_TOOL_MAPPING

        mapped_modules = set(MODULE_TOOL_MAPPING.keys())
        assert mapped_modules == VALID_MODULE_NAMES, (
            f"MODULE_TOOL_MAPPING 與 VALID_MODULE_NAMES 不一致。"
            f"Missing: {VALID_MODULE_NAMES - mapped_modules}, "
            f"Extra: {mapped_modules - VALID_MODULE_NAMES}"
        )
