#!/usr/bin/env python3
"""
Tests for GlyphsSDKModule Resource System

Issue #33: Test get_resources() and Python template tools
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from typing import Any


class TestGlyphsSDKModuleResources:
    """Test GlyphsSDKModule.get_resources() implementation"""

    @pytest.fixture
    def mock_sdk_module(self) -> tuple[Any, MagicMock]:
        """Create mock SDK module with templates manager"""
        from glyphs_info_mcp.modules.glyphs_sdk.glyphs_sdk_module import GlyphsSDKModule

        module = GlyphsSDKModule()

        # Mock templates manager
        mock_manager = MagicMock()
        module.templates_manager = mock_manager

        return module, mock_manager

    def test_get_resources_returns_dict(self, mock_sdk_module: tuple[MagicMock, MagicMock]) -> None:
        """Test get_resources returns dictionary of resource URIs"""
        module, mock_manager = mock_sdk_module

        # Mock templates
        mock_manager.get_templates.return_value = {
            "filter_without_dialog": {
                "name": "Filter Template",
                "type": "filter",
                "content": "# Filter code",
            },
            "reporter_default": {
                "name": "Reporter Template",
                "type": "reporter",
                "content": "# Reporter code",
            },
        }

        # Execute
        resources = module.get_resources()

        # Verify
        assert isinstance(resources, dict)
        assert len(resources) == 2
        assert "glyphs://plugin-template/filter_without_dialog" in resources
        assert "glyphs://plugin-template/reporter_default" in resources

        # Verify all values are callables
        for uri, handler in resources.items():
            assert callable(handler)

    def test_get_resources_without_templates_manager(self) -> None:
        """Test get_resources returns empty dict when manager not initialized"""
        from glyphs_info_mcp.modules.glyphs_sdk.glyphs_sdk_module import GlyphsSDKModule

        module = GlyphsSDKModule()
        module.templates_manager = None

        # Execute
        resources = module.get_resources()

        # Verify
        assert resources == {}

    def test_get_resources_closure_captures_template_id(self, mock_sdk_module: tuple[MagicMock, MagicMock]) -> None:
        """Test resource handlers correctly capture template_id (no late binding)"""
        module, mock_manager = mock_sdk_module

        # Mock templates
        mock_manager.get_templates.return_value = {
            "template_a": {"name": "A", "type": "filter", "content": "# A"},
            "template_b": {"name": "B", "type": "reporter", "content": "# B"},
        }

        # Mock _get_template_resource to track calls
        original_method = module._get_template_resource
        call_log = []

        def tracking_method(template_id: str) -> str:
            call_log.append(template_id)
            return f"Template: {template_id}"

        module._get_template_resource = tracking_method

        # Execute
        resources = module.get_resources()

        # Call each handler
        result_a = resources["glyphs://plugin-template/template_a"]()
        result_b = resources["glyphs://plugin-template/template_b"]()

        # Verify each handler called with correct template_id
        assert call_log == ["template_a", "template_b"]
        assert result_a == "Template: template_a"
        assert result_b == "Template: template_b"

    def test_get_template_resource_formats_markdown(self, mock_sdk_module: tuple[MagicMock, MagicMock]) -> None:
        """Test _get_template_resource returns formatted Markdown"""
        module, mock_manager = mock_sdk_module

        # Mock template data
        mock_manager.get_template_by_id.return_value = {
            "id": "filter_test",
            "name": "Test Filter",
            "type": "filter",
            "subtype": "without_dialog",
            "description": "A test filter",
            "content": "# Filter code\nclass TestFilter:\n    pass",
            "relative_path": "Filter/without dialog/plugin.py",
            "size": 45,
            "usage": {
                "base_class": "FilterWithoutDialog",
                "plugin_type": "filter",
            },
        }

        # Execute
        result = module._get_template_resource("filter_test")

        # Verify Markdown format
        assert "# Test Filter" in result
        assert "**Type**: filter" in result
        assert "**Subtype**: without_dialog" in result
        assert "## Description" in result
        assert "A test filter" in result
        assert "## Usage Information" in result
        assert "`FilterWithoutDialog`" in result
        assert "## Template Code" in result
        assert "```python" in result
        assert "# Filter code" in result
        assert "**Size**: 45 bytes" in result

    def test_get_template_resource_not_found(self, mock_sdk_module: tuple[MagicMock, MagicMock]) -> None:
        """Test _get_template_resource handles missing template"""
        module, mock_manager = mock_sdk_module

        mock_manager.get_template_by_id.return_value = None

        # Execute
        result = module._get_template_resource("nonexistent")

        # Verify error message
        assert "❌" in result
        assert "not found" in result.lower()


class TestListPythonTemplatesTool:
    """Test _list_python_templates_tool() method"""

    @pytest.fixture
    def mock_sdk_module(self) -> tuple[Any, MagicMock]:
        """Create mock SDK module with templates manager"""
        from glyphs_info_mcp.modules.glyphs_sdk.glyphs_sdk_module import GlyphsSDKModule

        module = GlyphsSDKModule()
        mock_manager = MagicMock()
        module.templates_manager = mock_manager
        return module, mock_manager

    def test_list_all_templates(self, mock_sdk_module: tuple[MagicMock, MagicMock]) -> None:
        """Test listing all Python templates"""
        module, mock_manager = mock_sdk_module

        mock_manager.get_templates.return_value = {
            "filter_without_dialog": {
                "name": "Filter Template",
                "type": "filter",
                "subtype": "without_dialog",
                "description": "A filter plugin",
            },
            "reporter_default": {
                "name": "Reporter Template",
                "type": "reporter",
                "subtype": "default",
                "description": "A reporter plugin",
            },
        }

        # Execute
        result = module._list_python_templates_tool()

        # Verify
        assert "🐍 Python Plugin Templates" in result
        assert "Found 2 template(s)" in result
        assert "filter_without_dialog" in result
        assert "reporter_default" in result
        assert "Filter Template" in result
        assert "Reporter Template" in result

    def test_list_templates_by_type(self, mock_sdk_module: tuple[MagicMock, MagicMock]) -> None:
        """Test listing templates filtered by type"""
        module, mock_manager = mock_sdk_module

        mock_manager.get_templates_by_type.return_value = {
            "filter_without_dialog": {
                "name": "Filter Template",
                "type": "filter",
                "subtype": "without_dialog",
                "description": "A filter plugin",
            }
        }

        # Execute
        result = module._list_python_templates_tool(template_type="filter")

        # Verify
        assert "Filter Templates" in result
        assert "filter_without_dialog" in result
        mock_manager.get_templates_by_type.assert_called_once_with("filter")

    def test_list_templates_empty_result(self, mock_sdk_module: tuple[MagicMock, MagicMock]) -> None:
        """Test listing when no templates found"""
        module, mock_manager = mock_sdk_module

        mock_manager.get_templates.return_value = {}

        # Execute
        result = module._list_python_templates_tool()

        # Verify
        assert "No Python templates found" in result

    def test_list_templates_without_manager(self) -> None:
        """Test listing when templates manager not initialized"""
        from glyphs_info_mcp.modules.glyphs_sdk.glyphs_sdk_module import GlyphsSDKModule

        module = GlyphsSDKModule()
        module.templates_manager = None

        # Execute
        result = module._list_python_templates_tool()

        # Verify
        assert "❌" in result
        assert "not initialized" in result.lower()


class TestGetPythonTemplateTool:
    """Test _get_python_template_tool() method"""

    @pytest.fixture
    def mock_sdk_module(self) -> tuple[Any, MagicMock]:
        """Create mock SDK module with templates manager"""
        from glyphs_info_mcp.modules.glyphs_sdk.glyphs_sdk_module import GlyphsSDKModule

        module = GlyphsSDKModule()
        mock_manager = MagicMock()
        module.templates_manager = mock_manager
        return module, mock_manager

    def test_get_template_success(self, mock_sdk_module: tuple[MagicMock, MagicMock]) -> None:
        """Test getting template details successfully"""
        module, mock_manager = mock_sdk_module

        mock_manager.get_template_by_id.return_value = {
            "id": "filter_test",
            "name": "Test Filter",
            "type": "filter",
            "subtype": "without_dialog",
            "description": "A test filter",
            "content": "class TestFilter:\n    pass",
            "relative_path": "Filter/without dialog/plugin.py",
            "size": 32,
            "usage": {
                "base_class": "FilterWithoutDialog",
                "plugin_type": "filter",
                "requirements": ["from GlyphsApp import *"],
            },
        }

        # Execute
        result = module._get_python_template_tool(template_id="filter_test")

        # Verify
        assert "🐍 Test Filter" in result
        assert "**Type**: filter" in result
        assert "**Subtype**: without_dialog" in result
        assert "### Description" in result
        assert "A test filter" in result
        assert "### Usage Information" in result
        assert "`FilterWithoutDialog`" in result
        assert "### Template Code" in result
        assert "```python" in result
        assert "class TestFilter" in result
        assert "### Placeholders to Replace" in result
        assert "____PluginClassName____" in result

    def test_get_template_not_found(self, mock_sdk_module: tuple[MagicMock, MagicMock]) -> None:
        """Test getting nonexistent template"""
        module, mock_manager = mock_sdk_module

        mock_manager.get_template_by_id.return_value = None
        mock_manager.get_templates.return_value = {
            "filter_a": {},
            "reporter_b": {},
        }

        # Execute
        result = module._get_python_template_tool(template_id="nonexistent")

        # Verify
        assert "❌" in result
        assert "not found" in result.lower()
        assert "filter_a" in result
        assert "reporter_b" in result

    def test_get_template_empty_id(self, mock_sdk_module: tuple[MagicMock, MagicMock]) -> None:
        """Test getting template with empty ID"""
        module, mock_manager = mock_sdk_module

        # Execute
        result = module._get_python_template_tool(template_id="")

        # Verify
        assert "provide a template_id" in result.lower()

    def test_get_template_without_manager(self) -> None:
        """Test getting template when manager not initialized"""
        from glyphs_info_mcp.modules.glyphs_sdk.glyphs_sdk_module import GlyphsSDKModule

        module = GlyphsSDKModule()
        module.templates_manager = None

        # Execute
        result = module._get_python_template_tool(template_id="test")

        # Verify
        assert "❌" in result
        assert "not initialized" in result.lower()
