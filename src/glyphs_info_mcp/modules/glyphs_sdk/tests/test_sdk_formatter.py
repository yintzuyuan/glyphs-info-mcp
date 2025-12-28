"""
SDK Result Formatting Test Suite

Tests SDK result formatting functionality.
Following TDD principles: Red → Green → Refactor
"""
from glyphs_info_mcp.modules.sdk_formatter import SDKResultFormatter


class TestSDKResultFormatter:
    """Test SDK result formatter"""

    def test_should_format_guide_result(self) -> None:
        """Should format guide result"""
        # Arrange
        formatter = SDKResultFormatter()
        result = {
            "type": "guide",
            "category": "template_guide",
            "path": "/test/Python Templates/Filter/README.md",
            "name": "README.md",
            "content": "Filter plugin development guide with examples and best practices",
            "relevance_score": 0.8
        }

        # Act
        formatted = formatter.format_single_result(result)

        # Assert
        assert "📚 指南：" in formatted
        assert "Filter" in formatted
        assert "README.md" in formatted
        assert "📄 檔案：" in formatted
        assert "Python Templates/Filter" in formatted

    def test_should_format_implementation_result(self) -> None:
        """Should format implementation result"""
        # Arrange
        formatter = SDKResultFormatter()
        result = {
            "type": "implementation",
            "category": "plugin_framework",
            "path": "/test/ObjectWrapper/GlyphsApp/plugins.py",
            "name": "plugins.py",
            "content": "class FilterWithDialog(GSFilterPlugin): def filter(self, layer, inEditView, customParameters):",
            "relevance_score": 0.9
        }

        # Act
        formatted = formatter.format_single_result(result)

        # Assert
        assert "🔧 實作：" in formatted
        assert "FilterWithDialog" in formatted
        assert "plugins.py" in formatted
        assert "📄 檔案：" in formatted
        assert "class FilterWithDialog" in formatted

    def test_should_format_example_result(self) -> None:
        """Should format example result"""
        # Arrange
        formatter = SDKResultFormatter()
        result = {
            "type": "example",
            "category": "plugin_sample",
            "path": "/test/Python Samples/MultipleTools/plugin.py",
            "name": "plugin.py",
            "content": "def selectTool(self): self.toolBarButton.setState_(1)",
            "relevance_score": 0.7
        }

        # Act
        formatted = formatter.format_single_result(result)

        # Assert
        assert "💡 範例：" in formatted
        assert "MultipleTools" in formatted
        assert "plugin.py" in formatted
        assert "📄 檔案：" in formatted
        assert "selectTool" in formatted

    def test_should_format_template_result(self) -> None:
        """Should format template result"""
        # Arrange
        formatter = SDKResultFormatter()
        result = {
            "type": "template",
            "category": "filter_template",
            "path": "/test/Python Templates/Filter/plugin.py",
            "name": "plugin.py",
            "content": "class ____PluginClassName____(FilterWithoutDialog):",
            "relevance_score": 0.6
        }

        # Act
        formatted = formatter.format_single_result(result)

        # Assert
        assert "📋 範本：" in formatted
        assert "Filter" in formatted
        assert "plugin.py" in formatted
        assert "📄 檔案：" in formatted
        assert "PluginClassName" in formatted

    def test_should_format_multiple_results(self) -> None:
        """Should format multiple search results"""
        # Arrange
        formatter = SDKResultFormatter()
        results = [
            {
                "type": "guide",
                "category": "template_guide",
                "path": "/test/Filter/README.md",
                "name": "README.md",
                "content": "Filter development guide",
                "relevance_score": 0.8
            },
            {
                "type": "implementation",
                "category": "plugin_framework",
                "path": "/test/plugins.py",
                "name": "plugins.py",
                "content": "class FilterWithDialog",
                "relevance_score": 0.7
            }
        ]

        # Act
        formatted = formatter.format_results(results, "Filter")

        # Assert
        assert "🔍 Found 2 related SDK content:" in formatted
        assert "**1. 📚 Guide:" in formatted
        assert "**2. 🔧 Implementation:" in formatted
        assert "Filter development guide" in formatted
        assert "FilterWithDialog" in formatted

    def test_should_handle_empty_results(self) -> None:
        """Should handle empty search results"""
        # Arrange
        formatter = SDKResultFormatter()
        results: list[dict[str, str]] = []

        # Act
        formatted = formatter.format_results(results, "nonexistent")

        # Assert
        assert "🔍 Found 0 related SDK content:" in formatted
        assert "No SDK content related to 'nonexistent' found" in formatted

    def test_should_limit_content_display(self) -> None:
        """Should limit content display length"""
        # Arrange
        formatter = SDKResultFormatter()
        long_content = "a" * 500  # Very long content
        result = {
            "type": "guide",
            "category": "template_guide",
            "path": "/test/README.md",
            "name": "README.md",
            "content": long_content,
            "relevance_score": 0.8
        }

        # Act
        formatted = formatter.format_single_result(result)

        # Assert
        assert len(formatted) < 1000  # Ensure formatted result is not too long
        content = str(result["content"])
        assert "..." in formatted or len(content) <= 200  # Should be truncated or content is short
