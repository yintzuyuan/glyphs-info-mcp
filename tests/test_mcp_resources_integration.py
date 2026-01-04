#!/usr/bin/env python3
"""
Tests for MCP Resources Integration

Issue #33: Test setup_resources() function and resource registration
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from typing import Any


class TestSetupResources:
    """Test setup_resources() function from server.py"""

    def test_setup_resources_with_valid_module(self) -> None:
        """Test resource registration with module that provides resources"""
        from glyphs_info_mcp.server import setup_resources

        # Mock FastMCP instance
        mock_mcp = MagicMock()
        mock_resource_decorator = MagicMock()
        mock_mcp.resource.return_value = mock_resource_decorator

        # Mock module with get_resources()
        mock_module = MagicMock()
        mock_resource_func = MagicMock()
        mock_module.get_resources.return_value = {
            "glyphs://test/resource1": mock_resource_func,
            "glyphs://test/resource2": mock_resource_func,
        }

        modules: dict[str, Any] = {"test_module": mock_module}

        # Execute
        setup_resources(mock_mcp, modules)  # type: ignore[arg-type]

        # Verify resource registration
        assert mock_mcp.resource.call_count == 2
        mock_mcp.resource.assert_any_call("glyphs://test/resource1")
        mock_mcp.resource.assert_any_call("glyphs://test/resource2")

        # Verify decorator was called with resource functions
        assert mock_resource_decorator.call_count == 2

    def test_setup_resources_with_module_without_get_resources(self) -> None:
        """Test setup_resources skips modules without get_resources method"""
        from glyphs_info_mcp.server import setup_resources

        mock_mcp = MagicMock()
        mock_module = MagicMock(spec=[])  # No get_resources method

        modules: dict[str, Any] = {"test_module": mock_module}

        # Execute (should not raise error)
        setup_resources(mock_mcp, modules)  # type: ignore

        # Verify no registration occurred
        mock_mcp.resource.assert_not_called()

    def test_setup_resources_with_empty_resources(self) -> None:
        """Test setup_resources handles modules that return empty resources"""
        from glyphs_info_mcp.server import setup_resources

        mock_mcp = MagicMock()
        mock_module = MagicMock()
        mock_module.get_resources.return_value = {}

        modules: dict[str, Any] = {"test_module": mock_module}

        # Execute
        setup_resources(mock_mcp, modules)  # type: ignore[arg-type]

        # Verify no registration occurred
        mock_mcp.resource.assert_not_called()

    def test_setup_resources_error_isolation(self) -> None:
        """Test setup_resources isolates errors from individual modules"""
        from glyphs_info_mcp.server import setup_resources

        mock_mcp = MagicMock()

        # Module 1: Raises error
        mock_module1 = MagicMock()
        mock_module1.get_resources.side_effect = RuntimeError("Test error")

        # Module 2: Works correctly
        mock_module2 = MagicMock()
        mock_resource_func = MagicMock()
        mock_module2.get_resources.return_value = {
            "glyphs://test/resource": mock_resource_func
        }

        modules: dict[str, Any] = {
            "failing_module": mock_module1,
            "working_module": mock_module2,
        }

        # Execute (should not raise error)
        setup_resources(mock_mcp, modules)  # type: ignore[arg-type]

        # Verify working module's resources were registered
        mock_mcp.resource.assert_called_once_with("glyphs://test/resource")

    def test_setup_resources_with_multiple_modules(self) -> None:
        """Test setup_resources with multiple modules providing resources"""
        from glyphs_info_mcp.server import setup_resources

        mock_mcp = MagicMock()
        mock_resource_decorator = MagicMock()
        mock_mcp.resource.return_value = mock_resource_decorator

        # Module 1
        mock_module1 = MagicMock()
        mock_module1.get_resources.return_value = {
            "glyphs://module1/resource1": MagicMock(),
            "glyphs://module1/resource2": MagicMock(),
        }

        # Module 2
        mock_module2 = MagicMock()
        mock_module2.get_resources.return_value = {
            "glyphs://module2/resource1": MagicMock(),
        }

        modules: dict[str, Any] = {
            "module1": mock_module1,
            "module2": mock_module2,
        }

        # Execute
        setup_resources(mock_mcp, modules)  # type: ignore[arg-type]

        # Verify total registrations
        assert mock_mcp.resource.call_count == 3
        mock_mcp.resource.assert_any_call("glyphs://module1/resource1")
        mock_mcp.resource.assert_any_call("glyphs://module1/resource2")
        mock_mcp.resource.assert_any_call("glyphs://module2/resource1")


@pytest.mark.skip(reason="Outdated test - create_mcp_server API no longer exists")
@pytest.mark.requires_glyphs_app
def test_xcode_templates_resources_registered() -> None:
    """Test that Xcode templates are registered as MCP resources (Issue #34)"""
    from glyphs_info_mcp.server import create_mcp_server  # type: ignore[attr-defined]
    from glyphs_info_mcp.config import get_sdk_path

    # Create server instance
    server = create_mcp_server()

    # Get resources from glyphs_sdk module
    sdk_module = server._modules.get("glyphs_sdk")  # type: ignore[attr-defined]
    if not sdk_module or not hasattr(sdk_module, "get_resources"):
        pytest.skip("SDK module not available or doesn't support resources")

    resources = sdk_module.get_resources()

    # Should have 7 Xcode template resources
    xcode_template_uris = [
        uri for uri in resources.keys() if uri.startswith("glyphs://xcode-template/")
    ]
    assert len(xcode_template_uris) == 7

    # Check specific templates
    expected_templates = [
        "glyphs://xcode-template/reporter",
        "glyphs://xcode-template/filter",
        "glyphs://xcode-template/palette",
        "glyphs://xcode-template/tool",
        "glyphs://xcode-template/file_format",
        "glyphs://xcode-template/plugin",
        "glyphs://xcode-template/plugin_base",
    ]

    for uri in expected_templates:
        assert uri in resources, f"Missing Xcode template resource: {uri}"


@pytest.mark.skip(reason="Outdated test - create_mcp_server API no longer exists")
@pytest.mark.requires_glyphs_app
def test_xcode_template_resource_content() -> None:
    """Test Xcode template resource content format (Issue #34)"""
    from glyphs_info_mcp.server import create_mcp_server  # type: ignore[attr-defined]

    # Create server instance
    server = create_mcp_server()

    # Get resources from glyphs_sdk module
    sdk_module = server._modules.get("glyphs_sdk")  # type: ignore[attr-defined]
    if not sdk_module or not hasattr(sdk_module, "get_resources"):
        pytest.skip("SDK module not available or doesn't support resources")

    resources = sdk_module.get_resources()

    # Get a specific template resource
    reporter_uri = "glyphs://xcode-template/reporter"
    assert reporter_uri in resources

    # Execute resource handler
    handler = resources[reporter_uri]
    content = handler()

    # Check content format
    assert isinstance(content, str)
    assert "Glyphs Reporter" in content or "Reporter" in content
    assert "```objective-c" in content  # Should have Obj-C code blocks
    assert (
        "___PACKAGENAMEASIDENTIFIER___" in content
    )  # Should have Xcode placeholders


class TestSamplesResourcesIntegration:
    """Test Python and Xcode Samples MCP resources integration (Issue #37)"""

    @pytest.fixture
    def sdk_module(self) -> Any:
        """Get initialized GlyphsSDKModule"""
        from glyphs_info_mcp.modules.glyphs_sdk.glyphs_sdk_module import (
            GlyphsSDKModule,
        )

        module = GlyphsSDKModule()
        success = module.initialize()
        if not success:
            pytest.skip("SDK module initialization failed")

        return module

    def test_python_samples_resources_registered(self, sdk_module: Any) -> None:
        """Test that Python samples are registered as MCP resources"""
        resources = sdk_module.get_resources()

        # Should have 6 Python sample resources
        python_sample_uris = [
            uri
            for uri in resources.keys()
            if uri.startswith("glyphs://python-sample/")
        ]
        assert len(python_sample_uris) == 6

        # Check specific samples
        expected_samples = [
            "glyphs://python-sample/callback_for_context_menu",
            "glyphs://python-sample/document_exported",
            "glyphs://python-sample/multipletools",
            "glyphs://python-sample/plugin_preferences",
            "glyphs://python-sample/plugin_with_window",
            "glyphs://python-sample/smiley_panel_plugin",
        ]

        for uri in expected_samples:
            assert uri in resources, f"Missing Python sample resource: {uri}"

    def test_xcode_samples_resources_registered(self, sdk_module: Any) -> None:
        """Test that Xcode samples are registered as MCP resources"""
        resources = sdk_module.get_resources()

        # Should have 4 Xcode sample resources
        xcode_sample_uris = [
            uri
            for uri in resources.keys()
            if uri.startswith("glyphs://xcode-sample/")
        ]
        assert len(xcode_sample_uris) == 4

        # Check specific samples
        expected_samples = [
            "glyphs://xcode-sample/custom_parameter_ui",
            "glyphs://xcode-sample/inspector_demo",
            "glyphs://xcode-sample/photofont",
            "glyphs://xcode-sample/plugin_with_window",
        ]

        for uri in expected_samples:
            assert uri in resources, f"Missing Xcode sample resource: {uri}"

    def test_total_resources_count(self, sdk_module: Any) -> None:
        """Test total resource count includes all templates and samples"""
        resources = sdk_module.get_resources()

        # Count resources by type
        python_templates = sum(
            1 for uri in resources if uri.startswith("glyphs://plugin-template/")
        )
        xcode_templates = sum(
            1 for uri in resources if uri.startswith("glyphs://xcode-template/")
        )
        python_samples = sum(
            1 for uri in resources if uri.startswith("glyphs://python-sample/")
        )
        xcode_samples = sum(
            1 for uri in resources if uri.startswith("glyphs://xcode-sample/")
        )

        # Should have 26 total resources
        # 9 Python Templates + 7 Xcode Templates + 6 Python Samples + 4 Xcode Samples
        assert python_templates == 9
        assert xcode_templates == 7
        assert python_samples == 6
        assert xcode_samples == 4
        assert len(resources) == 26

    def test_python_sample_resource_content(self, sdk_module: Any) -> None:
        """Test Python sample resource content format"""
        resources = sdk_module.get_resources()

        # Get a specific sample resource
        sample_uri = "glyphs://python-sample/callback_for_context_menu"
        assert sample_uri in resources

        # Execute resource handler
        handler = resources[sample_uri]
        content = handler()

        # Check content format
        assert isinstance(content, str)
        assert "Callback for context menu" in content
        assert "```python" in content  # Should have Python code blocks
        assert "**Type**:" in content  # Should have metadata
        assert "**Has Bundle**:" in content
        assert "## File Structure" in content
        assert "**MCP Resource**:" in content

    def test_xcode_sample_resource_content(self, sdk_module: Any) -> None:
        """Test Xcode sample resource content format"""
        resources = sdk_module.get_resources()

        # Get a specific sample resource
        sample_uri = "glyphs://xcode-sample/inspector_demo"
        assert sample_uri in resources

        # Execute resource handler
        handler = resources[sample_uri]
        content = handler()

        # Check content format
        assert isinstance(content, str)
        assert "InspectorDemo" in content
        assert "```objective-c" in content  # Should have Obj-C code blocks
        assert "**Xcode Project**:" in content  # Should have metadata
        assert "## File Structure" in content
        assert "**MCP Resource**:" in content

    def test_closure_factory_captures_correct_ids(self, sdk_module: Any) -> None:
        """Test that closure factory correctly captures different sample IDs"""
        resources = sdk_module.get_resources()

        # Get multiple Python sample handlers
        sample1_handler = resources["glyphs://python-sample/callback_for_context_menu"]
        sample2_handler = resources["glyphs://python-sample/plugin_with_window"]

        # Execute handlers
        content1 = sample1_handler()
        content2 = sample2_handler()

        # Verify they return different content
        assert content1 != content2
        assert "callback_for_context_menu" in content1
        assert "Plugin With Window" in content2
        assert "callback_for_context_menu" not in content2
        assert "Plugin With Window" not in content1

    def test_resource_handler_error_handling(self, sdk_module: Any) -> None:
        """Test resource handler error handling for invalid sample IDs"""
        # This tests the internal error handling in resource handlers
        # We can't directly access _get_python_sample_resource, but we can
        # verify the behavior through the public API

        resources = sdk_module.get_resources()

        # All registered resources should have valid handlers
        for uri, handler in resources.items():
            if uri.startswith("glyphs://python-sample/") or uri.startswith(
                "glyphs://xcode-sample/"
            ):
                content = handler()
                assert isinstance(content, str)
                # Should not return error message for valid resources
                assert not content.startswith("❌")
