"""
SDK Search Test Suite

Tests SDK search functionality.
Following TDD principles: Red → Green → Refactor
"""
from glyphs_info_mcp.modules.sdk_searcher import SDKSearcher


class TestSDKSearcher:
    """Test SDK searcher"""

    def test_should_create_searcher_with_index(self) -> None:
        """Should create searcher with index"""
        # Arrange
        index = {
            "guides": [{"type": "guide", "path": "/test/README.md", "name": "README.md"}],
            "implementation": []
        }

        # Act
        searcher = SDKSearcher(index)

        # Assert
        assert searcher.index == index

    def test_should_search_guides_by_keyword(self) -> None:
        """Should search guides by keyword"""
        # Arrange
        index = {
            "guides": [
                {
                    "type": "guide",
                    "path": "/test/Filter/README.md",
                    "name": "README.md",
                    "category": "template_guide",
                    "content": "Filter plugin development guide"
                }
            ],
            "implementation": []
        }
        searcher = SDKSearcher(index)

        # Act
        results = searcher.search("Filter plugin", max_results=5)

        # Assert
        assert len(results) == 1
        assert results[0]["type"] == "guide"
        assert "Filter" in results[0]["content"]

    def test_should_search_implementation_by_keyword(self) -> None:
        """Should search implementation code by keyword"""
        # Arrange
        index = {
            "guides": [],
            "implementation": [
                {
                    "type": "implementation",
                    "path": "/test/plugins.py",
                    "name": "plugins.py",
                    "category": "plugin_framework",
                    "content": "class FilterWithDialog(GSFilterPlugin):"
                }
            ]
        }
        searcher = SDKSearcher(index)

        # Act
        results = searcher.search("FilterWithDialog", max_results=5)

        # Assert
        assert len(results) == 1
        assert results[0]["type"] == "implementation"
        assert "FilterWithDialog" in results[0]["content"]

    def test_should_return_formatted_results(self) -> None:
        """Should return formatted search results"""
        # Arrange
        index = {
            "guides": [
                {
                    "type": "guide",
                    "path": "/test/Filter/README.md",
                    "name": "README.md",
                    "category": "template_guide",
                    "content": "Filter plugin development guide with examples"
                }
            ],
            "implementation": []
        }
        searcher = SDKSearcher(index)

        # Act
        results = searcher.search("Filter", max_results=5)

        # Assert
        result = results[0]
        assert "type" in result
        assert "category" in result
        assert "path" in result
        assert "content" in result
        assert "relevance_score" in result

    def test_should_search_across_multiple_categories(self) -> None:
        """Should search across multiple categories"""
        # Arrange
        index = {
            "guides": [
                {
                    "type": "guide",
                    "path": "/test/Filter/README.md",
                    "name": "README.md",
                    "category": "template_guide",
                    "content": "Filter plugin guide"
                }
            ],
            "implementation": [
                {
                    "type": "implementation",
                    "path": "/test/plugins.py",
                    "name": "plugins.py",
                    "category": "plugin_framework",
                    "content": "class FilterWithDialog"
                }
            ],
            "examples": [
                {
                    "type": "example",
                    "path": "/test/sample_filter.py",
                    "name": "sample_filter.py",
                    "category": "plugin_sample",
                    "content": "example filter implementation"
                }
            ]
        }
        searcher = SDKSearcher(index)

        # Act
        results = searcher.search("Filter", max_results=10)

        # Assert
        assert len(results) == 3
        types = [r["type"] for r in results]
        assert "guide" in types
        assert "implementation" in types
        assert "example" in types
