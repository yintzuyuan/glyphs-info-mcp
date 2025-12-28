#!/usr/bin/env python3
"""
測試統一錯誤處理系統
"""

import sys
from pathlib import Path

import pytest

# 添加共享核心庫路徑
shared_core_path = str(Path(__file__).parent.parent / "src" / "shared")
if shared_core_path not in sys.path:
    sys.path.insert(0, shared_core_path)

from glyphs_info_mcp.shared.core.error_handling import (
    ErrorCategory,
    ErrorHandler,
    MCPError,
    invalid_param_error,
    network_error,
    not_found_error,
    safe_error_message,
    too_many_results_error,
)


class TestMCPError:
    """測試 MCPError 基本功能"""

    def test_basic_error_creation(self) -> None:
        """測試基本錯誤建立"""
        error = MCPError(
            message="Test error",
            category=ErrorCategory.INVALID_INPUT,
        )
        assert error.message == "Test error"
        assert error.category == ErrorCategory.INVALID_INPUT
        assert error.suggestions == []
        assert error.context == {}

    def test_error_with_suggestions(self) -> None:
        """測試帶建議的錯誤"""
        error = MCPError(
            message="Parameter error",
            category=ErrorCategory.INVALID_INPUT,
            suggestions=["Suggestion 1", "Suggestion 2"],
        )
        message = error.to_user_message()
        assert "❌ Parameter error" in message
        assert "💡 Suggested actions:" in message
        assert "1. Suggestion 1" in message
        assert "2. Suggestion 2" in message

    def test_error_with_context(self) -> None:
        """測試帶上下文的錯誤"""
        error = MCPError(
            message="Resource not found",
            category=ErrorCategory.RESOURCE_NOT_FOUND,
            context={"resource": "test.py", "location": "/tmp"},
        )
        message = error.to_user_message()
        assert "📋 Related information:" in message
        assert "resource: test.py" in message
        assert "location: /tmp" in message


class TestErrorHandler:
    """測試 ErrorHandler 標準化錯誤處理"""

    def test_handle_not_found_basic(self) -> None:
        """測試基本的未找到錯誤"""
        error = ErrorHandler.handle_not_found(
            resource_type="class",
            resource_id="NonExistentClass",
        )
        assert "class not found: 'NonExistentClass'" in error.message
        assert len(error.suggestions) > 0
        assert "NonExistentClass" in error.context["searched_id"]

    def test_handle_not_found_with_alternatives(self) -> None:
        """測試帶替代選項的未找到錯誤"""
        error = ErrorHandler.handle_not_found(
            resource_type="method",
            resource_id="getName",
            available_alternatives=["get_name", "getName", "setName"],
            search_tool="api_search",
        )
        message = error.to_user_message()
        assert "get_name" in message
        assert "api_search" in message
        assert error.context["alternatives_count"] == 3

    def test_handle_invalid_parameter(self) -> None:
        """測試無效參數錯誤"""
        error = ErrorHandler.handle_invalid_parameter(
            parameter_name="max_results",
            provided_value=1000,
            valid_range="1-100",
        )
        assert "max_results" in error.message
        assert "1000" in error.message
        assert "1-100" in error.to_user_message()

    def test_handle_invalid_parameter_with_options(self) -> None:
        """測試帶選項列表的無效參數錯誤"""
        error = ErrorHandler.handle_invalid_parameter(
            parameter_name="format",
            provided_value="xml",
            valid_options=["json", "markdown", "text"],
        )
        message = error.to_user_message()
        assert "format" in message
        assert "xml" in message
        assert "json" in message
        assert "markdown" in message

    def test_handle_too_many_results(self) -> None:
        """測試結果過多錯誤"""
        error = ErrorHandler.handle_too_many_results(
            result_count=1000,
            limit=100,
            filter_suggestions=["Use category parameter to filter"],
        )
        assert "1000" in error.message
        assert "100" in error.message
        assert "category" in error.to_user_message()
        assert error.context["result_count"] == 1000

    def test_handle_network_error(self) -> None:
        """測試網路錯誤"""
        error = ErrorHandler.handle_network_error(
            operation="Search Glyphs tutorials",
            url="https://glyphsapp.com/tutorials",
        )
        assert "Network request failed" in error.message
        assert "glyphsapp.com" in error.context["domain"]
        # URL 不應該完整顯示在上下文中（安全考量）
        assert "https://glyphsapp.com/tutorials" not in error.to_user_message()

    def test_handle_initialization_error(self) -> None:
        """測試初始化錯誤"""
        error = ErrorHandler.handle_initialization_error(
            module_name="handbook",
            reason="Data file not found",
            fix_suggestions=["Run download_data.sh to download data"],
        )
        assert "handbook" in error.message
        assert "Data file not found" in error.message
        assert "download_data.sh" in error.to_user_message()

    def test_handle_timeout(self) -> None:
        """測試逾時錯誤"""
        error = ErrorHandler.handle_timeout(
            operation="Search large database",
            timeout_seconds=30,
            reduce_scope_tips=["Use limit parameter to restrict results"],
        )
        assert "timed out" in error.message
        assert "30 seconds" in error.message
        assert "limit" in error.to_user_message()


