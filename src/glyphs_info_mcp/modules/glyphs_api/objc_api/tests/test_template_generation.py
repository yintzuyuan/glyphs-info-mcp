"""
Template Auto-Generation Test Suite

Tests auto-generation of enhanced templates from Protocol data.
"""

import pytest
from glyphs_info_mcp.modules.glyphs_api.objc_api.glyphs_sdk_mapper import GlyphsSDKMapper


class TestParameterExtraction:
    """Test parameter name extraction"""

    def test_extract_single_parameter(self) -> None:
        """Test extracting single parameter"""
        parameters = ["(GSLayer *)layer"]
        result = GlyphsSDKMapper._extract_parameter_names(parameters)
        assert result == ["layer"]

    def test_extract_multiple_parameters(self) -> None:
        """Test extracting multiple parameters"""
        parameters = ["(GSLayer *)layer", "(NSDictionary *)options"]
        result = GlyphsSDKMapper._extract_parameter_names(parameters)
        assert result == ["layer", "options"]

    def test_extract_without_pointer(self) -> None:
        """Test extracting parameters without pointer types"""
        parameters = ["(NSInteger)value", "(BOOL)flag"]
        result = GlyphsSDKMapper._extract_parameter_names(parameters)
        assert result == ["value", "flag"]

    def test_extract_mixed_types(self) -> None:
        """Test mixed type parameters"""
        parameters = ["(GSLayer *)layer", "(NSInteger)index", "(BOOL)flag"]
        result = GlyphsSDKMapper._extract_parameter_names(parameters)
        assert result == ["layer", "index", "flag"]

    def test_extract_empty_list(self) -> None:
        """Test empty parameter list"""
        parameters: list[str] = []
        result = GlyphsSDKMapper._extract_parameter_names(parameters)
        assert result == []

    def test_extract_complex_types(self) -> None:
        """Test complex types"""
        parameters = [
            "(NSViewController<GSGlyphEditViewControllerProtocol> *)controller",
            "(id<NSCoding>)object"
        ]
        result = GlyphsSDKMapper._extract_parameter_names(parameters)
        assert result == ["controller", "object"]


class TestDocstringGeneration:
    """Test docstring generation"""

    def test_generate_basic_docstring(self) -> None:
        """Test generating basic docstring"""
        docstring = GlyphsSDKMapper._generate_docstring("reporter")
        assert '"""' in docstring
        assert "GlyphsReporter Protocol" in docstring

    def test_generate_with_parameters(self) -> None:
        """Test generating docstring with parameters"""
        parameters = ["(GSLayer *)layer", "(NSDictionary *)options"]
        docstring = GlyphsSDKMapper._generate_docstring("reporter", parameters)

        assert "Args:" in docstring
        assert "layer:" in docstring
        assert "options:" in docstring
        assert "GSLayer" in docstring
        assert "NSDictionary" in docstring

    def test_generate_without_parameters(self) -> None:
        """Test generating docstring without parameters"""
        docstring = GlyphsSDKMapper._generate_docstring("reporter", None)
        assert "Args:" not in docstring
        assert '"""' in docstring

    def test_generate_for_different_plugin_types(self) -> None:
        """Test docstring for different plugin types"""
        docstring_reporter = GlyphsSDKMapper._generate_docstring("reporter")
        docstring_filter = GlyphsSDKMapper._generate_docstring("filter")

        assert "GlyphsReporter Protocol" in docstring_reporter
        assert "FilterPlugin Protocol" in docstring_filter


class TestEnhancedTemplateGeneration:
    """Test enhanced template generation"""

    def test_generate_with_protocol_data(self) -> None:
        """Test generating template with Protocol data"""
        method_info = {
            'name': 'drawForegroundForLayer',
            'parameters': ["(GSLayer *)layer", "(NSDictionary *)options"],
            'return_type': 'void'
        }

        template = GlyphsSDKMapper.get_implementation_template(
            "drawForegroundForLayer_options_",
            "reporter",
            method_info=method_info
        )
        assert template is not None

        # Check parameter list
        assert "def drawForegroundForLayer_options_(self, layer, options):" in template

        # Check docstring
        assert '"""' in template
        assert "Args:" in template
        assert "layer:" in template
        assert "options:" in template

    def test_generate_without_protocol_data_fallback(self) -> None:
        """Test fallback when no Protocol data available"""
        template = GlyphsSDKMapper.get_implementation_template(
            "drawForegroundForLayer_options_",
            "reporter",
            method_info=None
        )
        assert template is not None

        # Should use legacy template
        assert "def drawForegroundForLayer_options_(self, ...)" in template
        assert "# 實作 Protocol 方法" in template

    def test_generate_no_param_method_with_protocol_data(self) -> None:
        """Test no-parameter method (with Protocol data)"""
        method_info = {
            'name': 'interfaceVersion',
            'parameters': [],
            'return_type': 'NSUInteger'
        }

        template = GlyphsSDKMapper.get_implementation_template(
            "interfaceVersion",
            "reporter",
            method_info=method_info
        )
        assert template is not None

        # No-parameter method should generate docstring
        assert "def interfaceVersion(self):" in template
        assert '"""' in template
        assert "GlyphsReporter Protocol" in template
        assert "return ..." in template

    def test_generate_helper_method_unchanged(self) -> None:
        """Test helper method is unaffected"""
        template = GlyphsSDKMapper.get_implementation_template(
            "drawTextAtPoint",
            "reporter",
            method_info={"parameters": ["test"]}  # Should be ignored even if data is provided
        )
        assert template is not None

        # Helper method still uses legacy template
        assert "@objc.python_method" in template
        assert "def drawTextAtPoint(self, ...)" in template


