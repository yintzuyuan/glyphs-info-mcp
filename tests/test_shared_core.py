"""
共享核心庫測試 - TDD 方法
"""

import sys
from pathlib import Path

# 添加共享庫到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_shared_base_module_interface() -> None:
    """測試共享基底模組介面"""
    # 這個測試會失敗，因為還沒有實作
    # 這是 TDD 的紅燈階段
    from glyphs_info_mcp.shared.core.base_module import BaseMCPModule

    # 測試抽象基底類可以被正確定義
    assert hasattr(BaseMCPModule, "initialize")
    assert hasattr(BaseMCPModule, "get_tools")
    assert hasattr(BaseMCPModule, "get_module_info")


def test_module_independence() -> None:
    """測試模組間無直接依賴"""
    # 確保共享基底類不依賴特定模組
    from glyphs_info_mcp.shared.core.base_module import BaseMCPModule
    import inspect

    # 基底類應該是通用的，檢查類別定義本身不包含特定業務邏輯
    class_attrs = [attr for attr in dir(BaseMCPModule) if not attr.startswith('_')]
    assert "vocabulary_data" not in class_attrs
    assert "handbook_data" not in class_attrs
    assert "api_data" not in class_attrs


def test_shared_interfaces() -> None:
    """測試共享介面定義"""
    from glyphs_info_mcp.shared.core.interfaces import ModuleInterface, ToolInterface

    # 測試模組介面有必要的方法
    assert hasattr(ModuleInterface, "initialize")
    assert hasattr(ModuleInterface, "get_tools")

    # 測試工具介面標準化 - dataclass 有這些欄位
    from dataclasses import fields

    tool_fields = [f.name for f in fields(ToolInterface)]
    assert "name" in tool_fields
    assert "description" in tool_fields
    assert "function" in tool_fields


if __name__ == "__main__":
    # 執行測試來驗證紅燈狀態
    try:
        test_shared_base_module_interface()
        print("❌ 測試不應該通過（紅燈階段）")
    except (ImportError, AttributeError):
        print("✅ 紅燈階段：測試失敗是預期的")

    try:
        test_shared_interfaces()
        print("❌ 測試不應該通過（紅燈階段）")
    except (ImportError, AttributeError):
        print("✅ 紅燈階段：測試失敗是預期的")
