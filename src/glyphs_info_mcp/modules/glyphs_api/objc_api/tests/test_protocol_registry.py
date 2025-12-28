"""
Protocol Registry Test Suite

Tests dynamic loading and caching of Protocol methods.
"""

import pytest
from pathlib import Path
from glyphs_info_mcp.modules.glyphs_api.objc_api.protocol_registry import ProtocolRegistry
from glyphs_info_mcp.modules.glyphs_api.objc_api.glyphs_sdk_mapper import MethodType


@pytest.fixture
def headers_path() -> Path:
    """Headers file path"""
    return Path("/Applications/Glyphs 3.app/Contents/Frameworks/GlyphsCore.framework/Versions/A/Headers")


@pytest.fixture
def registry(headers_path: Path) -> ProtocolRegistry:
    """Create ProtocolRegistry instance for testing"""
    if not headers_path.exists():
        pytest.skip("Glyphs 3 not installed")
    return ProtocolRegistry(headers_path)


class TestProtocolLoading:
    """Test Protocol loading functionality"""

    def test_load_glyphs_reporter_protocol(self, registry: ProtocolRegistry) -> None:
        """Test loading GlyphsReporter Protocol"""
        methods = registry.get_protocol_methods("GlyphsReporter")

        # Should include all required and optional methods
        assert len(methods) > 0
        assert "interfaceVersion" in methods
        assert "title" in methods

    def test_load_protocol_includes_optional_methods(self, registry: ProtocolRegistry) -> None:
        """Test loading includes optional methods"""
        methods = registry.get_protocol_methods("GlyphsReporter")

        # Check some key optional methods
        assert "drawForegroundForLayer_options_" in methods
        assert "drawBackgroundForLayer_options_" in methods
        assert "addMenuItemsForEvent_toMenu_" in methods

    def test_load_protocol_filters_deprecated_methods(self, registry: ProtocolRegistry) -> None:
        """Test filtering deprecated methods"""
        methods = registry.get_protocol_methods("GlyphsReporter")

        # Deprecated methods should not be included
        # These methods are marked with __attribute__((unavailable)) in Protocol
        deprecated_methods = {
            "drawBackgroundForLayer_",
            "drawForegroundForLayer_",
            "drawBackgroundForInactiveLayer_"
        }

        for method in deprecated_methods:
            assert method not in methods, f"Deprecated method {method} should not be included"

    def test_load_nonexistent_protocol(self, registry: ProtocolRegistry) -> None:
        """Test loading nonexistent Protocol"""
        methods = registry.get_protocol_methods("NonexistentProtocol")

        # Should return empty set
        assert methods == set()


class TestPyObjCConversion:
    """Test PyObjC naming conversion"""

    def test_convert_no_param_methods(self, registry: ProtocolRegistry) -> None:
        """Test no-parameter method conversion"""
        methods = registry.get_protocol_methods("GlyphsReporter")

        # No-parameter methods should keep original name
        assert "interfaceVersion" in methods
        assert "title" in methods
        assert "willActivate" in methods

    def test_convert_single_param_methods(self, registry: ProtocolRegistry) -> None:
        """Test single-parameter method conversion"""
        methods = registry.get_protocol_methods("GlyphsReporter")

        # Single-parameter methods should have one trailing underscore
        assert "drawBackgroundWithOptions_" in methods
        assert "drawForegroundWithOptions_" in methods
        assert "shouldDrawAccentCloudForLayer_" in methods

    def test_convert_multi_param_methods(self, registry: ProtocolRegistry) -> None:
        """Test multi-parameter method conversion"""
        methods = registry.get_protocol_methods("GlyphsReporter")

        # Multi-parameter methods should convert colons to underscores
        assert "drawForegroundForLayer_options_" in methods
        assert "addMenuItemsForEvent_toMenu_" in methods
        assert "addMenuItemsForEvent_controller_toMenu_" in methods


