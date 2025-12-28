"""
Glyphs SDK Mapper Test Suite

Tests SDK method classification and mapping functionality.
"""

import pytest
from glyphs_info_mcp.modules.glyphs_api.objc_api.glyphs_sdk_mapper import GlyphsSDKMapper, MethodType


class TestMethodTypeIdentification:
    """Test method type identification"""

    def test_identify_protocol_required_method(self) -> None:
        """Test identifying Protocol required method"""
        assert GlyphsSDKMapper.identify_method_type("interfaceVersion") == MethodType.PROTOCOL_METHOD
        assert GlyphsSDKMapper.identify_method_type("title") == MethodType.PROTOCOL_METHOD

    def test_identify_protocol_optional_method(self) -> None:
        """Test identifying Protocol optional method"""
        assert GlyphsSDKMapper.identify_method_type("drawForegroundForLayer_options_") == MethodType.PROTOCOL_METHOD
        assert GlyphsSDKMapper.identify_method_type("drawBackgroundForLayer_options_") == MethodType.PROTOCOL_METHOD

    def test_identify_python_helper_method(self) -> None:
        """Test identifying Python helper method"""
        assert GlyphsSDKMapper.identify_method_type("drawTextAtPoint") == MethodType.PYTHON_HELPER
        assert GlyphsSDKMapper.identify_method_type("getHandleSize") == MethodType.PYTHON_HELPER
        assert GlyphsSDKMapper.identify_method_type("getScale") == MethodType.PYTHON_HELPER

    def test_identify_python_wrapped_method(self) -> None:
        """Test identifying Python wrapped method"""
        assert GlyphsSDKMapper.identify_method_type("logToConsole") == MethodType.PYTHON_WRAPPED
        assert GlyphsSDKMapper.identify_method_type("logError") == MethodType.PYTHON_WRAPPED
        assert GlyphsSDKMapper.identify_method_type("loadNib") == MethodType.PYTHON_WRAPPED

    def test_identify_unknown_method(self) -> None:
        """Test identifying unknown method"""
        assert GlyphsSDKMapper.identify_method_type("unknownMethod") == MethodType.UNKNOWN
        assert GlyphsSDKMapper.identify_method_type("customUserMethod") == MethodType.UNKNOWN


class TestPyObjCConversionNeed:
    """Test PyObjC conversion requirement determination"""

    def test_protocol_methods_need_conversion(self) -> None:
        """Test Protocol methods require conversion"""
        assert GlyphsSDKMapper.needs_pyobjc_conversion("interfaceVersion") is True
        assert GlyphsSDKMapper.needs_pyobjc_conversion("drawForegroundForLayer_options_") is True

    def test_python_helpers_no_conversion(self) -> None:
        """Test Python helper methods don't require conversion"""
        assert GlyphsSDKMapper.needs_pyobjc_conversion("drawTextAtPoint") is False
        assert GlyphsSDKMapper.needs_pyobjc_conversion("getHandleSize") is False

    def test_python_wrapped_no_conversion(self) -> None:
        """Test Python wrapped methods don't require conversion"""
        assert GlyphsSDKMapper.needs_pyobjc_conversion("logToConsole") is False
        assert GlyphsSDKMapper.needs_pyobjc_conversion("logError") is False

    def test_unknown_methods_no_conversion(self) -> None:
        """Test unknown methods don't require conversion"""
        assert GlyphsSDKMapper.needs_pyobjc_conversion("unknownMethod") is False


class TestMethodDescription:
    """Test method description"""

    def test_protocol_method_description(self) -> None:
        """Test Protocol method description"""
        desc = GlyphsSDKMapper.get_method_description("interfaceVersion")
        assert "Protocol 方法" in desc
        assert "PyObjC" in desc

    def test_python_helper_description(self) -> None:
        """Test Python helper method description"""
        desc = GlyphsSDKMapper.get_method_description("drawTextAtPoint")
        assert "SDK 輔助方法" in desc
        assert "@objc.python_method" in desc

    def test_python_wrapped_description(self) -> None:
        """Test Python wrapped method description"""
        desc = GlyphsSDKMapper.get_method_description("logToConsole")
        assert "Python 包裝方法" in desc
        assert "python_method()" in desc

    def test_unknown_method_description(self) -> None:
        """Test unknown method description"""
        desc = GlyphsSDKMapper.get_method_description("unknownMethod")
        assert "未知方法" in desc


