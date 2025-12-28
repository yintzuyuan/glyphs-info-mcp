"""
測試 GlyphsPluginsModule 的增強功能
- 檔案清單列舉
- 外掛原始碼讀取

TDD 紅燈階段：先撰寫測試，預期失敗
"""

import plistlib
from pathlib import Path

import pytest

from glyphs_info_mcp.modules.glyphs_plugins.glyphs_plugins_module import GlyphsPluginsModule
from glyphs_info_mcp.shared.core.repository_scanner import RepositoryScanner


class TestPluginsEnhancedFeatures:
    """測試外掛探索增強功能"""

    @pytest.fixture
    def mock_plugin_with_source(self, tmp_path: Path) -> Path:
        """建立包含完整結構的模擬外掛"""
        repos = tmp_path / "Repositories"
        repos.mkdir()

        # 建立 ShowCrosshair 外掛結構
        plugin_dir = repos / "ShowCrosshair"
        plugin_dir.mkdir()

        # Bundle 目錄
        bundle_dir = plugin_dir / "ShowCrosshair.glyphsReporter"
        bundle_dir.mkdir()
        contents_dir = bundle_dir / "Contents"
        contents_dir.mkdir()
        resources_dir = contents_dir / "Resources"
        resources_dir.mkdir()

        # Info.plist
        info_plist = {
            "CFBundleName": "ShowCrosshair",
            "CFBundleIdentifier": "com.mekkablue.ShowCrosshair",
            "CFBundleShortVersionString": "2.5",
        }
        with open(contents_dir / "Info.plist", "wb") as f:
            plistlib.dump(info_plist, f)

        # plugin.py
        plugin_source = """# encoding: utf-8
from GlyphsApp.plugins import ReporterPlugin

class ShowCrosshair(ReporterPlugin):
    def settings(self):
        self.menuName = "Show Crosshair"

    def background(self, layer):
        # Draw crosshair
        pass
"""
        (resources_dir / "plugin.py").write_text(plugin_source, encoding="utf-8")

        # README.md
        (plugin_dir / "README.md").write_text("# ShowCrosshair\n\nA crosshair plugin.")

        # LICENSE
        (plugin_dir / "LICENSE").write_text("MIT License")

        # .git/config
        git_dir = plugin_dir / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text(
            '[remote "origin"]\n    url = https://github.com/mekkablue/ShowCrosshair\n'
        )

        return repos

    @pytest.fixture
    def module_with_mock_plugin(
        self, mock_plugin_with_source: Path
    ) -> GlyphsPluginsModule:
        """建立帶有模擬外掛的模組實例"""
        from glyphs_info_mcp.modules.glyphs_plugins.accessors.plugins_accessor import PluginsAccessor

        scanner = RepositoryScanner(repositories_path=mock_plugin_with_source)
        module = GlyphsPluginsModule()
        module.scanner = scanner
        module.plugins_accessor = PluginsAccessor(scanner)
        module.plugins_accessor.scan_all_tools()  # 掃描外掛
        return module

    def test_list_plugin_files(self, module_with_mock_plugin: GlyphsPluginsModule):
        """測試列出外掛檔案清單"""
        # Arrange
        module = module_with_mock_plugin

        # Act
        plugin_path = module.plugins_accessor.get_plugin_info("ShowCrosshair").path
        result = module._list_plugin_files(plugin_path)

        # Assert
        assert "ShowCrosshair.glyphsReporter/Contents/Info.plist" in result
        assert "ShowCrosshair.glyphsReporter/Contents/Resources/plugin.py" in result
        assert "README.md" in result
        assert "LICENSE" in result
        assert ".git" not in result  # 應排除 .git 目錄

    def test_get_plugin_source(self, module_with_mock_plugin: GlyphsPluginsModule):
        """測試讀取外掛原始碼"""
        # Arrange
        module = module_with_mock_plugin

        # Act
        plugin_path = module.plugins_accessor.get_plugin_info("ShowCrosshair").path
        result = module._get_plugin_source(plugin_path)

        # Assert
        assert "```python" in result
        assert "class ShowCrosshair(ReporterPlugin)" in result
        assert "def settings(self)" in result
        assert "def background(self, layer)" in result

    def test_get_plugin_source_not_found(
        self, module_with_mock_plugin: GlyphsPluginsModule, tmp_path: Path
    ):
        """測試當 plugin.py 不存在時的處理"""
        # Arrange
        module = module_with_mock_plugin
        empty_dir = tmp_path / "empty_plugin"
        empty_dir.mkdir()

        # Act
        result = module._get_plugin_source(empty_dir)

        # Assert - accepts "not found" or "No source files found"
        assert "未找到" in result or "found" in result.lower()

    def test_get_info_with_files(self, module_with_mock_plugin: GlyphsPluginsModule):
        """測試 _get_info_tool 的 include_files 參數"""
        # Arrange
        module = module_with_mock_plugin

        # Act
        result = module._get_info_tool("ShowCrosshair", "local", include_files=True)

        # Assert
        assert "📁" in result or "Files" in result or "File Structure" in result
        assert "plugin.py" in result
        assert "README.md" in result

    def test_get_info_with_source(self, module_with_mock_plugin: GlyphsPluginsModule):
        """測試 _get_info_tool 的 include_source 參數"""
        # Arrange
        module = module_with_mock_plugin

        # Act
        result = module._get_info_tool("ShowCrosshair", "local", include_source=True)

        # Assert
        assert "💻" in result or "Source Code" in result or "Plugin Source" in result
        assert "```python" in result
        assert "class ShowCrosshair" in result

    def test_get_info_with_both_options(
        self, module_with_mock_plugin: GlyphsPluginsModule
    ):
        """測試同時啟用 include_files 和 include_source"""
        # Arrange
        module = module_with_mock_plugin

        # Act
        result = module._get_info_tool(
            "ShowCrosshair", "local", include_files=True, include_source=True
        )

        # Assert
        assert "📁" in result or "Files" in result or "File Structure" in result
        assert "💻" in result or "Source Code" in result or "Plugin Source" in result
        assert "README.md" in result
        assert "class ShowCrosshair" in result

    def test_get_info_backward_compatible(
        self, module_with_mock_plugin: GlyphsPluginsModule
    ):
        """測試向後相容性（不傳入新參數）"""
        # Arrange
        module = module_with_mock_plugin

        # Act - 不使用新參數
        result = module._get_info_tool("ShowCrosshair", "local")

        # Assert - 應該只有基本資訊，不包含檔案清單和原始碼
        assert "ShowCrosshair" in result
        assert "Reporter" in result
        # Should not contain file structure or source code sections
        assert "📁 檔案結構" not in result and "File Structure" not in result
        assert "💻 外掛原始碼" not in result and "Plugin Source Code" not in result