class TestCacheMechanism:
    """Test cache mechanism"""

    def test_cache_protocol_methods(self, registry: ProtocolRegistry) -> None:
        """Test Protocol methods are cached"""
        # First load
        methods1 = registry.get_protocol_methods("GlyphsReporter")

        # Second load (should get from cache)
        methods2 = registry.get_protocol_methods("GlyphsReporter")

        # Should be the same set
        assert methods1 == methods2

        # Should be the same object (cache hit)
        assert methods1 is methods2

    def test_cache_different_protocols(self, registry: ProtocolRegistry) -> None:
        """Test different Protocols are cached separately"""
        # Load two different Protocols (if they exist)
        methods1 = registry.get_protocol_methods("GlyphsReporter")
        methods2 = registry.get_protocol_methods("FilterPlugin")

        # Should be different sets
        assert methods1 != methods2


class TestValidationTools:
    """Test validation tools"""

    def test_validate_against_manual_list(self, registry: ProtocolRegistry) -> None:
        """Test validating against manual list"""
        # Simulate manual list (incomplete)
        manual_set = {
            "interfaceVersion",
            "title",
            "drawForegroundForLayer_options_",
            "drawBackgroundForLayer_options_",
        }

        result = registry.validate_against_manual_list("GlyphsReporter", manual_set)

        # Should return difference report
        assert "missing_in_manual" in result
        assert "extra_in_manual" in result
        assert "match_rate" in result

        # Should have missing methods
        assert len(result["missing_in_manual"]) > 0

    def test_validate_complete_manual_list(self, registry: ProtocolRegistry) -> None:
        """Test validating complete manual list"""
        # Use auto-loaded methods as manual list
        auto_methods = registry.get_protocol_methods("GlyphsReporter")

        result = registry.validate_against_manual_list("GlyphsReporter", auto_methods)

        # Should match completely
        assert len(result["missing_in_manual"]) == 0
        assert len(result["extra_in_manual"]) == 0
        assert result["match_rate"] == 1.0


class TestMethodLookup:
    """Test method lookup functionality"""

    def test_get_method_info(self, registry: ProtocolRegistry) -> None:
        """Test getting method detailed information"""
        method_info = registry.get_method_info("GlyphsReporter", "drawForegroundForLayer_options_")

        # Should return method info
        assert method_info is not None
        assert "name" in method_info
        assert "parameters" in method_info
        assert "return_type" in method_info

    def test_get_method_info_nonexistent(self, registry: ProtocolRegistry) -> None:
        """Test getting nonexistent method"""
        method_info = registry.get_method_info("GlyphsReporter", "nonexistentMethod")

        # Should return None
        assert method_info is None

    def test_is_protocol_method(self, registry: ProtocolRegistry) -> None:
        """Test determining if it's a Protocol method"""
        assert registry.is_protocol_method("GlyphsReporter", "interfaceVersion") is True
        assert registry.is_protocol_method("GlyphsReporter", "drawForegroundForLayer_options_") is True
        assert registry.is_protocol_method("GlyphsReporter", "unknownMethod") is False


class TestRealWorldCoverage:
    """Test real-world coverage"""

    def test_coverage_completeness(self, registry: ProtocolRegistry) -> None:
        """Test coverage completeness"""
        methods = registry.get_protocol_methods("GlyphsReporter")

        # Based on actual Protocol definition, should have 23 active methods (excluding 3 deprecated)
        # This is 3 more than the manual list (20)
        assert len(methods) >= 23

    def test_includes_missing_methods_from_manual_list(self, registry: ProtocolRegistry) -> None:
        """Test includes 9 methods missing from manual list"""
        methods = registry.get_protocol_methods("GlyphsReporter")

        # Check methods missing from manual list
        missing_methods = {
            "drawBackgroundWithOptions_",
            "drawForegroundWithOptions_",
            "needsExtraMainOutlineDrawingForActiveLayer_",
            "needsExtraMainOutlineDrawingInPreviewLayer_",
            "shouldDrawAccentCloudForLayer_",
            "drawFontViewBackgroundForLayer_inFrame_",
            "drawFontViewForegroundForLayer_inFrame_",
            "viewWillDraw",
        }

        found_count = sum(1 for method in missing_methods if method in methods)

        # Should find most of the missing methods
        assert found_count >= 6, f"Only found {found_count} missing methods, expected at least 6"
