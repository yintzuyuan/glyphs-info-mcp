"""
測試 PluginsAccessor - 本機外掛存取器

TDD 紅燈階段：先撰寫測試，預期失敗
"""

import plistlib
from pathlib import Path

import pytest

from glyphs_info_mcp.modules.glyphs_plugins.accessors.plugins_accessor import (
    PluginInfo,
    PluginsAccessor,
    ScriptsCollection,
)
from glyphs_info_mcp.shared.core.repository_scanner import RepositoryScanner


class TestPluginsAccessor:
    """測試 PluginsAccessor 類別"""

    @pytest.fixture
    def mock_repositories(self, tmp_path: Path) -> Path:
        """建立模擬的 Repositories 目錄結構"""
        repos = tmp_path / "Repositories"
        repos.mkdir()

        # 1. Plugin Bundle - ShowCrosshair
        plugin_dir = repos / "ShowCrosshair"
        plugin_dir.mkdir()
        bundle_dir = plugin_dir / "ShowCrosshair.glyphsReporter"
        bundle_dir.mkdir()
        contents_dir = bundle_dir / "Contents"
        contents_dir.mkdir()

        # Info.plist
        info_plist = {
            "CFBundleName": "ShowCrosshair",
            "CFBundleIdentifier": "com.mekkablue.ShowCrosshair",
            "CFBundleShortVersionString": "3.1.1",
        }
        with open(contents_dir / "Info.plist", "wb") as f:
            plistlib.dump(info_plist, f)

        # README.md
        (plugin_dir / "README.md").write_text("# ShowCrosshair\nA crosshair plugin.")

        # .git/config
        git_dir = plugin_dir / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text(
            '[remote "origin"]\n    url = https://github.com/mekkablue/ShowCrosshair\n'
        )

        # 2. Scripts Collection - YinTzuYuan
        scripts_dir = repos / "YinTzuYuan"
        scripts_dir.mkdir()
        (scripts_dir / "Script1.py").write_text("# MenuTitle: Script 1\nprint('test')")
        (scripts_dir / "Script2.py").write_text("# Script 2")
        (scripts_dir / "README.md").write_text("# My Scripts")

        # 3. Python Library - vanilla
        lib_dir = repos / "vanilla"
        lib_dir.mkdir()
        (lib_dir / "Lib").mkdir()
        (lib_dir / "setup.py").write_text("# Setup")

        return repos

    @pytest.fixture
    def scanner(self, mock_repositories: Path) -> RepositoryScanner:
        """建立 RepositoryScanner 實例"""
        return RepositoryScanner(mock_repositories)

    @pytest.fixture
    def accessor(self, scanner: RepositoryScanner) -> PluginsAccessor:
        """建立 PluginsAccessor 實例"""
        return PluginsAccessor(scanner)

    def test_init(self, accessor: PluginsAccessor) -> None:
        """測試初始化"""
        assert accessor.scanner is not None
        assert accessor._plugins_index == {}
        assert accessor._scripts_index == {}
        assert accessor._libraries_index == {}

    def test_scan_all_tools(self, accessor: PluginsAccessor) -> None:
        """測試掃描所有工具"""
        # Act
        accessor.scan_all_tools()

        # Assert
        assert len(accessor._plugins_index) == 1  # ShowCrosshair
        assert len(accessor._scripts_index) == 1  # YinTzuYuan
        assert len(accessor._libraries_index) == 1  # vanilla

        # 驗證 Plugin
        assert "ShowCrosshair" in accessor._plugins_index
        plugin = accessor._plugins_index["ShowCrosshair"]
        assert plugin.name == "ShowCrosshair"
        assert plugin.bundle_id == "com.mekkablue.ShowCrosshair"
        assert plugin.version == "3.1.1"
        assert plugin.type == "Reporter"
        assert "crosshair" in plugin.readme.lower()

        # 驗證 Scripts Collection
        assert "YinTzuYuan" in accessor._scripts_index
        scripts = accessor._scripts_index["YinTzuYuan"]
        assert scripts.name == "YinTzuYuan"
        assert scripts.script_count == 2
        assert len(scripts.scripts) == 2

        # 驗證 Library
        assert "vanilla" in accessor._libraries_index

    def test_get_plugin_info(self, accessor: PluginsAccessor) -> None:
        """測試取得特定外掛資訊（透過目錄名稱）"""
        # Arrange
        accessor.scan_all_tools()

        # Act
        plugin = accessor.get_plugin_info("ShowCrosshair")

        # Assert
        assert plugin is not None
        assert plugin.name == "ShowCrosshair"
        assert plugin.version == "3.1.1"

    def test_get_plugin_info_by_bundle_name(self, tmp_path: Path) -> None:
        """測試透過 Bundle 名稱查詢外掛（新功能）"""
        # Arrange - 建立 variable-font-preview 結構
        repos = tmp_path / "Repositories"
        repos.mkdir()

        plugin_dir = repos / "variable-font-preview"
        plugin_dir.mkdir()

        bundle_dir = plugin_dir / "Variable Font Preview X.glyphsReporter"
        bundle_dir.mkdir()
        contents_dir = bundle_dir / "Contents"
        contents_dir.mkdir()

        info_plist = {
            "CFBundleName": "Variable Font Preview X",
            "CFBundleIdentifier": "com.markfromberg.Variable_Font_Preview_X",
            "CFBundleShortVersionString": "3.7.6",
        }
        with open(contents_dir / "Info.plist", "wb") as f:
            plistlib.dump(info_plist, f)

        scanner = RepositoryScanner(repositories_path=repos)
        accessor = PluginsAccessor(scanner)
        accessor.scan_all_tools()

        # Act - 使用 Bundle 顯示名稱查詢（不是目錄名）
        plugin = accessor.get_plugin_info("Variable Font Preview X")

        # Assert
        assert plugin is not None
        assert plugin.name == "Variable Font Preview X"
        assert plugin.version == "3.7.6"
        assert plugin.path.name == "variable-font-preview"

    def test_get_plugin_info_case_insensitive(self, tmp_path: Path) -> None:
        """測試不區分大小寫查詢"""
        # Arrange
        repos = tmp_path / "Repositories"
        repos.mkdir()

        plugin_dir = repos / "variable-font-preview"
        plugin_dir.mkdir()

        bundle_dir = plugin_dir / "Variable Font Preview X.glyphsReporter"
        bundle_dir.mkdir()
        contents_dir = bundle_dir / "Contents"
        contents_dir.mkdir()

        info_plist = {
            "CFBundleName": "Variable Font Preview X",
            "CFBundleIdentifier": "com.markfromberg.Variable_Font_Preview_X",
            "CFBundleShortVersionString": "3.7.6",
        }
        with open(contents_dir / "Info.plist", "wb") as f:
            plistlib.dump(info_plist, f)

        scanner = RepositoryScanner(repositories_path=repos)
        accessor = PluginsAccessor(scanner)
        accessor.scan_all_tools()

        # Act - 不同大小寫查詢
        plugin1 = accessor.get_plugin_info("variable font preview x")
        plugin2 = accessor.get_plugin_info("VARIABLE FONT PREVIEW X")

        # Assert
        assert plugin1 is not None
        assert plugin2 is not None
        assert plugin1.name == plugin2.name == "Variable Font Preview X"

    def test_get_plugin_info_not_found(self, accessor: PluginsAccessor) -> None:
        """測試取得不存在的外掛"""
        # Arrange
        accessor.scan_all_tools()

        # Act
        plugin = accessor.get_plugin_info("NonExistent")

        # Assert
        assert plugin is None

    def test_get_scripts_collection(self, accessor: PluginsAccessor) -> None:
        """測試取得腳本集合"""
        # Arrange
        accessor.scan_all_tools()

        # Act
        scripts = accessor.get_scripts_collection("YinTzuYuan")

        # Assert
        assert scripts is not None
        assert scripts.name == "YinTzuYuan"
        assert scripts.script_count == 2

    def test_list_all_plugins(self, accessor: PluginsAccessor) -> None:
        """測試列出所有外掛"""
        # Arrange
        accessor.scan_all_tools()

        # Act
        plugins = accessor.list_all_plugins()

        # Assert
        assert len(plugins) == 1
        assert plugins[0].name == "ShowCrosshair"

    def test_list_all_scripts(self, accessor: PluginsAccessor) -> None:
        """測試列出所有腳本集合"""
        # Arrange
        accessor.scan_all_tools()

        # Act
        scripts = accessor.list_all_scripts()

        # Assert
        assert len(scripts) == 1
        assert scripts[0].name == "YinTzuYuan"

    def test_list_all_libraries(self, accessor: PluginsAccessor) -> None:
        """測試列出所有函式庫"""
        # Arrange
        accessor.scan_all_tools()

        # Act
        libraries = accessor.list_all_libraries()

        # Assert
        assert len(libraries) == 1
        assert "vanilla" in libraries

    def test_is_plugin_bundle(
        self, accessor: PluginsAccessor, mock_repositories: Path
    ) -> None:
        """測試識別 Plugin Bundle"""
        # Arrange
        plugin_path = mock_repositories / "ShowCrosshair"

        # Act
        result = accessor._is_plugin_bundle(plugin_path)

        # Assert
        assert result is True

    def test_is_scripts_collection(
        self, accessor: PluginsAccessor, mock_repositories: Path
    ) -> None:
        """測試識別 Scripts Collection"""
        # Arrange
        scripts_path = mock_repositories / "YinTzuYuan"

        # Act
        result = accessor._is_scripts_collection(scripts_path)

        # Assert
        assert result is True

    def test_is_library(
        self, accessor: PluginsAccessor, mock_repositories: Path
    ) -> None:
        """測試識別 Python Library"""
        # Arrange
        lib_path = mock_repositories / "vanilla"

        # Act
        result = accessor._is_library(lib_path)

        # Assert
        assert result is True

    def test_infer_plugin_type(self, accessor: PluginsAccessor) -> None:
        """測試推斷外掛類型"""
        assert accessor._infer_plugin_type(".glyphsReporter") == "Reporter"
        assert accessor._infer_plugin_type(".glyphsFilter") == "Filter"
        assert accessor._infer_plugin_type(".glyphsPalette") == "Palette"
        assert accessor._infer_plugin_type(".glyphsPlugin") == "Plugin"
        assert accessor._infer_plugin_type(".glyphsTool") == "Tool"
        assert accessor._infer_plugin_type(".unknown") == "Unknown"

    def test_plugin_with_different_bundle_name(self, tmp_path: Path) -> None:
        """測試目錄名與 Bundle 名不一致的外掛（如 variable-font-preview）"""
        # Arrange - 建立 variable-font-preview 結構
        repos = tmp_path / "Repositories"
        repos.mkdir()

        plugin_dir = repos / "variable-font-preview"
        plugin_dir.mkdir()

        # Bundle 名稱與目錄不同
        bundle_dir = plugin_dir / "Variable Font Preview X.glyphsReporter"
        bundle_dir.mkdir()
        contents_dir = bundle_dir / "Contents"
        contents_dir.mkdir()

        info_plist = {
            "CFBundleName": "Variable Font Preview X",
            "CFBundleIdentifier": "com.markfromberg.Variable_Font_Preview_X",
            "CFBundleShortVersionString": "3.7.6",
        }
        with open(contents_dir / "Info.plist", "wb") as f:
            plistlib.dump(info_plist, f)

        # Act
        scanner = RepositoryScanner(repositories_path=repos)
        accessor = PluginsAccessor(scanner)
        accessor.scan_all_tools()

        # Assert
        plugins = accessor.list_all_plugins()
        assert len(plugins) == 1
        assert plugins[0].name == "Variable Font Preview X"
        assert plugins[0].bundle_id == "com.markfromberg.Variable_Font_Preview_X"
        assert plugins[0].version == "3.7.6"
        assert plugins[0].type == "Reporter"

    def test_plugin_directory_with_multiple_bundles(self, tmp_path: Path) -> None:
        """測試一個目錄包含多個 Bundle 的邊界情況"""
        # Arrange - 建立包含多個 Bundle 的目錄（極罕見但理論上可能）
        repos = tmp_path / "Repositories"
        repos.mkdir()

        plugin_dir = repos / "multi-bundle-plugin"
        plugin_dir.mkdir()

        # 第一個 Bundle
        bundle1_dir = plugin_dir / "Plugin A.glyphsReporter"
        bundle1_dir.mkdir()
        contents1_dir = bundle1_dir / "Contents"
        contents1_dir.mkdir()

        info_plist1 = {
            "CFBundleName": "Plugin A",
            "CFBundleIdentifier": "com.test.plugin_a",
            "CFBundleShortVersionString": "1.0.0",
        }
        with open(contents1_dir / "Info.plist", "wb") as f:
            plistlib.dump(info_plist1, f)

        # 第二個 Bundle（應該被忽略）
        bundle2_dir = plugin_dir / "Plugin B.glyphsReporter"
        bundle2_dir.mkdir()
        contents2_dir = bundle2_dir / "Contents"
        contents2_dir.mkdir()

        info_plist2 = {
            "CFBundleName": "Plugin B",
            "CFBundleIdentifier": "com.test.plugin_b",
            "CFBundleShortVersionString": "2.0.0",
        }
        with open(contents2_dir / "Info.plist", "wb") as f:
            plistlib.dump(info_plist2, f)

        # Act
        scanner = RepositoryScanner(repositories_path=repos)
        accessor = PluginsAccessor(scanner)
        accessor.scan_all_tools()

        # Assert - 應該只識別第一個 Bundle
        plugins = accessor.list_all_plugins()
        assert len(plugins) == 1
        # 驗證是其中一個 Bundle（根據 glob 順序可能是 A 或 B）
        assert plugins[0].name in ["Plugin A", "Plugin B"]


class TestPluginInfo:
    """測試 PluginInfo 資料類別"""

    def test_plugin_info_creation(self) -> None:
        """測試建立 PluginInfo"""
        plugin = PluginInfo(
            name="TestPlugin",
            bundle_id="com.test.plugin",
            version="1.0.0",
            type="Reporter",
            path=Path("/test/path"),
            git_url="https://github.com/test/plugin",
            readme="# Test Plugin",
        )

        assert plugin.name == "TestPlugin"
        assert plugin.bundle_id == "com.test.plugin"
        assert plugin.version == "1.0.0"
        assert plugin.type == "Reporter"
        assert plugin.git_url == "https://github.com/test/plugin"


class TestScriptsCollection:
    """測試 ScriptsCollection 資料類別"""

    def test_scripts_collection_creation(self) -> None:
        """測試建立 ScriptsCollection"""
        scripts = ScriptsCollection(
            name="TestScripts",
            path=Path("/test/scripts"),
            script_count=5,
            scripts=["script1.py", "script2.py"],
            readme="# Test Scripts",
        )

        assert scripts.name == "TestScripts"
        assert scripts.script_count == 5
        assert len(scripts.scripts) == 2
        assert scripts.readme == "# Test Scripts"
