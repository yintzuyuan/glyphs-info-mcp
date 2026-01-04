"""Tests for XcodeSamplesResourceManager"""

import pytest
from pathlib import Path
from glyphs_info_mcp.shared.core.xcode_samples_resources import (
    XcodeSamplesResourceManager,
)


@pytest.fixture
def sdk_path() -> Path:
    """Get GlyphsSDK path"""
    project_root = Path(__file__).parent.parent
    return (
        project_root / "src" / "glyphs_info_mcp" / "data" / "official" / "GlyphsSDK"
    )


@pytest.fixture
def manager(sdk_path: Path) -> XcodeSamplesResourceManager:
    """Create XcodeSamplesResourceManager instance"""
    return XcodeSamplesResourceManager(sdk_path)


def test_initialization(manager: XcodeSamplesResourceManager) -> None:
    """Test manager initialization"""
    assert manager is not None
    assert manager.sdk_path.exists()
    assert manager.native_accessor is not None


def test_initialization_with_invalid_path() -> None:
    """Test initialization with non-existent SDK path"""
    with pytest.raises(FileNotFoundError):
        XcodeSamplesResourceManager(Path("/nonexistent/path"))


def test_initialization_with_file_instead_of_directory(tmp_path: Path) -> None:
    """Test initialization with file instead of directory"""
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("test")

    with pytest.raises(ValueError, match="not a directory"):
        XcodeSamplesResourceManager(file_path)


def test_scan_xcode_samples(manager: XcodeSamplesResourceManager) -> None:
    """Test scanning all Xcode samples"""
    samples = manager.scan_xcode_samples()

    # Should find 4 samples
    assert len(samples) == 4

    # Check sample IDs
    expected_ids = {
        "custom_parameter_ui",
        "inspector_demo",
        "photofont",
        "plugin_with_window",
    }
    assert set(samples.keys()) == expected_ids

    # Each sample should have required fields
    for sid, info in samples.items():
        assert "id" in info
        assert "name" in info
        assert "path" in info
        assert "has_xcode_project" in info
        assert "readme" in info
        assert "source_files" in info
        assert "source_file_count" in info


def test_get_samples_with_cache(manager: XcodeSamplesResourceManager) -> None:
    """Test sample caching"""
    # First call - should scan
    samples1 = manager.get_samples()

    # Second call - should use cache
    samples2 = manager.get_samples()

    assert samples1 is samples2  # Same object reference


def test_get_sample_by_id(manager: XcodeSamplesResourceManager) -> None:
    """Test getting specific sample with full content"""
    sample = manager.get_sample_by_id("inspector_demo")

    assert sample is not None
    assert sample["id"] == "inspector_demo"
    assert sample["name"] == "InspectorDemo"
    assert "source_code" in sample  # Should have full content loaded

    # Source code should be a dict
    source_code = sample["source_code"]
    assert isinstance(source_code, dict)
    assert len(source_code) > 0

    # Should contain .h and .m files
    file_extensions = [Path(path).suffix for path in source_code.keys()]
    assert ".h" in file_extensions or ".m" in file_extensions


def test_get_sample_by_id_not_found(manager: XcodeSamplesResourceManager) -> None:
    """Test getting non-existent sample"""
    sample = manager.get_sample_by_id("nonexistent")
    assert sample is None


def test_sample_id_generation(manager: XcodeSamplesResourceManager) -> None:
    """Test sample ID generation logic (CamelCase to snake_case)"""
    # Test CamelCase conversion
    assert manager._generate_sample_id("InspectorDemo") == "inspector_demo"
    assert manager._generate_sample_id("CustomParameterUI") == "custom_parameter_ui"
    assert manager._generate_sample_id("PhotoFont") == "photo_font"

    # Test space handling
    assert manager._generate_sample_id("Plugin With Window") == "plugin_with_window"

    # Test consecutive underscores removal
    assert manager._generate_sample_id("Some  Spaced  Name") == "some_spaced_name"

    # Test edge cases
    assert manager._generate_sample_id("SimpleTest") == "simple_test"


def test_get_resource_list(manager: XcodeSamplesResourceManager) -> None:
    """Test MCP resource list format"""
    resources = manager.get_resource_list()

    # Should have 4 resources
    assert len(resources) == 4

    # Check resource format
    for resource in resources:
        assert "uri" in resource
        assert "name" in resource
        assert "description" in resource
        assert "mimeType" in resource

        # Check URI format
        assert resource["uri"].startswith("glyphs://xcode-sample/")

        # Check MIME type
        assert resource["mimeType"] == "text/x-objective-c"

        # Check name prefix
        assert resource["name"].startswith("Xcode Sample: ")


def test_resource_list_description_truncation(manager: XcodeSamplesResourceManager) -> None:
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


def test_samples_source_file_count_matches(manager: XcodeSamplesResourceManager) -> None:
    """Test that source_file_count matches actual source_files length"""
    samples = manager.get_samples()

    for sid, sample in samples.items():
        assert sample["source_file_count"] == len(sample["source_files"]), \
            f"Mismatch in sample {sid}: count={sample['source_file_count']}, actual={len(sample['source_files'])}"


def test_camelcase_conversion_with_consecutive_capitals(manager: XcodeSamplesResourceManager) -> None:
    """Test CamelCase conversion handles consecutive capitals correctly"""
    # This is a critical test for the regex logic
    test_cases = {
        "CustomParameterUI": "custom_parameter_ui",
        "SimpleTest": "simple_test",
        "PhotoFont": "photo_font",
    }

    for input_name, expected_id in test_cases.items():
        actual_id = manager._generate_sample_id(input_name)
        assert actual_id == expected_id, \
            f"Failed for '{input_name}': expected '{expected_id}', got '{actual_id}'"


def test_no_consecutive_underscores_in_generated_ids(manager: XcodeSamplesResourceManager) -> None:
    """Test that generated IDs never contain consecutive underscores"""
    samples = manager.get_samples()

    for sample_id in samples.keys():
        assert "__" not in sample_id, \
            f"Sample ID '{sample_id}' contains consecutive underscores"