class TestMultiFileSourceSupport:
    """測試多檔案原始碼支援（Python + Objective-C）"""

    @pytest.fixture
    def objc_plugin(self, tmp_path: Path) -> Path:
        """建立 Objective-C 外掛"""
        repos = tmp_path / "Repositories"
        repos.mkdir()

        plugin_dir = repos / "ObjCPlugin"
        plugin_dir.mkdir()

        bundle_dir = plugin_dir / "ObjCPlugin.glyphsReporter"
        bundle_dir.mkdir()
        contents_dir = bundle_dir / "Contents"
        contents_dir.mkdir()
        resources_dir = contents_dir / "Resources"
        resources_dir.mkdir()

        # Info.plist
        info_plist = {
            "CFBundleName": "ObjCPlugin",
            "CFBundleIdentifier": "com.test.ObjCPlugin",
            "CFBundleShortVersionString": "1.0",
        }
        with open(contents_dir / "Info.plist", "wb") as f:
            plistlib.dump(info_plist, f)

        # ObjCPlugin.h
        (resources_dir / "ObjCPlugin.h").write_text(
            "#import <Cocoa/Cocoa.h>\n@interface ObjCPlugin : NSObject\n@end\n",
            encoding="utf-8",
        )

        # ObjCPlugin.m
        (resources_dir / "ObjCPlugin.m").write_text(
            '#import "ObjCPlugin.h"\n@implementation ObjCPlugin\n@end\n',
            encoding="utf-8",
        )

        return repos

    @pytest.fixture
    def mixed_plugin(self, tmp_path: Path) -> Path:
        """建立混合外掛（Python + Objective-C）"""
        repos = tmp_path / "Repositories"
        repos.mkdir()

        plugin_dir = repos / "MixedPlugin"
        plugin_dir.mkdir()

        bundle_dir = plugin_dir / "MixedPlugin.glyphsReporter"
        bundle_dir.mkdir()
        contents_dir = bundle_dir / "Contents"
        contents_dir.mkdir()
        resources_dir = contents_dir / "Resources"
        resources_dir.mkdir()

        # Info.plist
        info_plist = {
            "CFBundleName": "MixedPlugin",
            "CFBundleIdentifier": "com.test.MixedPlugin",
            "CFBundleShortVersionString": "1.0",
        }
        with open(contents_dir / "Info.plist", "wb") as f:
            plistlib.dump(info_plist, f)

        # Python files
        (resources_dir / "plugin.py").write_text(
            "# encoding: utf-8\nclass MixedPlugin:\n    pass\n", encoding="utf-8"
        )
        (resources_dir / "helper.py").write_text(
            "def helper():\n    return True\n", encoding="utf-8"
        )

        # Objective-C files
        (resources_dir / "Helper.h").write_text(
            "#import <Cocoa/Cocoa.h>\n@interface Helper : NSObject\n@end\n",
            encoding="utf-8",
        )
        (resources_dir / "Helper.m").write_text(
            '#import "Helper.h"\n@implementation Helper\n@end\n', encoding="utf-8"
        )

        # Binary stub
        (resources_dir / "MixedPlugin").write_bytes(b"\xcf\xfa\xed\xfe" + b"\x00" * 100)

        return repos

    def test_objc_plugin_source_extraction(self, objc_plugin: Path):
        """測試 Objective-C 外掛原始碼提取"""
        from glyphs_info_mcp.modules.glyphs_plugins.accessors.plugins_accessor import PluginsAccessor

        scanner = RepositoryScanner(repositories_path=objc_plugin)
        module = GlyphsPluginsModule()
        module.scanner = scanner
        module.plugins_accessor = PluginsAccessor(scanner)
        module.plugins_accessor.scan_all_tools()

        plugin_info = module.plugins_accessor.get_plugin_info("ObjCPlugin")
        result = module._get_plugin_source(plugin_info.path)

        # 應該包含 Objective-C 原始碼
        assert "### Objective-C Headers" in result
        assert "### Objective-C Implementation" in result
        assert "@interface ObjCPlugin" in result
        assert "@implementation ObjCPlugin" in result
        assert "```objc" in result

    def test_mixed_plugin_source_extraction(self, mixed_plugin: Path):
        """測試混合外掛原始碼提取"""
        from glyphs_info_mcp.modules.glyphs_plugins.accessors.plugins_accessor import PluginsAccessor

        scanner = RepositoryScanner(repositories_path=mixed_plugin)
        module = GlyphsPluginsModule()
        module.scanner = scanner
        module.plugins_accessor = PluginsAccessor(scanner)
        module.plugins_accessor.scan_all_tools()

        plugin_info = module.plugins_accessor.get_plugin_info("MixedPlugin")
        result = module._get_plugin_source(plugin_info.path)

        # Should contain both Python and Objective-C
        assert "### Python" in result or "Python Source" in result
        assert "### Objective-C Headers" in result
        assert "### Objective-C Implementation" in result
        assert "class MixedPlugin" in result
        assert "@interface Helper" in result
        assert "```python" in result
        assert "```objc" in result

    def test_multiple_python_files(self, mixed_plugin: Path):
        """測試多個 Python 檔案"""
        from glyphs_info_mcp.modules.glyphs_plugins.accessors.plugins_accessor import PluginsAccessor

        scanner = RepositoryScanner(repositories_path=mixed_plugin)
        module = GlyphsPluginsModule()
        module.scanner = scanner
        module.plugins_accessor = PluginsAccessor(scanner)
        module.plugins_accessor.scan_all_tools()

        plugin_info = module.plugins_accessor.get_plugin_info("MixedPlugin")
        result = module._get_plugin_source(plugin_info.path)

        # 應該包含兩個 Python 檔案
        assert "plugin.py" in result
        assert "helper.py" in result
        assert "class MixedPlugin" in result
        assert "def helper()" in result

    def test_binary_file_detection(self, mixed_plugin: Path):
        """測試二進位檔案識別"""
        from glyphs_info_mcp.modules.glyphs_plugins.accessors.plugins_accessor import PluginsAccessor

        scanner = RepositoryScanner(repositories_path=mixed_plugin)
        module = GlyphsPluginsModule()
        module.scanner = scanner
        module.plugins_accessor = PluginsAccessor(scanner)
        module.plugins_accessor.scan_all_tools()

        plugin_info = module.plugins_accessor.get_plugin_info("MixedPlugin")
        result = module._get_plugin_source(plugin_info.path)

        # Should identify binary files
        assert "二進位/編譯檔案" in result or "Binary/Compiled" in result
        assert "MixedPlugin" in result
        assert "bytes" in result

    def test_statistics_summary(self, mixed_plugin: Path):
        """測試統計資訊"""
        from glyphs_info_mcp.modules.glyphs_plugins.accessors.plugins_accessor import PluginsAccessor

        scanner = RepositoryScanner(repositories_path=mixed_plugin)
        module = GlyphsPluginsModule()
        module.scanner = scanner
        module.plugins_accessor = PluginsAccessor(scanner)
        module.plugins_accessor.scan_all_tools()

        plugin_info = module.plugins_accessor.get_plugin_info("MixedPlugin")
        result = module._get_plugin_source(plugin_info.path)

        # Should include statistics info
        assert "統計" in result or "Statistics" in result
        assert "檔案" in result or "files" in result.lower()
