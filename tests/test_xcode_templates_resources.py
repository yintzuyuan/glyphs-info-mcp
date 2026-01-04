"""Tests for XcodeTemplatesResourceManager"""

import pytest
from pathlib import Path
from glyphs_info_mcp.shared.core.xcode_templates_resources import (
    XcodeTemplatesResourceManager,
)


@pytest.fixture
def sdk_path() -> Path:
    """Get GlyphsSDK path"""
    project_root = Path(__file__).parent.parent
    return (
        project_root / "src" / "glyphs_info_mcp" / "data" / "official" / "GlyphsSDK"
    )


@pytest.fixture
def manager(sdk_path: Path) -> XcodeTemplatesResourceManager:
    """Create XcodeTemplatesResourceManager instance"""
    return XcodeTemplatesResourceManager(sdk_path)


def test_initialization(manager: XcodeTemplatesResourceManager) -> None:
    """Test manager initialization"""
    assert manager is not None
    assert manager.sdk_path.exists()
    assert manager.native_accessor is not None


def test_scan_xcode_templates(manager: XcodeTemplatesResourceManager) -> None:
    """Test scanning all Xcode templates"""
    templates = manager.scan_xcode_templates()

    # Should find 7 templates
    assert len(templates) == 7

    # Check template IDs
    expected_ids = {
        "reporter",
        "filter",
        "palette",
        "tool",
        "file_format",
        "plugin",
        "plugin_base",
    }
    assert set(templates.keys()) == expected_ids

    # Each template should have required fields
    for tid, info in templates.items():
        assert "id" in info
        assert "name" in info
        assert "type" in info
        assert "path" in info
        assert "file_count" in info


def test_get_templates_with_cache(manager: XcodeTemplatesResourceManager) -> None:
    """Test template caching"""
    # First call - should scan
    templates1 = manager.get_templates()

    # Second call - should use cache
    templates2 = manager.get_templates()

    assert templates1 is templates2  # Same object reference


def test_get_template_by_id(manager: XcodeTemplatesResourceManager) -> None:
    """Test getting specific template with full content"""
    template = manager.get_template_by_id("reporter")

    assert template is not None
    assert template["id"] == "reporter"
    assert template["type"] == "Reporter"
    assert "source_files" in template  # Should have full content

    # Source files should include .h and .m files
    source_files = template["source_files"]
    assert any(".h" in path for path in source_files.keys())
    assert any(".m" in path for path in source_files.keys())


def test_get_template_by_id_not_found(manager: XcodeTemplatesResourceManager) -> None:
    """Test getting non-existent template"""
    template = manager.get_template_by_id("nonexistent")
    assert template is None


def test_get_templates_by_type(manager: XcodeTemplatesResourceManager) -> None:
    """Test filtering templates by type"""
    reporter_templates = manager.get_templates_by_type("Reporter")

    assert len(reporter_templates) >= 1
    for tid, info in reporter_templates.items():
        assert info["type"] == "Reporter"


def test_get_template_types(manager: XcodeTemplatesResourceManager) -> None:
    """Test getting all template types"""
    types = manager.get_template_types()

    assert isinstance(types, list)
    assert len(types) > 0
    assert "Reporter" in types or "Filter" in types


def test_get_resource_list(manager: XcodeTemplatesResourceManager) -> None:
    """Test MCP resource list format"""
    resources = manager.get_resource_list()

    # Should have 7 resources
    assert len(resources) == 7

    # Check resource format
    for resource in resources:
        assert "uri" in resource
        assert "name" in resource
        assert "description" in resource
        assert "mimeType" in resource

        # Check URI format
        assert resource["uri"].startswith("glyphs://xcode-template/")

        # Check MIME type
        assert resource["mimeType"] == "text/x-objective-c"


def test_template_id_generation(manager: XcodeTemplatesResourceManager) -> None:
    """Test template ID generation logic"""
    # Test various template names
    assert manager._generate_template_id("Glyphs Reporter") == "reporter"
    assert manager._generate_template_id("Glyphs Filter Plugin") == "filter"
    assert manager._generate_template_id("Glyphs Plugin Base") == "plugin_base"