class TestRealWorldProtocolData:
    """Test real-world Protocol data"""

    def test_glyphs_reporter_method(self) -> None:
        """Test GlyphsReporter Protocol method"""
        method_info = {
            'name': 'drawBackgroundForLayer',
            'parameters': ["(GSLayer *)Layer", "(NSDictionary *)options"],
            'return_type': 'void',
            'method_type': 'instance'
        }

        template = GlyphsSDKMapper.get_implementation_template(
            "drawBackgroundForLayer_options_",
            "reporter",
            method_info=method_info
        )
        assert template is not None

        assert "def drawBackgroundForLayer_options_(self, Layer, options):" in template
        assert "GlyphsReporter Protocol" in template
        assert "Args:" in template

    def test_complex_parameter_types(self) -> None:
        """Test complex parameter types"""
        method_info = {
            'parameters': [
                "(NSViewController<GSGlyphEditViewControllerProtocol> *)controller",
                "(NSArray<NSString *> *)items"
            ]
        }

        template = GlyphsSDKMapper.get_implementation_template(
            "addMenuItemsForEvent_toMenu_",
            "reporter",
            method_info=method_info
        )
        assert template is not None

        assert "controller" in template
        assert "items" in template
        assert "NSViewController<GSGlyphEditViewControllerProtocol>" in template

    def test_three_parameter_method_recognition(self) -> None:
        """Test 3-parameter method recognition"""
        from glyphs_info_mcp.modules.glyphs_api.objc_api.glyphs_sdk_mapper import GlyphsSDKMapper, MethodType

        # Confirm 3-parameter version of addMenuItemsForEvent is recognized as Protocol method
        method_type = GlyphsSDKMapper.identify_method_type("addMenuItemsForEvent_controller_toMenu_")
        assert method_type == MethodType.PROTOCOL_METHOD

        # Confirm template can be generated
        template = GlyphsSDKMapper.get_implementation_template(
            "addMenuItemsForEvent_controller_toMenu_",
            "reporter"
        )
        assert template is not None
        assert "def addMenuItemsForEvent_controller_toMenu_" in template


class TestBackwardCompatibility:
    """Test backward compatibility"""

    def test_old_api_still_works(self) -> None:
        """Test old API still works"""
        # Not passing method_info, should still work
        template = GlyphsSDKMapper.get_implementation_template(
            "drawForegroundForLayer_options_",
            "reporter"
        )
        assert template is not None

        assert "def drawForegroundForLayer_options_" in template

    def test_existing_tests_not_broken(self) -> None:
        """Test existing tests are not broken"""
        # Test all method types still work
        protocol_template = GlyphsSDKMapper.get_implementation_template("interfaceVersion")
        helper_template = GlyphsSDKMapper.get_implementation_template("drawTextAtPoint")
        wrapped_template = GlyphsSDKMapper.get_implementation_template("logToConsole")

        assert protocol_template is not None
        assert helper_template is not None
        assert wrapped_template is not None


class TestHeaderParserFormat:
    """Test HeaderParser format support"""

    def test_extract_header_parser_format_single_param(self) -> None:
        """Test extracting single parameter in HeaderParser format"""
        # HeaderParser format: Type * name
        parameters = ["GSLayer * layer"]
        result = GlyphsSDKMapper._extract_parameter_names(parameters)
        assert result == ["layer"]

    def test_extract_header_parser_format_multiple_params(self) -> None:
        """Test extracting multiple parameters in HeaderParser format"""
        parameters = ["GSLayer * layer", "NSDictionary * options"]
        result = GlyphsSDKMapper._extract_parameter_names(parameters)
        assert result == ["layer", "options"]

    def test_extract_mixed_formats(self) -> None:
        """Test mixed formats"""
        # Test both Objective-C format and HeaderParser format
        parameters = [
            "(GSLayer *)layer",       # Objective-C format
            "NSDictionary * options"  # HeaderParser format
        ]
        result = GlyphsSDKMapper._extract_parameter_names(parameters)
        assert result == ["layer", "options"]

    def test_generate_docstring_with_header_parser_format(self) -> None:
        """Test generating docstring with HeaderParser format"""
        parameters = ["GSLayer * layer", "NSDictionary * options"]
        docstring = GlyphsSDKMapper._generate_docstring(
            "reporter",
            parameters
        )

        assert '"""' in docstring
        assert "Args:" in docstring
        assert "layer:" in docstring
        assert "options:" in docstring
        assert "GSLayer *" in docstring or "GSLayer" in docstring
        assert "NSDictionary *" in docstring or "NSDictionary" in docstring

    def test_generate_template_with_header_parser_format(self) -> None:
        """Test generating complete template with HeaderParser format"""
        method_info = {
            'name': 'drawForegroundForLayer',
            'parameters': ["GSLayer * layer", "NSDictionary * options"],
            'return_type': 'void'
        }

        template = GlyphsSDKMapper.get_implementation_template(
            "drawForegroundForLayer_options_",
            "reporter",
            method_info=method_info
        )
        assert template is not None

        # Should successfully generate template with correct parameter names
        assert "def drawForegroundForLayer_options_(self, layer, options):" in template
        assert '"""' in template
        assert "Args:" in template
