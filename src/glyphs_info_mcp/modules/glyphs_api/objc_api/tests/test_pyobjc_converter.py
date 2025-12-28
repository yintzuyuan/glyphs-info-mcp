"""
PyObjC Converter Test Suite

Tests bidirectional conversion between Objective-C and Python method names.
"""

import pytest
from glyphs_info_mcp.modules.glyphs_api.objc_api.pyobjc_converter import PyObjCConverter


class TestObjCToPython:
    """Test Objective-C → Python conversion"""

    def test_no_parameter_method(self) -> None:
        """Test no-parameter method"""
        assert PyObjCConverter.objc_to_python("title") == "title"
        assert PyObjCConverter.objc_to_python("interfaceVersion") == "interfaceVersion"

    def test_single_parameter_method(self) -> None:
        """Test single-parameter method"""
        result = PyObjCConverter.objc_to_python("setValue:(id)value")
        assert result == "setValue_"

    def test_multiple_parameters_method(self) -> None:
        """Test multi-parameter method"""
        signature = "doSomething:(id)arg withOther:(id)other"
        result = PyObjCConverter.objc_to_python(signature)
        assert result == "doSomething_withOther_"

    def test_full_signature_with_return_type(self) -> None:
        """Test full signature with return type"""
        signature = "- (void)drawForegroundForLayer:(GSLayer *)layer"
        result = PyObjCConverter.objc_to_python(signature)
        assert result == "drawForegroundForLayer_"

    def test_full_signature_multiple_params(self) -> None:
        """Test full signature with multiple parameters"""
        signature = "- (void)drawForegroundForLayer:(GSLayer *)layer options:(NSDictionary *)options"
        result = PyObjCConverter.objc_to_python(signature)
        assert result == "drawForegroundForLayer_options_"

    def test_class_method(self) -> None:
        """Test class method (+ symbol)"""
        signature = "+ (instancetype)alloc"
        result = PyObjCConverter.objc_to_python(signature)
        assert result == "alloc"

    def test_instance_method(self) -> None:
        """Test instance method (- symbol)"""
        signature = "- (NSUInteger)interfaceVersion"
        result = PyObjCConverter.objc_to_python(signature)
        assert result == "interfaceVersion"

    def test_method_with_attributes(self) -> None:
        """Test method with __attribute__"""
        signature = "- (void)dealloc __attribute__((deprecated))"
        result = PyObjCConverter.objc_to_python(signature)
        assert result == "dealloc"

    def test_glyphs_reporter_method(self) -> None:
        """Test Glyphs Reporter Protocol method"""
        signature = "- (void)drawBackgroundForLayer:(GSLayer *)layer"
        result = PyObjCConverter.objc_to_python(signature)
        assert result == "drawBackgroundForLayer_"

    def test_method_with_semicolon(self) -> None:
        """Test method signature with semicolon"""
        signature = "- (NSUInteger)interfaceVersion;"
        result = PyObjCConverter.objc_to_python(signature)
        assert result == "interfaceVersion"


class TestPythonToObjC:
    """Test Python → Objective-C conversion"""

    def test_no_parameter_method(self) -> None:
        """Test no-parameter method"""
        assert PyObjCConverter.python_to_objc("title") == "title"
        assert PyObjCConverter.python_to_objc("interfaceVersion") == "interfaceVersion"

    def test_single_parameter_method(self) -> None:
        """Test single-parameter method"""
        result = PyObjCConverter.python_to_objc("setValue_")
        assert result == "setValue:"

    def test_multiple_parameters_method(self) -> None:
        """Test multi-parameter method"""
        result = PyObjCConverter.python_to_objc("doSomething_withOther_")
        assert result == "doSomething:withOther:"

    def test_with_param_count_validation(self) -> None:
        """Test parameter count validation"""
        result = PyObjCConverter.python_to_objc("doSomething_withOther_", param_count=2)
        assert result == "doSomething:withOther:"

    def test_param_count_mismatch(self) -> None:
        """Test error thrown when parameter count mismatch"""
        with pytest.raises(ValueError, match="Parameter count mismatch"):
            PyObjCConverter.python_to_objc("doSomething_withOther_", param_count=3)

    def test_trailing_underscores_removal(self) -> None:
        """Test removing trailing underscores"""
        # Multiple trailing underscores should all be removed
        result = PyObjCConverter.python_to_objc("setValue___")
        assert result == "setValue:"


