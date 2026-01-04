"""Tests for Python Samples tool layer (Issue #38)

Tests for _list_python_samples_tool() and _get_python_sample_tool()
following the Xcode Samples pattern.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock

from glyphs_info_mcp.modules.glyphs_sdk.glyphs_sdk_module import GlyphsSDKModule
from glyphs_info_mcp.shared.core.sdk_native_accessor import SDKNativeAccessor


@pytest.fixture
def sdk_path() -> Path:
    """Get GlyphsSDK path"""
    project_root = Path(__file__).parent.parent.parent
    return (
        project_root / "src" / "glyphs_info_mcp" / "data" / "official" / "GlyphsSDK"
    )


@pytest.fixture
def native_accessor(sdk_path: Path) -> SDKNativeAccessor:
    """Create SDKNativeAccessor instance"""
    return SDKNativeAccessor(sdk_path)


@pytest.fixture
def sdk_module() -> GlyphsSDKModule:
    """Create GlyphsSDKModule instance and initialize it"""
    module = GlyphsSDKModule()
    module.initialize()
    return module


class TestListPythonSamplesTool:
    """Tests for _list_python_samples_tool()"""

    def test_returns_markdown_format(self, sdk_module: GlyphsSDKModule) -> None:
        """Test that result is formatted as Markdown"""
        result = sdk_module._list_python_samples_tool()

        assert result.startswith("## ")
        assert "Python Sample" in result

    def test_shows_sample_count(self, sdk_module: GlyphsSDKModule) -> None:
        """Test that result shows sample count"""
        result = sdk_module._list_python_samples_tool()

        # Should mention the count of samples found
        assert "6" in result or "Found" in result

    def test_shows_sample_info(self, sdk_module: GlyphsSDKModule) -> None:
        """Test that result shows sample information"""
        result = sdk_module._list_python_samples_tool()

        # Should show sample names
        assert "Callback for context menu" in result or "context menu" in result.lower()

        # Should show type information
        assert "Type" in result or "type" in result

        # Should show source file count
        assert "Source" in result or "files" in result.lower()

    def test_shows_usage_tips(self, sdk_module: GlyphsSDKModule) -> None:
        """Test that result includes usage tips"""
        result = sdk_module._list_python_samples_tool()

        assert "tip" in result.lower() or "usage" in result.lower()

    def test_handles_no_native_accessor(self) -> None:
        """Test error handling when native accessor not initialized"""
        module = GlyphsSDKModule.__new__(GlyphsSDKModule)
        module.native_accessor = None

        result = module._list_python_samples_tool()

        assert "not initialized" in result.lower() or "error" in result.lower()


class TestGetPythonSampleTool:
    """Tests for _get_python_sample_tool()"""

    def test_returns_sample_content(self, sdk_module: GlyphsSDKModule) -> None:
        """Test that result contains sample content"""
        result = sdk_module._get_python_sample_tool("Callback for context menu")

        assert "Callback for context menu" in result
        assert "Source" in result or "code" in result.lower()

    def test_shows_sample_type(self, sdk_module: GlyphsSDKModule) -> None:
        """Test that result shows sample type"""
        result = sdk_module._get_python_sample_tool("Callback for context menu")

        assert "Type" in result or "type" in result

    def test_shows_source_code(self, sdk_module: GlyphsSDKModule) -> None:
        """Test that result includes source code blocks"""
        result = sdk_module._get_python_sample_tool("Callback for context menu")

        # Should contain Python code blocks
        assert "```python" in result or "```" in result

    def test_shows_file_structure(self, sdk_module: GlyphsSDKModule) -> None:
        """Test that result shows file structure"""
        result = sdk_module._get_python_sample_tool("Callback for context menu")

        assert "File" in result and ".py" in result

    def test_not_found_lists_available(self, sdk_module: GlyphsSDKModule) -> None:
        """Test that not found returns available samples list"""
        result = sdk_module._get_python_sample_tool("NonExistentSample")

        assert "not found" in result.lower() or "available" in result.lower()
        # Should list some available samples
        assert "Callback" in result or "Plugin" in result

    def test_empty_name_error(self, sdk_module: GlyphsSDKModule) -> None:
        """Test error handling for empty sample name"""
        result = sdk_module._get_python_sample_tool("")

        assert "provide" in result.lower() or "name" in result.lower()

    def test_handles_no_native_accessor(self) -> None:
        """Test error handling when native accessor not initialized"""
        module = GlyphsSDKModule.__new__(GlyphsSDKModule)
        module.native_accessor = None

        result = module._get_python_sample_tool("test")

        assert "not initialized" in result.lower() or "error" in result.lower()


class TestUnifiedToolsIntegration:
    """Tests for unified tools integration (Issue #38)"""

    def test_sdk_list_python_samples_action(self) -> None:
        """Test sdk router dispatches list_python_samples action correctly"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        mock_module = MagicMock()
        mock_module._list_python_samples_tool.return_value = "sample list"

        router = UnifiedToolsRouter()
        router.set_module("glyphs_sdk", mock_module)

        result = router.sdk(action="list_python_samples")

        mock_module._list_python_samples_tool.assert_called_once()
        assert result == "sample list"

    def test_sdk_get_python_sample_action(self) -> None:
        """Test sdk router dispatches get_python_sample action correctly"""
        from glyphs_info_mcp.unified_tools import UnifiedToolsRouter

        mock_module = MagicMock()
        mock_module._get_python_sample_tool.return_value = "sample details"

        router = UnifiedToolsRouter()
        router.set_module("glyphs_sdk", mock_module)

        result = router.sdk(action="get_python_sample", sample_name="Plugin With Window")

        mock_module._get_python_sample_tool.assert_called_once_with(
            sample_name="Plugin With Window"
        )
        assert result == "sample details"