class TestShortcutFunctions:
    """測試快捷方法"""

    def test_not_found_error_shortcut(self) -> None:
        """測試 not_found_error 快捷方法"""
        error = not_found_error("script", "MyScript.py")
        assert isinstance(error, MCPError)
        assert error.category == ErrorCategory.RESOURCE_NOT_FOUND
        assert "MyScript.py" in error.message

    def test_invalid_param_error_shortcut(self) -> None:
        """測試 invalid_param_error 快捷方法"""
        error = invalid_param_error("query", "")
        assert isinstance(error, MCPError)
        assert error.category == ErrorCategory.INVALID_INPUT

    def test_too_many_results_error_shortcut(self) -> None:
        """測試 too_many_results_error 快捷方法"""
        error = too_many_results_error(500, 100)
        assert isinstance(error, MCPError)
        assert error.category == ErrorCategory.RESOURCE_EXHAUSTED

    def test_network_error_shortcut(self) -> None:
        """測試 network_error 快捷方法"""
        error = network_error("Fetch tutorial")
        assert isinstance(error, MCPError)
        assert error.category == ErrorCategory.NETWORK_ERROR


class TestSafeErrorMessage:
    """測試安全錯誤訊息轉換"""

    def test_mcp_error_passthrough(self) -> None:
        """測試 MCPError 直接傳遞"""
        original_error = not_found_error("file", "test.txt")
        message = safe_error_message(original_error, "Read file")
        assert "test.txt" in message
        assert "❌" in message

    def test_generic_exception_handling(self) -> None:
        """測試通用異常處理"""
        generic_error = ValueError("Some internal error")
        message = safe_error_message(generic_error, "Process data")
        # 不應該洩漏內部錯誤訊息
        assert "Some internal error" not in message
        # 應該提供通用建議
        assert "Suggested actions" in message
        assert "❌" in message


def test_error_message_formatting() -> None:
    """測試錯誤訊息格式化的完整性"""
    error = ErrorHandler.handle_not_found(
        resource_type="API method",
        resource_id="nonExistentMethod",
        available_alternatives=["existingMethod1", "existingMethod2"],
        search_tool="api_search",
    )

    message = error.to_user_message()

    # 檢查必要元素
    assert "❌" in message  # 錯誤標記
    assert "💡" in message  # 建議標記
    assert "📋" in message  # 上下文標記
    assert "API method" in message
    assert "nonExistentMethod" in message
    assert "existingMethod1" in message


if __name__ == "__main__":
    # 執行測試
    pytest.main([__file__, "-v"])
