"""
SDK Content Indexing Test Suite

Tests SDK content index building functionality.
Following TDD principles: Red → Green → Refactor
"""
from pathlib import Path

from glyphs_info_mcp.modules.sdk_indexer import SDKIndexer


class TestSDKIndexer:
    """Test SDK indexer"""

    def test_should_create_indexer_with_sdk_path(self) -> None:
        """Should create indexer with SDK path"""
        # Arrange
        sdk_path = Path("../glyphs-api/src/resources/GlyphsSDK")

        # Act
        indexer = SDKIndexer(sdk_path)

        # Assert
        assert indexer.sdk_path == sdk_path

    def test_should_scan_readme_files(self) -> None:
        """Should scan all README files"""
        # Arrange
        sdk_path = Path("../glyphs-api/src/resources/GlyphsSDK")
        indexer = SDKIndexer(sdk_path)

        # Act
        readme_files = indexer.scan_readme_files()

        # Assert
        assert len(readme_files) > 0
        assert any("README.md" in str(file) for file in readme_files)
        assert any("Python Templates" in str(file) for file in readme_files)

    def test_should_scan_python_implementation_files(self) -> None:
        """Should scan Python implementation files (excluding __init__.py)"""
        # Arrange
        sdk_path = Path("../glyphs-api/src/resources/GlyphsSDK")
        indexer = SDKIndexer(sdk_path)

        # Act
        impl_files = indexer.scan_implementation_files()

        # Assert
        assert len(impl_files) > 0
        assert any("plugins.py" in str(file) for file in impl_files)
        assert any("drawingTools.py" in str(file) for file in impl_files)
        # Verify __init__.py is excluded
        assert not any("__init__.py" in str(file) for file in impl_files)

    def test_should_build_content_index(self) -> None:
        """Should build content index"""
        # Arrange
        sdk_path = Path("../glyphs-api/src/resources/GlyphsSDK")
        indexer = SDKIndexer(sdk_path)

        # Act
        index = indexer.build_index()

        # Assert
        assert "guides" in index
        assert "implementation" in index
        assert "examples" in index
        assert "templates" in index

        # Check guides index
        guides = index["guides"]
        assert len(guides) > 0
        assert any(item["type"] == "guide" for item in guides)

        # Check implementation index
        implementation = index["implementation"]
        assert len(implementation) > 0
        assert any(item["type"] == "implementation" for item in implementation)