class TestExtractMethodName:
    """Test method name extraction"""

    def test_extract_no_param_method(self) -> None:
        """Test extracting no-parameter method name"""
        signature = "- (NSUInteger)interfaceVersion;"
        result = PyObjCConverter.extract_method_name(signature)
        assert result == "interfaceVersion"

    def test_extract_single_param_method(self) -> None:
        """Test extracting single-parameter method name"""
        signature = "- (void)setValue:(id)value;"
        result = PyObjCConverter.extract_method_name(signature)
        assert result == "setValue:"

    def test_extract_multiple_params_method(self) -> None:
        """Test extracting multi-parameter method name"""
        signature = "- (void)drawForegroundForLayer:(GSLayer *)layer options:(NSDictionary *)options;"
        result = PyObjCConverter.extract_method_name(signature)
        assert result == "drawForegroundForLayer:options:"

    def test_extract_with_attributes(self) -> None:
        """Test extracting method name from signature with __attribute__"""
        signature = "- (void)dealloc __attribute__((deprecated));"
        result = PyObjCConverter.extract_method_name(signature)
        assert result == "dealloc"

    def test_extract_class_method(self) -> None:
        """Test extracting class method name"""
        signature = "+ (instancetype)alloc;"
        result = PyObjCConverter.extract_method_name(signature)
        assert result == "alloc"

    def test_extract_without_semicolon(self) -> None:
        """Test signature without semicolon"""
        signature = "- (void)drawBackgroundForLayer:(GSLayer *)layer"
        result = PyObjCConverter.extract_method_name(signature)
        assert result == "drawBackgroundForLayer:"


class TestIsValidPythonName:
    """Test Python method name validation"""

    def test_valid_simple_name(self) -> None:
        """Test valid simple name"""
        assert PyObjCConverter.is_valid_python_name("title") is True
        assert PyObjCConverter.is_valid_python_name("interfaceVersion") is True

    def test_valid_name_with_underscores(self) -> None:
        """Test valid name with underscores"""
        assert PyObjCConverter.is_valid_python_name("setValue_") is True
        assert PyObjCConverter.is_valid_python_name("doSomething_withOther_") is True

    def test_valid_name_starting_with_underscore(self) -> None:
        """Test valid name starting with underscore"""
        assert PyObjCConverter.is_valid_python_name("_private_method") is True
        assert PyObjCConverter.is_valid_python_name("__init__") is True

    def test_invalid_empty_name(self) -> None:
        """Test invalid empty name"""
        assert PyObjCConverter.is_valid_python_name("") is False

    def test_invalid_name_with_spaces(self) -> None:
        """Test invalid name with spaces"""
        assert PyObjCConverter.is_valid_python_name("do something") is False

    def test_invalid_name_with_special_chars(self) -> None:
        """Test invalid name with special characters"""
        assert PyObjCConverter.is_valid_python_name("do-something") is False
        assert PyObjCConverter.is_valid_python_name("do.something") is False
        assert PyObjCConverter.is_valid_python_name("do:something") is False

    def test_invalid_name_starting_with_number(self) -> None:
        """Test invalid name starting with number"""
        assert PyObjCConverter.is_valid_python_name("1method") is False


