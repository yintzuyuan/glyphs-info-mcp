#!/usr/bin/env python3
"""
Tests for MCP Resources Integration

Issue #33: Test setup_resources() function and resource registration
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path


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

        modules = {"test_module": mock_module}

        # Execute
        setup_resources(mock_mcp, modules)

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

        modules = {"test_module": mock_module}

        # Execute (should not raise error)
        setup_resources(mock_mcp, modules)

        # Verify no registration occurred
        mock_mcp.resource.assert_not_called()

    def test_setup_resources_with_empty_resources(self) -> None:
        """Test setup_resources handles modules that return empty resources"""
        from glyphs_info_mcp.server import setup_resources

        mock_mcp = MagicMock()
        mock_module = MagicMock()
        mock_module.get_resources.return_value = {}

        modules = {"test_module": mock_module}

        # Execute
        setup_resources(mock_mcp, modules)

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

        modules = {
            "failing_module": mock_module1,
            "working_module": mock_module2,
        }

        # Execute (should not raise error)
        setup_resources(mock_mcp, modules)

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

        modules = {
            "module1": mock_module1,
            "module2": mock_module2,
        }

        # Execute
        setup_resources(mock_mcp, modules)

        # Verify total registrations
        assert mock_mcp.resource.call_count == 3
        mock_mcp.resource.assert_any_call("glyphs://module1/resource1")
        mock_mcp.resource.assert_any_call("glyphs://module1/resource2")
        mock_mcp.resource.assert_any_call("glyphs://module2/resource1")
