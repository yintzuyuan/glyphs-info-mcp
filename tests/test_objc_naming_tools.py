"""
Objective-C API Module - 命名轉換工具測試

測試 ObjectiveCAPIModule 的 4 個新增命名轉換 MCP 工具。
"""

from pathlib import Path

import pytest

from glyphs_info_mcp.modules.glyphs_api.objc_api.objc_api_module import ObjectiveCAPIModule


@pytest.fixture
def module() -> ObjectiveCAPIModule:
    """建立測試用的 ObjectiveCAPIModule 實例"""
    test_module = ObjectiveCAPIModule()
    # 不需要完整初始化（命名轉換工具不依賴資料檔案）
    test_module.is_initialized = True
    return test_module


class TestConvertObjCToPython:
    """測試 api_convert_objc_to_python 工具"""

    def test_convert_no_param_method(self, module: ObjectiveCAPIModule) -> None:
        """測試無參數方法轉換"""
        result = module.convert_objc_to_python("interfaceVersion")
        assert "interfaceVersion" in result
        assert "Conversion Result" in result

    def test_convert_single_param_method(self, module: ObjectiveCAPIModule) -> None:
        """測試單參數方法轉換"""
        result = module.convert_objc_to_python("setValue:(id)value")
        assert "setValue_" in result
        assert "Conversion Result" in result

    def test_convert_full_signature(self, module: ObjectiveCAPIModule) -> None:
        """測試完整 Objective-C 簽名轉換"""
        signature = "- (void)drawForegroundForLayer:(GSLayer *)layer options:(NSDictionary *)options;"
        result = module.convert_objc_to_python(signature)
        assert "drawForegroundForLayer_options_" in result
        assert "Conversion Result" in result


class TestConvertPythonToObjC:
    """測試 api_convert_python_to_objc 工具"""

    def test_convert_no_param_method(self, module: ObjectiveCAPIModule) -> None:
        """測試無參數方法轉換"""
        result = module.convert_python_to_objc("interfaceVersion")
        assert "interfaceVersion" in result
        assert "Conversion Result" in result

    def test_convert_single_param_method(self, module: ObjectiveCAPIModule) -> None:
        """測試單參數方法轉換"""
        result = module.convert_python_to_objc("setValue_")
        assert "setValue:" in result
        assert "Conversion Result" in result

    def test_convert_multiple_params_method(self, module: ObjectiveCAPIModule) -> None:
        """測試多參數方法轉換"""
        result = module.convert_python_to_objc("drawForegroundForLayer_options_")
        assert "drawForegroundForLayer:options:" in result
        assert "Conversion Result" in result

    def test_convert_with_param_count_validation(self, module: ObjectiveCAPIModule) -> None:
        """測試帶參數數量驗證的轉換"""
        result = module.convert_python_to_objc("drawForegroundForLayer_options_", param_count=2)
        assert "drawForegroundForLayer:options:" in result

    def test_convert_param_count_mismatch(self, module: ObjectiveCAPIModule) -> None:
        """測試參數數量不匹配"""
        result = module.convert_python_to_objc("drawForegroundForLayer_options_", param_count=3)
        assert "Conversion failed" in result or "Parameter count mismatch" in result


class TestIdentifyMethodType:
    """測試 api_identify_method_type 工具"""

    def test_identify_protocol_method(self, module: ObjectiveCAPIModule) -> None:
        """測試識別 Protocol 方法"""
        result = module.identify_method_type("interfaceVersion")
        assert "Method Analysis" in result
        assert "protocol" in result
        assert "✅ Yes" in result  # 需要 PyObjC 轉換

    def test_identify_python_helper_method(self, module: ObjectiveCAPIModule) -> None:
        """測試識別 Python 輔助方法"""
        result = module.identify_method_type("drawTextAtPoint")
        assert "Method Analysis" in result
        assert "python_helper" in result
        assert "❌ No" in result  # 不需要 PyObjC 轉換

    def test_identify_python_wrapped_method(self, module: ObjectiveCAPIModule) -> None:
        """測試識別 Python 包裝方法"""
        result = module.identify_method_type("logToConsole")
        assert "Method Analysis" in result
        assert "python_wrapped" in result
        assert "❌ No" in result

    def test_identify_unknown_method(self, module: ObjectiveCAPIModule) -> None:
        """測試識別未知方法"""
        result = module.identify_method_type("unknownMethod")
        assert "Method Analysis" in result
        assert "unknown" in result


