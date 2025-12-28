"""
SDK Content Indexer
Responsible for scanning and indexing various content in GlyphsSDK
"""
from pathlib import Path
from typing import Any


class SDKIndexer:
    """SDK content index builder"""

    def __init__(self, sdk_path: Path):
        """
        Initialize indexer

        Args:
            sdk_path: GlyphsSDK root directory path
        """
        self.sdk_path = Path(sdk_path)

    def scan_readme_files(self) -> list[Path]:
        """
        Scan all README files

        Returns:
            List of README file paths
        """
        readme_files = []

        # Scan root directory README
        if (self.sdk_path / "README.md").exists():
            readme_files.append(self.sdk_path / "README.md")

        # Scan README in Python Templates
        templates_path = self.sdk_path / "Python Templates"
        if templates_path.exists():
            for item in templates_path.rglob("README.md"):
                readme_files.append(item)

        # Scan readme in Python Samples
        samples_path = self.sdk_path / "Python Samples"
        if samples_path.exists():
            for item in samples_path.rglob("readme.md"):
                readme_files.append(item)

        return readme_files

    def scan_implementation_files(self) -> list[Path]:
        """
        Scan Python implementation files (excluding __init__.py)

        Returns:
            List of Python implementation file paths
        """
        impl_files = []

        # Scan Python files in ObjectWrapper/GlyphsApp
        glyphsapp_path = self.sdk_path / "ObjectWrapper" / "GlyphsApp"
        if glyphsapp_path.exists():
            for py_file in glyphsapp_path.rglob("*.py"):
                # Exclude __init__.py
                if py_file.name != "__init__.py":
                    impl_files.append(py_file)

        return impl_files

    def scan_sample_files(self) -> list[Path]:
        """
        Scan sample Python files

        Returns:
            List of sample Python file paths
        """
        sample_files = []

        samples_path = self.sdk_path / "Python Samples"
        if samples_path.exists():
            for py_file in samples_path.rglob("*.py"):
                sample_files.append(py_file)

        return sample_files

    def scan_template_files(self) -> list[Path]:
        """
        Scan template Python files - disabled, template code will be provided as MCP resources

        Returns:
            Empty list (template code is no longer indexed as search content)
        """
        # Template code has been moved to MCP resource system, no longer indexed as search content
        # This avoids overlap with README file content
        return []

    def build_index(self) -> dict[str, list[dict[str, Any]]]:
        """
        Build complete content index

        Note: Paths use relative paths from SDK root directory to avoid hardcoded absolute paths

        Returns:
            Index dictionary containing all content categories
        """
        index: dict[str, list[dict[str, Any]]] = {
            "guides": [],
            "implementation": [],
            "examples": [],
            "templates": []
        }

        # Build guide index
        readme_files = self.scan_readme_files()
        for file_path in readme_files:
            index["guides"].append({
                "type": "guide",
                "path": self._to_relative_path(file_path),
                "name": file_path.name,
                "category": self._categorize_guide(file_path)
            })

        # Build implementation index
        impl_files = self.scan_implementation_files()
        for file_path in impl_files:
            index["implementation"].append({
                "type": "implementation",
                "path": self._to_relative_path(file_path),
                "name": file_path.name,
                "category": self._categorize_implementation(file_path)
            })

        # Build example index
        sample_files = self.scan_sample_files()
        for file_path in sample_files:
            index["examples"].append({
                "type": "example",
                "path": self._to_relative_path(file_path),
                "name": file_path.name,
                "category": self._categorize_sample(file_path)
            })

        # Build template index
        template_files = self.scan_template_files()
        for file_path in template_files:
            index["templates"].append({
                "type": "template",
                "path": self._to_relative_path(file_path),
                "name": file_path.name,
                "category": self._categorize_template(file_path)
            })

        return index

    def _to_relative_path(self, file_path: Path) -> str:
        """Convert absolute path to relative path from SDK root directory"""
        try:
            return str(file_path.relative_to(self.sdk_path))
        except ValueError:
            # If relative path cannot be calculated, return original path
            return str(file_path)

    def _categorize_guide(self, file_path: Path) -> str:
        """Categorize guide file"""
        if "Python Templates" in str(file_path):
            return "template_guide"
        elif "Python Samples" in str(file_path):
            return "sample_guide"
        else:
            return "general_guide"

    def _categorize_implementation(self, file_path: Path) -> str:
        """Categorize implementation file"""
        if "plugins.py" in file_path.name:
            return "plugin_framework"
        elif "drawingTools.py" in file_path.name:
            return "drawing_tools"
        elif "UI" in str(file_path):
            return "ui_components"
        else:
            return "other_implementation"

    def _categorize_sample(self, file_path: Path) -> str:
        """Categorize sample file"""
        path_str = str(file_path)
        if "Tool" in path_str:
            return "tool_sample"
        elif "Plugin" in path_str:
            return "plugin_sample"
        else:
            return "other_sample"

    def _categorize_template(self, file_path: Path) -> str:
        """Categorize template file"""
        path_str = str(file_path)
        if "Filter" in path_str:
            return "filter_template"
        elif "Reporter" in path_str:
            return "reporter_template"
        elif "Tool" in path_str:
            return "tool_template"
        elif "Palette" in path_str:
            return "palette_template"
        elif "General" in path_str:
            return "general_template"
        else:
            return "other_template"
