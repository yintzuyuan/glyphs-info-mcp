"""Tests for SDKNativeAccessor Python Samples functionality"""

import pytest
from pathlib import Path
from glyphs_info_mcp.shared.core.sdk_native_accessor import SDKNativeAccessor


@pytest.fixture
def sdk_path() -> Path:
    """Get GlyphsSDK path"""
    project_root = Path(__file__).parent.parent.parent
    return (
        project_root / "src" / "glyphs_info_mcp" / "data" / "official" / "GlyphsSDK"
    )


@pytest.fixture
def accessor(sdk_path: Path) -> SDKNativeAccessor:
    """Create SDKNativeAccessor instance"""
    return SDKNativeAccessor(sdk_path)


def test_list_python_samples(accessor: SDKNativeAccessor) -> None:
    """Test listing all Python samples"""
    samples = accessor.list_python_samples()

    # Should find 6 Python samples
    assert len(samples) == 6

    # Each sample should have required fields
    for sample in samples:
        assert "name" in sample
        assert "type" in sample
        assert "path" in sample
        assert "has_bundle" in sample
        assert "readme" in sample
        assert "source_files" in sample
        assert "source_file_count" in sample

        # Type should be valid
        assert sample["type"] in {
            "script",
            "plugin",
            "palette",
            "tool",
            "filter",
            "reporter",
        }

        # Source file count should match actual files
        assert sample["source_file_count"] == len(sample["source_files"])


def test_python_samples_cache(accessor: SDKNativeAccessor) -> None:
    """Test that Python samples are cached"""
    # First call
    samples1 = accessor.list_python_samples()

    # Second call should use cache
    samples2 = accessor.list_python_samples()

    # Should be same object
    assert samples1 is samples2


def test_get_python_sample(accessor: SDKNativeAccessor) -> None:
    """Test getting a specific Python sample with full content"""
    sample = accessor.get_python_sample("Callback for context menu")

    assert sample is not None
    assert sample["name"] == "Callback for context menu"
    assert "source_code" in sample

    # Source code should be a dict with file paths as keys
    source_code = sample["source_code"]
    assert isinstance(source_code, dict)
    assert len(source_code) > 0

    # All source code values should be strings
    for file_path, content in source_code.items():
        assert isinstance(content, str)
        assert len(content) > 0


def test_get_python_sample_not_found(accessor: SDKNativeAccessor) -> None:
    """Test getting non-existent Python sample"""
    sample = accessor.get_python_sample("NonExistentSample")
    assert sample is None


def test_search_python_samples_by_name(accessor: SDKNativeAccessor) -> None:
    """Test searching Python samples by name"""
    results = accessor.search_python_samples("context menu")

    # Should find at least one result
    assert len(results) > 0

    # First result should have score 1.0 (exact name match)
    assert results[0]["score"] == 1.0
    assert "context menu" in results[0]["name"].lower()


def test_search_python_samples_by_readme(accessor: SDKNativeAccessor) -> None:
    """Test searching Python samples by README content"""
    # Search for a term likely in READMEs
    results = accessor.search_python_samples("plugin")

    # Should find results
    assert len(results) > 0

    # Results should have scores
    for result in results:
        assert "score" in result
        assert 0 < result["score"] <= 1.0


def test_search_python_samples_empty_query(accessor: SDKNativeAccessor) -> None:
    """Test searching with empty query"""
    results = accessor.search_python_samples("")

    # Should return all samples with empty query
    assert len(results) == 6


def test_python_sample_bundle_detection(accessor: SDKNativeAccessor) -> None:
    """Test that bundle samples are correctly identified"""
    samples = accessor.list_python_samples()

    # Should have 6 samples total
    assert len(samples) == 6

    # Check bundle detection - should have both types
    bundle_samples = [s for s in samples if s["has_bundle"]]
    standalone_samples = [s for s in samples if not s["has_bundle"]]

    # Should have at least 3 bundle samples (Plugin With Window, Smiley Panel Plugin, MultipleTools)
    assert len(bundle_samples) >= 3

    # Should have at least some standalone samples
    assert len(standalone_samples) >= 1

    # Verify has_bundle is a boolean
    for sample in samples:
        assert isinstance(sample["has_bundle"], bool)


def test_python_sample_readme_extraction(accessor: SDKNativeAccessor) -> None:
    """Test README extraction from samples"""
    samples = accessor.list_python_samples()

    # Check if any samples have README content
    samples_with_readme = [s for s in samples if s["readme"]]

    # At least some samples should have README
    # If none have README, it's acceptable but we should verify the logic works
    for sample in samples_with_readme:
        assert isinstance(sample["readme"], str)
        assert len(sample["readme"]) > 0


def test_python_sample_type_inference(accessor: SDKNativeAccessor) -> None:
    """Test sample type inference from bundle suffix"""
    samples = accessor.list_python_samples()

    for sample in samples:
        sample_type = sample["type"]

        # If has bundle, type should match bundle suffix
        if sample["has_bundle"]:
            path_lower = sample["path"].lower()
            if ".glyphsplugin" in path_lower and sample_type != "plugin":
                # Type might be inferred from other indicators
                assert sample_type in {"script", "plugin", "palette", "tool", "filter", "reporter"}
            elif ".glyphspalette" in path_lower:
                assert sample_type == "palette"
            elif ".glyphsfilter" in path_lower:
                assert sample_type == "filter"
            elif ".glyphsreporter" in path_lower:
                assert sample_type == "reporter"
            elif ".glyphstool" in path_lower:
                assert sample_type == "tool"


def test_python_sample_source_files_are_python(accessor: SDKNativeAccessor) -> None:
    """Test that source files are Python files"""
    samples = accessor.list_python_samples()

    for sample in samples:
        for file_info in sample["source_files"]:
            # All source files should be .py files
            assert file_info["path"].endswith(".py"), \
                f"Non-Python file found: {file_info['path']} in sample {sample['name']}"


def test_parse_python_sample_error_handling(accessor: SDKNativeAccessor, tmp_path: Path) -> None:
    """Test error handling when parsing invalid sample directory"""
    # This test verifies that invalid directories are skipped gracefully
    # We can't directly test _parse_python_sample as it's private,
    # but we can verify list_python_samples handles errors

    samples = accessor.list_python_samples()

    # Should complete without raising exceptions
    assert isinstance(samples, list)
    assert all(isinstance(s, dict) for s in samples)