class TestImplementationTemplate:
    """Test implementation template generation"""

    def test_protocol_method_template_no_params(self) -> None:
        """Test no-parameter Protocol method template"""
        template = GlyphsSDKMapper.get_implementation_template("interfaceVersion")
        assert template is not None
        assert "def interfaceVersion(self):" in template
        assert "return" in template

    def test_protocol_method_template_with_params(self) -> None:
        """Test Protocol method template with parameters"""
        template = GlyphsSDKMapper.get_implementation_template("drawForegroundForLayer_options_")
        assert template is not None
        assert "def drawForegroundForLayer_options_" in template
        assert "pass" in template

    def test_python_helper_template(self) -> None:
        """Test Python helper method template"""
        template = GlyphsSDKMapper.get_implementation_template("drawTextAtPoint")
        assert template is not None
        assert "@objc.python_method" in template
        assert "def drawTextAtPoint" in template

    def test_python_wrapped_template(self) -> None:
        """Test Python wrapped method template"""
        template = GlyphsSDKMapper.get_implementation_template("logToConsole")
        assert template is not None
        assert "已由 SDK 預先定義" in template
        assert "self.logToConsole" in template

    def test_unknown_method_template(self) -> None:
        """Test unknown method template"""
        template = GlyphsSDKMapper.get_implementation_template("unknownMethod")
        assert template is None


class TestListProtocolMethods:
    """Test listing Protocol methods"""

    def test_list_reporter_protocol_methods(self) -> None:
        """Test listing Reporter Protocol methods"""
        methods = GlyphsSDKMapper.list_protocol_methods("reporter")

        # Check required methods
        assert "required" in methods
        assert "interfaceVersion" in methods["required"]
        assert "title" in methods["required"]
        assert len(methods["required"]) == 2

        # Check optional methods
        assert "optional" in methods
        assert "drawForegroundForLayer_options_" in methods["optional"]
        assert "drawBackgroundForLayer_options_" in methods["optional"]
        assert len(methods["optional"]) > 0

    def test_list_unknown_plugin_type(self) -> None:
        """Test listing methods for unknown plugin type"""
        methods = GlyphsSDKMapper.list_protocol_methods("unknown")
        assert methods["required"] == []
        assert methods["optional"] == []


class TestRealWorldUseCases:
    """Test real-world use cases"""

    def test_reporter_plugin_development(self) -> None:
        """Test Reporter plugin development scenario"""
        # Developer wants to know how to use drawForegroundForLayer_options_
        method_name = "drawForegroundForLayer_options_"

        # 1. Identify method type
        method_type = GlyphsSDKMapper.identify_method_type(method_name)
        assert method_type == MethodType.PROTOCOL_METHOD

        # 2. Confirm PyObjC conversion is needed
        needs_conversion = GlyphsSDKMapper.needs_pyobjc_conversion(method_name)
        assert needs_conversion is True

        # 3. Get implementation template
        template = GlyphsSDKMapper.get_implementation_template(method_name)
        assert template is not None
        assert "def drawForegroundForLayer_options_" in template

    def test_helper_method_usage(self) -> None:
        """Test helper method usage scenario"""
        # Developer wants to know how to use drawTextAtPoint
        method_name = "drawTextAtPoint"

        # 1. Identify method type
        method_type = GlyphsSDKMapper.identify_method_type(method_name)
        assert method_type == MethodType.PYTHON_HELPER

        # 2. Confirm PyObjC conversion is not needed
        needs_conversion = GlyphsSDKMapper.needs_pyobjc_conversion(method_name)
        assert needs_conversion is False

        # 3. Get implementation template
        template = GlyphsSDKMapper.get_implementation_template(method_name)
        assert template is not None
        assert "@objc.python_method" in template

    def test_check_all_required_methods(self) -> None:
        """Test checking if all required methods are implemented"""
        methods = GlyphsSDKMapper.list_protocol_methods("reporter")
        required_methods = methods["required"]

        # Simulate developer checking which required methods they've implemented
        implemented_methods = ["interfaceVersion", "title"]

        for method in required_methods:
            assert method in implemented_methods, f"Required method {method} not yet implemented"
