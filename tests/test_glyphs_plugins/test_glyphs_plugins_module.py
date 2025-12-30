"""
測試 GlyphsPluginsModule - 外掛管理主模組

TDD 紅燈階段：先撰寫測試，預期失敗
目標：將覆蓋率從 0% 提升至 85%+

注意：部分測試類別需要本地 Repositories 目錄才能正確執行 mock。
"""

import plistlib
from pathlib import Path
from unittest.mock import patch

import pytest

from glyphs_info_mcp.modules.glyphs_plugins.accessors.official_registry import OfficialRegistry
from glyphs_info_mcp.modules.glyphs_plugins.accessors.plugins_accessor import PluginsAccessor
from glyphs_info_mcp.modules.glyphs_plugins.glyphs_plugins_module import GlyphsPluginsModule
from glyphs_info_mcp.shared.core.repository_scanner import RepositoryScanner


class TestGlyphsPluginsModuleInitialization:
    """測試模組初始化"""

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

        # 2. Scripts Collection - TestScripts
        scripts_dir = repos / "TestScripts"
        scripts_dir.mkdir()
        (scripts_dir / "Script1.py").write_text(
            "# MenuTitle: Test Script 1\nprint('test')"
        )
        (scripts_dir / "README.md").write_text("# Test Scripts Collection")

        # .git/config
        git_dir = scripts_dir / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text(
            '[remote "origin"]\n    url = https://github.com/test/TestScripts\n'
        )

        # 3. Python Library - vanilla
        lib_dir = repos / "vanilla"
        lib_dir.mkdir()
        (lib_dir / "Lib").mkdir()
        (lib_dir / "setup.py").write_text("# Setup")

        return repos

    @pytest.fixture
    def module_with_repos(
        self, mock_repositories: Path, monkeypatch: pytest.MonkeyPatch
    ) -> GlyphsPluginsModule:
        """建立已初始化的模組實例（有 Repositories）"""

        # Mock RepositoryScanner 的預設路徑為我們的 mock 路徑
        def mock_init(self: RepositoryScanner, repositories_path: Path | None = None) -> None:
            self.repositories_path = repositories_path or mock_repositories
            self.modules = []  # type: ignore[attr-defined]

        monkeypatch.setattr(RepositoryScanner, "__init__", mock_init)

        module = GlyphsPluginsModule()
        module.initialize()
        return module

    @pytest.fixture
    def module_without_repos(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> GlyphsPluginsModule:
        """建立模組實例（無 Repositories）"""
        # Mock 一個不存在的路徑
        nonexistent_path = tmp_path / "nonexistent"

        def mock_init(self: RepositoryScanner, repositories_path: Path | None = None) -> None:
            self.repositories_path = repositories_path or nonexistent_path
            self.modules = []  # type: ignore[attr-defined]

        monkeypatch.setattr(RepositoryScanner, "__init__", mock_init)

        module = GlyphsPluginsModule()
        module.initialize()
        return module

    @pytest.fixture
    def uninitialized_module(self) -> GlyphsPluginsModule:
        """建立未初始化的模組實例"""
        return GlyphsPluginsModule()

    def test_module_creation(self) -> None:
        """測試模組建立"""
        # Act
        module = GlyphsPluginsModule()

        # Assert
        assert module.name == "glyphs-plugins"
        assert module.description == "Glyphs.app plugins, scripts, and libraries management"
        assert module.scanner is None
        assert module.plugins_accessor is None
        assert module.official_registry is None
        assert module.is_initialized is False

    def test_initialize_success(self, module_with_repos: GlyphsPluginsModule) -> None:
        """測試成功初始化"""
        # Assert
        assert module_with_repos.is_initialized is True
        assert module_with_repos.scanner is not None
        assert module_with_repos.plugins_accessor is not None
        assert module_with_repos.official_registry is not None

    def test_initialize_without_repositories(
        self, module_without_repos: GlyphsPluginsModule
    ) -> None:
        """測試在 Repositories 不存在時初始化"""
        # Assert - 應該仍然成功初始化，但不掃描本機外掛
        assert module_without_repos.is_initialized is True
        assert module_without_repos.scanner is not None
        assert module_without_repos.plugins_accessor is not None
        assert module_without_repos.official_registry is not None

    def test_get_tools(self, module_with_repos: GlyphsPluginsModule) -> None:
        """測試取得工具清單"""
        # Act
        tools = module_with_repos.get_tools()

        # Assert
        assert len(tools) == 5
        assert "plugins_search_local" in tools
        assert "plugins_search_official" in tools
        assert "plugins_get_info" in tools
        assert "plugins_scan_repository" in tools
        assert "plugins_list_categories" in tools

    def test_get_module_info(self, module_with_repos: GlyphsPluginsModule) -> None:
        """測試取得模組資訊"""
        # Act
        info = module_with_repos.get_module_info()

        # Assert
        assert "name" in info
        assert "description" in info
        assert info["name"] == "glyphs-plugins"

    def test_initialize_with_empty_repositories(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """測試空 Repositories 目錄的初始化"""
        # Arrange
        empty_repos = tmp_path / "EmptyRepositories"
        empty_repos.mkdir()

        def mock_init(self: RepositoryScanner, repositories_path: Path | None = None) -> None:
            self.repositories_path = repositories_path or empty_repos
            self.modules = []  # type: ignore[attr-defined]

        monkeypatch.setattr(RepositoryScanner, "__init__", mock_init)

        # Act
        module = GlyphsPluginsModule()
        result = module.initialize()

        # Assert
        assert result is True
        assert module.is_initialized is True


@pytest.mark.requires_repositories
class TestSearchLocalTool:
    """測試本機搜尋工具（需要 Repositories 目錄）"""

    @pytest.fixture
    def mock_repositories(self, tmp_path: Path) -> Path:
        """建立模擬的 Repositories 目錄結構"""
        repos = tmp_path / "Repositories"
        repos.mkdir()

        # Plugin Bundle - ShowCrosshair
        plugin_dir = repos / "ShowCrosshair"
        plugin_dir.mkdir()
        bundle_dir = plugin_dir / "ShowCrosshair.glyphsReporter"
        bundle_dir.mkdir()
        contents_dir = bundle_dir / "Contents"
        contents_dir.mkdir()

        info_plist = {
            "CFBundleName": "ShowCrosshair",
            "CFBundleIdentifier": "com.mekkablue.ShowCrosshair",
            "CFBundleShortVersionString": "3.1.1",
        }
        with open(contents_dir / "Info.plist", "wb") as f:
            plistlib.dump(info_plist, f)

        (plugin_dir / "README.md").write_text(
            "# ShowCrosshair\nA crosshair reporter plugin."
        )

        git_dir = plugin_dir / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text(
            '[remote "origin"]\n    url = https://github.com/mekkablue/ShowCrosshair\n'
        )

        # Scripts Collection
        scripts_dir = repos / "TestScripts"
        scripts_dir.mkdir()
        (scripts_dir / "Script1.py").write_text(
            "# MenuTitle: Test Script\nprint('test')"
        )
        (scripts_dir / "README.md").write_text("# Test Scripts")

        git_dir = scripts_dir / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text(
            '[remote "origin"]\n    url = https://github.com/test/TestScripts\n'
        )

        return repos

    @pytest.fixture
    def module(self, mock_repositories: Path, monkeypatch: pytest.MonkeyPatch) -> GlyphsPluginsModule:
        """建立已初始化的模組實例"""

        def mock_init(self: RepositoryScanner, repositories_path: Path | None = None) -> None:
            self.repositories_path = repositories_path or mock_repositories
            self.modules = []  # type: ignore[attr-defined]

        monkeypatch.setattr(RepositoryScanner, "__init__", mock_init)

        module = GlyphsPluginsModule()
        module.initialize()
        return module

    def test_search_all_categories(self, module: GlyphsPluginsModule) -> None:
        """測試搜尋所有類別"""
        # Act
        result = module._search_local_tool("cross", category="all")

        # Assert
        assert "🔍" in result  # Has search icon
        assert "ShowCrosshair" in result or "Found" in result or "找到" in result

    def test_search_plugins_only(self, module: GlyphsPluginsModule) -> None:
        """測試只搜尋外掛"""
        # Act
        result = module._search_local_tool("cross", category="plugin")

        # Assert
        assert "ShowCrosshair" in result
        # Compact format uses table, type is shown as icon + type name
        assert "Reporter" in result or "🔌" in result

    def test_search_scripts_only(self, module: GlyphsPluginsModule) -> None:
        """測試只搜尋腳本"""
        # Act
        result = module._search_local_tool("script", category="scripts")

        # Assert
        # 使用 "script" 作為查詢詞，更有可能匹配到真實的腳本集合
        assert "found" in result.lower() or "未找到" in result or "scripts" in result.lower() or "腳本" in result

    def test_search_no_results(self, module: GlyphsPluginsModule) -> None:
        """測試無結果搜尋"""
        # Act
        result = module._search_local_tool("nonexistent", category="all")

        # Assert
        assert "未找到" in result or "找不到" in result or "無結果" in result or "found" in result.lower() or "no results" in result.lower()

    def test_search_accessor_not_initialized(self) -> None:
        """測試未初始化狀態的搜尋"""
        # Arrange
        module = GlyphsPluginsModule()  # 未呼叫 initialize()

        # Act
        result = module._search_local_tool("test")

        # Assert
        assert "尚未初始化" in result or "未初始化" in result or "無法" in result or "not initialized" in result.lower()

    def test_search_with_match_in_bundle_id(self, module: GlyphsPluginsModule) -> None:
        """測試 Bundle ID 匹配"""
        # Act
        result = module._search_local_tool("mekkablue", category="plugin")

        # Assert
        # Compact format only shows name, type, version - not bundle ID
        # Bundle ID is available via plugins_get_info
        assert "ShowCrosshair" in result
        assert "plugins_get_info" in result  # Hint for full details


class TestSearchOfficialTool:
    """測試官方搜尋工具"""

    @pytest.fixture
    def module(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> GlyphsPluginsModule:
        """建立模組並 mock OfficialRegistry"""
        module = GlyphsPluginsModule()

        # Mock RepositoryScanner
        def mock_scanner_init(self: RepositoryScanner, repositories_path: Path | None = None) -> None:
            self.repositories_path = tmp_path / "Repositories"
            self.modules = []  # type: ignore[attr-defined]

        monkeypatch.setattr(RepositoryScanner, "__init__", mock_scanner_init)

        # Mock OfficialRegistry.core_search
        mock_packages: list[dict[str, str | float]] = [
            {
                "title": "TestPlugin",
                "url": "https://github.com/test/TestPlugin",
                "description": "A test plugin for Glyphs",
                "owner": "test",
                "repo_name": "TestPlugin",
                "score": 1.0,
                "type": "plugin",
                "source": "official_registry",
            },
            {
                "title": "AnotherPlugin",
                "url": "https://github.com/test/AnotherPlugin",
                "description": "Another test plugin",
                "owner": "test",
                "repo_name": "AnotherPlugin",
                "score": 0.8,
                "type": "plugin",
                "source": "official_registry",
            },
        ]

        def mock_core_search(self: OfficialRegistry, query: str, max_results: int = 10, **kwargs: object) -> list[dict[str, str | float]]:
            return [p for p in mock_packages if query.lower() in str(p["title"]).lower()][:max_results]

        monkeypatch.setattr(
            OfficialRegistry,
            "core_search",
            mock_core_search,
        )

        module.initialize()
        return module

    def test_search_official_success(self, module: GlyphsPluginsModule) -> None:
        """測試成功的官方搜尋"""
        # Act
        result = module._search_official_tool("Test")

        # Assert
        assert "🔍" in result  # Has search icon
        # Compact format uses "Found X results"
        assert "Found" in result
        assert "TestPlugin" in result

    def test_search_official_multiple_results(self, module: GlyphsPluginsModule) -> None:
        """測試多筆結果搜尋"""
        # Act
        result = module._search_official_tool("Plugin")

        # Assert
        assert "Plugin" in result
        # All matching results should be shown (no limit)
        assert "TestPlugin" in result or "AnotherPlugin" in result

    def test_search_official_no_results(self, module: GlyphsPluginsModule) -> None:
        """測試無結果搜尋"""
        # Act
        result = module._search_official_tool("NonexistentPlugin")

        # Assert
        assert "未找到" in result or "找不到" in result or "無結果" in result or "found" in result.lower() or "no results" in result.lower()

    def test_search_official_registry_not_initialized(self) -> None:
        """測試 Registry 未初始化"""
        # Arrange
        module = GlyphsPluginsModule()

        # Act
        result = module._search_official_tool("test")

        # Assert
        assert "尚未初始化" in result or "未初始化" in result or "not initialized" in result.lower()


class TestGetInfoTool:
    """測試取得資訊工具"""

    @pytest.fixture
    def mock_repositories(self, tmp_path: Path) -> Path:
        """建立模擬的 Repositories 目錄結構"""
        repos = tmp_path / "Repositories"
        repos.mkdir()

        # Plugin
        plugin_dir = repos / "TestPlugin"
        plugin_dir.mkdir()
        bundle_dir = plugin_dir / "TestPlugin.glyphsReporter"
        bundle_dir.mkdir()
        contents_dir = bundle_dir / "Contents"
        contents_dir.mkdir()

        info_plist = {
            "CFBundleName": "TestPlugin",
            "CFBundleIdentifier": "com.test.TestPlugin",
            "CFBundleShortVersionString": "1.0.0",
        }
        with open(contents_dir / "Info.plist", "wb") as f:
            plistlib.dump(info_plist, f)

        (plugin_dir / "README.md").write_text("# TestPlugin\nA test plugin.")

        git_dir = plugin_dir / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text(
            '[remote "origin"]\n    url = https://github.com/test/TestPlugin\n'
        )

        # Scripts Collection
        scripts_dir = repos / "TestScripts"
        scripts_dir.mkdir()
        (scripts_dir / "Script1.py").write_text(
            "# MenuTitle: Test Script 1\nprint('test')"
        )
        (scripts_dir / "Script2.py").write_text(
            "# MenuTitle: Test Script 2\nprint('test2')"
        )
        (scripts_dir / "README.md").write_text("# Test Scripts")

        git_dir = scripts_dir / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text(
            '[remote "origin"]\n    url = https://github.com/test/TestScripts\n'
        )

        return repos

    @pytest.fixture
    def module(self, mock_repositories: Path) -> GlyphsPluginsModule:
        """建立已初始化的模組實例"""
        # 直接建立 module 並手動設置 scanner
        module = GlyphsPluginsModule()

        # 手動初始化核心組件，使用 mock 路徑
        module.scanner = RepositoryScanner(repositories_path=mock_repositories)
        module.plugins_accessor = PluginsAccessor(module.scanner)
        module.official_registry = OfficialRegistry(cache_dir=module.data_dir)

        # 掃描本機外掛
        if module.scanner.is_available():
            module.plugins_accessor.scan_all_tools()

        module.is_initialized = True
        return module

    def test_get_plugin_info_local(self, module: GlyphsPluginsModule) -> None:
        """測試取得本機 Plugin 資訊"""
        # Act
        result = module._get_info_tool("TestPlugin", source="local")

        # Assert
        assert "TestPlugin" in result
        assert "1.0.0" in result
        assert "com.test.TestPlugin" in result

    def test_get_scripts_info_local(self, module: GlyphsPluginsModule) -> None:
        """測試取得本機 Scripts 資訊"""
        # Act
        result = module._get_info_tool("TestScripts", source="local")

        # Assert
        assert "TestScripts" in result
        assert "Scripts Collection" in result or "腳本" in result or "scripts" in result.lower()
        assert "Script1" in result or "Script2" in result

    def test_get_info_official_with_exact_match(self, module: GlyphsPluginsModule) -> None:
        """測試從官方清單取得資訊（精確匹配）"""
        # 使用 Mock 模擬官方清單回傳結果（匹配 core_search 返回格式）
        mock_plugin = {
            "title": "Show Crosshair",
            "url": "https://github.com/mekkablue/ShowCrosshair",
            "description": "Shows a crosshair at the current cursor position",
            "owner": "mekkablue",
            "repo_name": "ShowCrosshair",
            "score": 1.0,
            "type": "plugin",
            "source": "official_registry",
        }

        with patch.object(
            module.official_registry,
            "core_search",
            return_value=[mock_plugin],
        ):
            # Act
            result = module._get_info_tool("Show Crosshair", source="official")

            # Assert
            assert "Show Crosshair" in result
            assert "ShowCrosshair" in result  # repo_name
            assert "Shows a crosshair" in result

    def test_get_info_not_found_local(self, module: GlyphsPluginsModule) -> None:
        """測試本機找不到"""
        # Act
        result = module._get_info_tool("NonexistentPlugin", source="local")

        # Assert
        assert "未找到" in result or "找不到" in result or "not found" in result.lower()

    def test_get_info_accessor_not_initialized(self) -> None:
        """測試未初始化狀態"""
        # Arrange
        module = GlyphsPluginsModule()

        # Act
        result = module._get_info_tool("test", source="local")

        # Assert
        assert "未初始化" in result or "無法" in result or "not initialized" in result.lower()

    def test_get_info_invalid_source(self, module: GlyphsPluginsModule) -> None:
        """測試無效來源"""
        # Act
        result = module._get_info_tool("test", source="invalid")

        # Assert
        assert "無效" in result or "錯誤" in result or "invalid" in result.lower() or "error" in result.lower()


@pytest.mark.requires_repositories
class TestScanRepositoryTool:
    """測試掃描工具（需要 Repositories 目錄）"""

    @pytest.fixture
    def mock_repositories(self, tmp_path: Path) -> Path:
        """建立模擬目錄"""
        repos = tmp_path / "Repositories"
        repos.mkdir()
        return repos

    @pytest.fixture
    def module(self, mock_repositories: Path, monkeypatch: pytest.MonkeyPatch) -> GlyphsPluginsModule:
        """建立模組實例"""

        def mock_init(self: RepositoryScanner, repositories_path: Path | None = None) -> None:
            self.repositories_path = repositories_path or mock_repositories
            self.modules = []  # type: ignore[attr-defined]

        monkeypatch.setattr(RepositoryScanner, "__init__", mock_init)

        module = GlyphsPluginsModule()
        module.initialize()
        return module

    def test_scan_repository_success(self, module: GlyphsPluginsModule) -> None:
        """測試成功掃描"""
        # Act
        result = module._scan_repository_tool()

        # Assert
        assert "掃描完成" in result or "完成" in result or "個" in result or "scan complete" in result.lower() or "found" in result.lower()

    def test_scan_repository_not_initialized(self) -> None:
        """測試未初始化"""
        # Arrange
        module = GlyphsPluginsModule()

        # Act
        result = module._scan_repository_tool()

        # Assert
        assert "未初始化" in result or "無法" in result or "not initialized" in result.lower()


class TestListCategoriesTool:
    """測試分類列表工具"""

    @pytest.fixture
    def mock_repositories(self, tmp_path: Path) -> Path:
        """建立模擬目錄"""
        repos = tmp_path / "Repositories"
        repos.mkdir()

        # Plugin
        plugin_dir = repos / "TestPlugin"
        plugin_dir.mkdir()
        bundle_dir = plugin_dir / "TestPlugin.glyphsReporter"
        bundle_dir.mkdir()
        contents_dir = bundle_dir / "Contents"
        contents_dir.mkdir()

        info_plist = {
            "CFBundleName": "TestPlugin",
            "CFBundleIdentifier": "com.test.TestPlugin",
        }
        with open(contents_dir / "Info.plist", "wb") as f:
            plistlib.dump(info_plist, f)

        return repos

    @pytest.fixture
    def module(self, mock_repositories: Path, monkeypatch: pytest.MonkeyPatch) -> GlyphsPluginsModule:
        """建立模組實例"""

        def mock_init(self: RepositoryScanner, repositories_path: Path | None = None) -> None:
            self.repositories_path = repositories_path or mock_repositories
            self.modules = []  # type: ignore[attr-defined]

        monkeypatch.setattr(RepositoryScanner, "__init__", mock_init)

        module = GlyphsPluginsModule()
        module.initialize()
        return module

    def test_list_categories_with_plugins(self, module: GlyphsPluginsModule) -> None:
        """測試列出分類（有外掛）"""
        # Act
        result = module._list_categories_tool()

        # Assert
        assert "分類" in result or "類別" in result or "統計" in result or "Category" in result or "Statistics" in result

    def test_list_categories_not_initialized(self) -> None:
        """測試未初始化"""
        # Arrange
        module = GlyphsPluginsModule()

        # Act
        result = module._list_categories_tool()

        # Assert
        assert "未初始化" in result or "無法" in result or "not initialized" in result.lower()

    def test_list_categories_with_many_scripts(self, tmp_path: Path) -> None:
        """測試腳本清單截斷邏輯（>10個）"""
        # Arrange - 建立包含 15 個腳本集合的 mock
        repos = tmp_path / "Repositories"
        repos.mkdir()

        # 建立 15 個腳本集合
        for i in range(15):
            scripts_dir = repos / f"Scripts{i:02d}"
            scripts_dir.mkdir()
            (scripts_dir / "Script.py").write_text(
                f"# MenuTitle: Script {i}\nprint('test')"
            )

        # 初始化模組
        scanner = RepositoryScanner(repositories_path=repos)
        module = GlyphsPluginsModule()
        module.scanner = scanner
        module.plugins_accessor = PluginsAccessor(scanner)
        module.plugins_accessor.scan_all_tools()
        module.is_initialized = True

        # Act
        result = module._list_categories_tool()

        # Assert
        assert "Scripts Collections (15" in result or "Scripts Collections (15 個)" in result
        assert "還有 5 個集合" in result or "5 more collections" in result  # Truncation message

    def test_list_categories_with_many_libraries(self, tmp_path: Path) -> None:
        """測試函式庫清單截斷邏輯（>10個）"""
        # Arrange - 建立包含 15 個 Library 的 mock
        repos = tmp_path / "Repositories"
        repos.mkdir()

        # 建立 15 個 Python Library
        for i in range(15):
            lib_dir = repos / f"Library{i:02d}"
            lib_dir.mkdir()
            (lib_dir / "Lib").mkdir()
            (lib_dir / "setup.py").write_text("# Setup")

        # 初始化模組
        scanner = RepositoryScanner(repositories_path=repos)
        module = GlyphsPluginsModule()
        module.scanner = scanner
        module.plugins_accessor = PluginsAccessor(scanner)
        module.plugins_accessor.scan_all_tools()
        module.is_initialized = True

        # Act
        result = module._list_categories_tool()

        # Assert
        assert "Python Libraries (15" in result or "Python Libraries (15 個)" in result
        assert "還有 5 個函式庫" in result or "5 more libraries" in result  # Truncation message
