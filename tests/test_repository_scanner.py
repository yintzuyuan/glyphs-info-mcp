#!/usr/bin/env python3
"""
測試 Repository Scanner - TDD 紅燈階段
"""


# 導入待測試的模組
import sys
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent
shared_core_path = str(project_root / "src" / "shared")
if shared_core_path not in sys.path:
    sys.path.insert(0, shared_core_path)

from glyphs_info_mcp.shared.core.repository_scanner import RepositoryScanner


class TestRepositoryScanner:
    """測試 Repository Scanner 基本功能"""

    @pytest.fixture
    def temp_repositories(self) -> Generator[Path, None, None]:
        """建立臨時 Repositories 目錄結構"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "Repositories"
            repo_path.mkdir()

            # 建立 vanilla 模組結構
            vanilla_path = repo_path / "vanilla" / "Lib" / "vanilla"
            vanilla_path.mkdir(parents=True)

            # 建立 __init__.py
            init_file = vanilla_path / "__init__.py"
            init_file.write_text(
                """
from vanilla.vanillaButton import Button
from vanilla.vanillaTextBox import TextBox

__all__ = ["Button", "TextBox"]
"""
            )

            # 建立 Button 檔案
            button_file = vanilla_path / "vanillaButton.py"
            button_file.write_text(
                '''
class Button:
    """A standard button widget."""
    def __init__(self, posSize, title, callback=None):
        pass
'''
            )

            # 建立 TextBox 檔案
            textbox_file = vanilla_path / "vanillaTextBox.py"
            textbox_file.write_text(
                '''
class TextBox:
    """A text display widget."""
    def __init__(self, posSize, text=""):
        pass
'''
            )

            yield repo_path

    def test_scanner_initialization(self, temp_repositories: Path) -> None:
        """測試 Scanner 正確初始化"""
        scanner = RepositoryScanner(temp_repositories)
        assert scanner.repositories_path == temp_repositories
        assert scanner.is_available()

    def test_scanner_initialization_nonexistent_path(self) -> None:
        """測試不存在的路徑"""
        scanner = RepositoryScanner(Path("/nonexistent/path"))
        assert not scanner.is_available()

    def test_scan_repositories(self, temp_repositories: Path) -> None:
        """測試掃描 Repositories 並找到已安裝模組"""
        scanner = RepositoryScanner(temp_repositories)
        modules = scanner.scan_repositories()

        assert "vanilla" in modules
        assert len(modules) >= 1

    def test_is_module_installed(self, temp_repositories: Path) -> None:
        """測試檢查模組是否已安裝"""
        scanner = RepositoryScanner(temp_repositories)
        scanner.scan_repositories()

        assert scanner.is_module_installed("vanilla")
        assert not scanner.is_module_installed("nonexistent_module")

    def test_get_module_path(self, temp_repositories: Path) -> None:
        """測試取得模組路徑"""
        scanner = RepositoryScanner(temp_repositories)
        scanner.scan_repositories()

        vanilla_path = scanner.get_module_path("vanilla")
        assert vanilla_path is not None
        assert vanilla_path.exists()
        assert "vanilla" in str(vanilla_path)

    def test_get_module_path_nonexistent(self, temp_repositories: Path) -> None:
        """測試取得不存在模組的路徑"""
        scanner = RepositoryScanner(temp_repositories)
        scanner.scan_repositories()

        path = scanner.get_module_path("nonexistent")
        assert path is None

    def test_get_installed_modules(self, temp_repositories: Path) -> None:
        """測試列出所有已安裝模組"""
        scanner = RepositoryScanner(temp_repositories)
        scanner.scan_repositories()

        modules = scanner.get_installed_modules()
        assert isinstance(modules, list)
        assert "vanilla" in modules

    def test_cache_mechanism(self, temp_repositories: Path) -> None:
        """測試快取機制 - 第二次呼叫不重新掃描"""
        scanner = RepositoryScanner(temp_repositories)

        # 第一次掃描
        modules1 = scanner.scan_repositories()

        # 第二次應該使用快取
        modules2 = scanner.scan_repositories()

        assert modules1 == modules2

    def test_force_rescan(self, temp_repositories: Path) -> None:
        """測試強制重新掃描"""
        scanner = RepositoryScanner(temp_repositories)

        # 第一次掃描
        scanner.scan_repositories()

        # 強制重新掃描
        modules = scanner.scan_repositories(force=True)

        assert "vanilla" in modules


class TestRepositoryScannerAutoDetection:
    """測試 Repository Scanner 自動偵測功能"""

    def test_auto_detect_glyphs3_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """測試自動偵測 Glyphs 3 路徑"""
        # 創建臨時目錄模擬 Glyphs 3
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_home = Path(tmpdir)
            mock_path = tmp_home / "Library/Application Support/Glyphs 3/Repositories"
            mock_path.mkdir(parents=True)

            # 模擬 Path.home() 返回臨時 home
            def mock_home() -> Path:
                return tmp_home

            monkeypatch.setattr(Path, "home", mock_home)

            scanner = RepositoryScanner.auto_detect()
            assert scanner is not None
            assert scanner.repositories_path == mock_path

    def test_auto_detect_with_env_var(self, monkeypatch: pytest.MonkeyPatch, temp_repositories: Path) -> None:
        """測試使用環境變數指定路徑"""
        monkeypatch.setenv("GLYPHS_REPOSITORIES_PATH", str(temp_repositories))

        scanner = RepositoryScanner.auto_detect()
        assert scanner is not None
        assert scanner.repositories_path == temp_repositories
        assert scanner.is_available()

    @pytest.fixture
    def temp_repositories(self) -> Generator[Path, None, None]:
        """建立臨時 Repositories 目錄"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "Repositories"
            repo_path.mkdir()
            yield repo_path