class TestFormatFullSignature:
    """Test full signature formatting"""

    def test_format_no_param_instance_method(self) -> None:
        """Test formatting no-parameter instance method"""
        result = PyObjCConverter.format_full_signature(
            method_name="interfaceVersion",
            parameters=[],
            return_type="NSUInteger",
            method_type="instance"
        )
        assert result == "- (NSUInteger)interfaceVersion"

    def test_format_single_param_instance_method(self) -> None:
        """Test formatting single-parameter instance method"""
        result = PyObjCConverter.format_full_signature(
            method_name="setValue:",
            parameters=[("id", "value")],
            return_type="void",
            method_type="instance"
        )
        assert result == "- (void)setValue:(id)value"

    def test_format_multiple_params_instance_method(self) -> None:
        """Test formatting multi-parameter instance method"""
        result = PyObjCConverter.format_full_signature(
            method_name="drawForegroundForLayer:options:",
            parameters=[
                ("GSLayer *", "layer"),
                ("NSDictionary *", "options")
            ],
            return_type="void",
            method_type="instance"
        )
        expected = "- (void)drawForegroundForLayer:(GSLayer *)layer options:(NSDictionary *)options"
        assert result == expected

    def test_format_class_method(self) -> None:
        """Test formatting class method"""
        result = PyObjCConverter.format_full_signature(
            method_name="alloc",
            parameters=[],
            return_type="instancetype",
            method_type="class"
        )
        assert result == "+ (instancetype)alloc"

    def test_format_param_count_mismatch(self) -> None:
        """Test error thrown when parameter count mismatch"""
        with pytest.raises(ValueError, match="Method name parts.*doesn't match parameter count"):
            PyObjCConverter.format_full_signature(
                method_name="doSomething:withOther:",
                parameters=[("id", "arg")],  # Only 1 parameter but method requires 2
                return_type="void"
            )


class TestRoundTripConversion:
    """Test round-trip conversion consistency"""

    def test_roundtrip_no_param(self) -> None:
        """Test round-trip conversion for no-parameter method"""
        objc_name = "title"
        python_name = PyObjCConverter.objc_to_python(objc_name)
        back_to_objc = PyObjCConverter.python_to_objc(python_name)
        assert back_to_objc == objc_name

    def test_roundtrip_single_param(self) -> None:
        """Test round-trip conversion for single-parameter method"""
        objc_name = "setValue:"
        python_name = PyObjCConverter.objc_to_python(f"setValue:(id)value")
        back_to_objc = PyObjCConverter.python_to_objc(python_name)
        assert back_to_objc == objc_name

    def test_roundtrip_multiple_params(self) -> None:
        """Test round-trip conversion for multi-parameter method"""
        objc_name = "doSomething:withOther:"
        python_name = PyObjCConverter.objc_to_python("doSomething:(id)arg withOther:(id)other")
        back_to_objc = PyObjCConverter.python_to_objc(python_name)
        assert back_to_objc == objc_name

    def test_roundtrip_glyphs_method(self) -> None:
        """Test round-trip conversion for Glyphs method"""
        objc_signature = "- (void)drawForegroundForLayer:(GSLayer *)layer options:(NSDictionary *)options"

        # ObjC → Python
        python_name = PyObjCConverter.objc_to_python(objc_signature)
        assert python_name == "drawForegroundForLayer_options_"

        # Python → ObjC (basic form)
        back_to_objc = PyObjCConverter.python_to_objc(python_name)
        assert back_to_objc == "drawForegroundForLayer:options:"

        # Extracted method name should be consistent
        extracted = PyObjCConverter.extract_method_name(objc_signature)
        assert extracted == back_to_objc


class TestRealWorldExamples:
    """Test real-world Glyphs API examples"""

    def test_reporter_protocol_methods(self) -> None:
        """Test GlyphsReporterProtocol methods"""
        methods = [
            ("- (void)drawBackgroundForLayer:(GSLayer *)layer", "drawBackgroundForLayer_"),
            ("- (void)drawForegroundForLayer:(GSLayer *)layer", "drawForegroundForLayer_"),
            ("- (void)drawBackgroundForInactiveLayer:(GSLayer *)layer", "drawBackgroundForInactiveLayer_"),
        ]

        for objc_sig, expected_python in methods:
            result = PyObjCConverter.objc_to_python(objc_sig)
            assert result == expected_python

    def test_filter_protocol_methods(self) -> None:
        """Test GlyphsFilterProtocol methods"""
        signature = "- (NSString *)filter:(GSLayer *)layer inFont:(GSFont *)font withArguments:(NSArray *)args error:(NSError **)error"
        result = PyObjCConverter.objc_to_python(signature)
        assert result == "filter_inFont_withArguments_error_"

    def test_palette_protocol_methods(self) -> None:
        """Test GlyphsPaletteProtocol methods"""
        methods = [
            ("- (CGFloat)minSize", "minSize"),
            ("- (CGFloat)maxSize", "maxSize"),
            ("- (NSView *)paletteView", "paletteView"),
        ]

        for objc_sig, expected_python in methods:
            result = PyObjCConverter.objc_to_python(objc_sig)
            assert result == expected_python
