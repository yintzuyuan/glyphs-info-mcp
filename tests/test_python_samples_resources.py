"""Tests for PythonSamplesResourceManager"""

import pytest
from pathlib import Path
from glyphs_info_mcp.shared.core.python_samples_resources import (
    PythonSamplesResourceManager,
)


@pytest.fixture
def sdk_path() -> Path:
    """Get GlyphsSDK path"""
    project_root = Path(__file__).parent.parent
    return (
        project_root / "src" / "glyphs_info_mcp" / "data" / "official" / "GlyphsSDK"
    )


@pytest.fixture
def manager(sdk_path: Path) -> PythonSamplesResourceManager:
    """Create PythonSamplesResourceManager instance"""
    return PythonSamplesResourceManager(sdk_path)


def test_initialization(manager: PythonSamplesResourceManager) -> None:
    """Test manager initialization"""
    assert manager is not None
    assert manager.sdk_path.exists()
    assert manager.native_accessor is not None


def test_initialization_with_invalid_path() -> None:
    """Test initialization with non-existent SDK path"""
    with pytest.raises(FileNotFoundError):
        PythonSamplesResourceManager(Path("/nonexistent/path"))


def test_initialization_with_file_instead_of_directory(tmp_path: Path) -> None:
    """Test initialization with file instead of directory"""
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("test")

    with pytest.raises(ValueError, match="not a directory"):
        PythonSamplesResourceManager(file_path)


def test_scan_python_samples(manager: PythonSamplesResourceManager) -> None:
    """Test scanning all Python samples"""
    samples = manager.scan_python_samples()

    # Should find 6 samples
    assert len(samples) == 6

    # Check sample IDs
    expected_ids = {
        "callback_for_context_menu",
        "document_exported",
        "multipletools",
        "plugin_preferences",
        "plugin_with_window",
        "smiley_panel_plugin",
    }
    assert set(samples.keys()) == expected_ids

    # Each sample should have required fields
    for sid, info in samples.items():
        assert "id" in info
        assert "name" in info
        assert "type" in info
        assert "path" in info
        assert "has_bundle" in info
        assert "readme" in info
        assert "source_files" in info
        assert "source_file_count" in info


def test_get_samples_with_cache(manager: PythonSamplesResourceManager) -> None:
    """Test sample caching"""
    # First call - should scan
    samples1 = manager.get_samples()

    # Second call - should use cache
    samples2 = manager.get_samples()

    assert samples1 is samples2  # Same object reference


def test_get_sample_by_id(manager: PythonSamplesResourceManager) -> None:
    """Test getting specific sample with full content"""
    sample = manager.get_sample_by_id("callback_for_context_menu")

    assert sample is not None
    assert sample["id"] == "callback_for_context_menu"
    assert sample["name"] == "Callback for context menu"
    assert "source_code" in sample  # Should have full content loaded

    # Source code should be a dict
    source_code = sample["source_code"]
    assert isinstance(source_code, dict)
    assert len(source_code) > 0


def test_get_sample_by_id_not_found(manager: PythonSamplesResourceManager) -> None:
    """Test getting non-existent sample"""
    sample = manager.get_sample_by_id("nonexistent")
    assert sample is None


def test_sample_id_generation(manager: PythonSamplesResourceManager) -> None:
    """Test sample ID generation logic"""
    # Test various sample names
    assert manager._generate_sample_id("Callback for context menu") == "callback_for_context_menu"
    assert manager._generate_sample_id("Plugin With Window") == "plugin_with_window"
    assert manager._generate_sample_id("Document exported") == "document_exported"

    # Test edge cases
    assert manager._generate_sample_id("Test  Multiple   Spaces") == "test_multiple_spaces"
    assert manager._generate_sample_id("UPPERCASE") == "uppercase"
    assert manager._generate_sample_id("mixedCase") == "mixedcase"


def test_get_resource_list(manager: PythonSamplesResourceManager) -> None:
    """Test MCP resource list format"""
    resources = manager.get_resource_list()

    # Should have 6 resources
    assert len(resources) == 6

    # Check resource format
    for resource in resources:
        assert "uri" in resource
        assert "name" in resource
        assert "description" in resource
        assert "mimeType" in resource

        # Check URI format
        assert resource["uri"].startswith("glyphs://python-sample/")

        # Check MIME type
        assert resource["mimeType"] == "text/x-python"

        # Check name prefix
        assert resource["name"].startswith("Python Sample: ")


def test_resource_list_description_truncation(manager: PythonSamplesResourceManager) -> None:
    """Test that README descriptions are truncated to 100 chars"""
    resources = manager.get_resource_list()

    for resource in resources:
        # Description should not exceed 103 chars (100 + "...")
        assert len(resource["description"]) <= 103

        # If original README was >100 chars, should end with "..."
        sample_id = resource["uri"].split("/")[-1]
        sample = manager.get_sample_by_id(sample_id)
        if sample and len(sample.get("readme", "")) > 100:
            assert resource["description"].endswith("...")


def test_samples_have_valid_types(manager: PythonSamplesResourceManager) -> None:
    """Test that all samples have valid type values"""
    samples = manager.get_samples()

    valid_types = {"script", "plugin", "palette", "tool", "filter", "reporter"}

    for sid, sample in samples.items():
        assert sample["type"] in valid_types, f"Invalid type '{sample['type']}' for sample {sid}"


def test_samples_source_file_count_matches(manager: PythonSamplesResourceManager) -> None:
    """Test that source_file_count matches actual source_files length"""
    samples = manager.get_samples()

    for sid, sample in samples.items():
        assert sample["source_file_count"] == len(sample["source_files"]), \
            f"Mismatch in sample {sid}: count={sample['source_file_count']}, actual={len(sample['source_files'])}"