class TestGetMethodTemplate:
    """測試 api_get_method_template 工具"""

    def test_get_protocol_method_template(self, module: ObjectiveCAPIModule) -> None:
        """測試取得 Protocol 方法範本"""
        result = module.get_method_template("interfaceVersion")
        assert "Implementation Template" in result
        assert "def interfaceVersion(self):" in result
        assert "```python" in result

    def test_get_protocol_method_with_params_template(self, module: ObjectiveCAPIModule) -> None:
        """測試取得帶參數 Protocol 方法範本"""
        result = module.get_method_template("drawForegroundForLayer_options_")
        assert "Implementation Template" in result
        assert "def drawForegroundForLayer_options_" in result

    def test_get_python_helper_template(self, module: ObjectiveCAPIModule) -> None:
        """測試取得 Python 輔助方法範本"""
        result = module.get_method_template("drawTextAtPoint")
        assert "Implementation Template" in result
        assert "@objc.python_method" in result
        assert "def drawTextAtPoint" in result

    def test_get_python_wrapped_template(self, module: ObjectiveCAPIModule) -> None:
        """測試取得 Python 包裝方法範本"""
        result = module.get_method_template("logToConsole")
        assert "Implementation Template" in result
        assert "predefined by SDK" in result

    def test_get_unknown_method_template(self, module: ObjectiveCAPIModule) -> None:
        """測試取得未知方法範本"""
        result = module.get_method_template("unknownMethod")
        assert "Cannot generate template" in result


class TestModuleIntegration:
    """測試模組整合"""

    def test_module_has_all_tools(self, module: ObjectiveCAPIModule) -> None:
        """測試模組包含所有工具"""
        tools = module.get_tools()
        assert 'api_convert_objc_to_python' in tools
        assert 'api_convert_python_to_objc' in tools
        assert 'api_identify_method_type' in tools
        assert 'api_get_method_template' in tools

    def test_module_info_updated(self, module: ObjectiveCAPIModule) -> None:
        """測試模組資訊已更新"""
        info = module.get_module_info()
        assert info['tools_count'] == 8  # 4 個原有 + 4 個新增
        assert "naming conversion" in info['description'].lower()

    def test_all_tools_callable(self, module: ObjectiveCAPIModule) -> None:
        """測試所有工具可呼叫"""
        tools = module.get_tools()
        for tool_name, tool_func in tools.items():
            assert callable(tool_func), f"{tool_name} 應該是可呼叫的"


class TestRealWorldWorkflow:
    """測試真實世界工作流程"""

    def test_reporter_plugin_development_workflow(self, module: ObjectiveCAPIModule) -> None:
        """測試 Reporter 外掛開發完整流程"""
        # 1. 開發者看到文件中的 Objective-C 方法
        objc_method = "- (void)drawForegroundForLayer:(GSLayer *)layer options:(NSDictionary *)options;"

        # 2. 轉換為 Python 方法名稱
        conversion_result = module.convert_objc_to_python(objc_method)
        assert "drawForegroundForLayer_options_" in conversion_result

        # 3. 識別方法類型
        type_result = module.identify_method_type("drawForegroundForLayer_options_")
        assert "protocol" in type_result
        assert "✅ Yes" in type_result

        # 4. 取得實作範本
        template_result = module.get_method_template("drawForegroundForLayer_options_")
        assert "def drawForegroundForLayer_options_" in template_result

    def test_helper_method_workflow(self, module: ObjectiveCAPIModule) -> None:
        """測試輔助方法使用流程"""
        # 1. 開發者想使用 drawTextAtPoint
        method_name = "drawTextAtPoint"

        # 2. 識別方法類型
        type_result = module.identify_method_type(method_name)
        assert "python_helper" in type_result
        assert "❌ No" in type_result  # 不需要 PyObjC 轉換

        # 3. 取得實作範本
        template_result = module.get_method_template(method_name)
        assert "@objc.python_method" in template_result

    def test_reverse_engineering_workflow(self, module: ObjectiveCAPIModule) -> None:
        """測試從 Python 程式碼反推 Objective-C"""
        # 1. 開發者看到 Python 程式碼中的方法名稱
        python_method = "drawForegroundForLayer_options_"

        # 2. 轉換回 Objective-C
        conversion_result = module.convert_python_to_objc(python_method)
        assert "drawForegroundForLayer:options:" in conversion_result

        # 3. 可用於搜尋文件或 Headers
        # (在實際使用中，開發者會使用這個結果去 api_search_objc_headers)
