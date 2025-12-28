#!/usr/bin/env python3
"""
測試 Repository Scanner 的動態路徑切換功能

測試優先順序：
1. 本地安裝（Repositories 目錄）
2. 環境變數
3. Git Submodule fallback
"""

import sys
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest

project_root = Path(__file__).parent.parent
shared_core_path = str(project_root / "src" / "shared")
if shared_core_path not in sys.path:
    sys.path.insert(0, shared_core_path)

from glyphs_info_mcp.shared.core.repository_scanner import RepositoryScanner


class TestRepositoryFallbackMechanism:
    """測試 Repository Scanner 的 Fallback 機制"""

    @pytest.fixture
    def temp_local_repo(self) -> Generator[Path, None, None]:
        """建立臨時本地 Repositories 目錄"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "Repositories"
            repo_path.mkdir()

            # 建立 mekkablue 模組
            mekkablue_path = repo_path / "mekkablue"
            mekkablue_path.mkdir()
            (mekkablue_path / "__init__.py").write_text("# mekkablue scripts")

            # 建立 vanilla 模組
            vanilla_path = repo_path / "vanilla" / "Lib" / "vanilla"
            vanilla_path.mkdir(parents=True)
            (vanilla_path / "__init__.py").write_text("# vanilla UI")

            yield repo_path

    @pytest.fixture
    def temp_fallback_paths(self) -> Generator[dict[str, Path], None, None]:
        """建立臨時 Submodule fallback 路徑"""
        with tempfile.TemporaryDirectory() as tmpdir:
            submodule_base = Path(tmpdir) / "data" / "official"
            submodule_base.mkdir(parents=True)

            # 建立 mekkablue-scripts submodule
            mekkablue_sub = submodule_base / "mekkablue-scripts"
            mekkablue_sub.mkdir()
            (mekkablue_sub / "__init__.py").write_text("# mekkablue submodule")

            # 建立 vanilla submodule
            vanilla_sub = submodule_base / "vanilla" / "Lib" / "vanilla"
            vanilla_sub.mkdir(parents=True)
            (vanilla_sub / "__init__.py").write_text("# vanilla submodule")

            yield {
                "mekkablue": mekkablue_sub,
                "vanilla": submodule_base / "vanilla",
            }

    def test_priority_1_local_installation(self, temp_local_repo: Path, temp_fallback_paths: dict[str, Path]) -> None:
        """測試優先順序 1：本地安裝優先"""
        scanner = RepositoryScanner(temp_local_repo, temp_fallback_paths)
        scanner.scan_repositories()

        # 取得模組路徑
        mekkablue_path = scanner.get_module_path("mekkablue")
        vanilla_path = scanner.get_module_path("vanilla")

        # 應該使用本地安裝的版本
        assert mekkablue_path == temp_local_repo / "mekkablue"
        assert vanilla_path == temp_local_repo / "vanilla"

    def test_priority_3_submodule_fallback(self, temp_fallback_paths: dict[str, Path]) -> None:
        """測試優先順序 3：Submodule fallback（本地未安裝）"""
        # 使用不存在的 Repositories 路徑
        nonexistent_repo = Path("/nonexistent/repositories")
        scanner = RepositoryScanner(nonexistent_repo, temp_fallback_paths)
        scanner.scan_repositories()

        # 取得模組路徑
        mekkablue_path = scanner.get_module_path("mekkablue")
        vanilla_path = scanner.get_module_path("vanilla")

        # 應該使用 Submodule fallback
        assert mekkablue_path == temp_fallback_paths["mekkablue"]
        assert vanilla_path == temp_fallback_paths["vanilla"]

    def test_priority_2_environment_variable(
        self, monkeypatch: pytest.MonkeyPatch, temp_local_repo: Path, temp_fallback_paths: dict[str, Path]
    ) -> None:
        """測試優先順序 2：環境變數（本地安裝不存在時）"""
        # 建立環境變數指定的路徑
        with tempfile.TemporaryDirectory() as tmpdir:
            env_mekkablue = Path(tmpdir) / "env_mekkablue"
            env_mekkablue.mkdir()
            (env_mekkablue / "__init__.py").write_text("# env mekkablue")

            # 設定環境變數
            monkeypatch.setenv("GLYPHS_MEKKABLUE_PATH", str(env_mekkablue))

            # 使用空的 Repositories（本地未安裝）
            empty_repo = Path(tmpdir) / "empty_repositories"
            empty_repo.mkdir()

            scanner = RepositoryScanner(empty_repo, temp_fallback_paths)
            scanner.scan_repositories()

            # 取得模組路徑
            mekkablue_path = scanner.get_module_path("mekkablue")

            # 應該使用環境變數指定的路徑
            assert mekkablue_path == env_mekkablue

    def test_local_overrides_environment_variable(
        self, monkeypatch: pytest.MonkeyPatch, temp_local_repo: Path, temp_fallback_paths: dict[str, Path]
    ) -> None:
        """測試本地安裝優先於環境變數"""
        # 建立環境變數路徑
        with tempfile.TemporaryDirectory() as tmpdir:
            env_mekkablue = Path(tmpdir) / "env_mekkablue"
            env_mekkablue.mkdir()

            # 設定環境變數
            monkeypatch.setenv("GLYPHS_MEKKABLUE_PATH", str(env_mekkablue))

            scanner = RepositoryScanner(temp_local_repo, temp_fallback_paths)
            scanner.scan_repositories()

            mekkablue_path = scanner.get_module_path("mekkablue")

            # 本地安裝應該優先於環境變數
            assert mekkablue_path == temp_local_repo / "mekkablue"

    def test_environment_variable_overrides_submodule(
        self, monkeypatch: pytest.MonkeyPatch, temp_fallback_paths: dict[str, Path]
    ) -> None:
        """測試環境變數優先於 Submodule fallback"""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_mekkablue = Path(tmpdir) / "env_mekkablue"
            env_mekkablue.mkdir()
            (env_mekkablue / "__init__.py").write_text("# env mekkablue")

            # 設定環境變數
            monkeypatch.setenv("GLYPHS_MEKKABLUE_PATH", str(env_mekkablue))

            # 使用不存在的 Repositories 路徑
            nonexistent_repo = Path("/nonexistent/repositories")
            scanner = RepositoryScanner(nonexistent_repo, temp_fallback_paths)
            scanner.scan_repositories()

            mekkablue_path = scanner.get_module_path("mekkablue")

            # 環境變數應該優先於 Submodule
            assert mekkablue_path == env_mekkablue

    def test_no_fallback_returns_none(self) -> None:
        """測試當所有路徑都不存在時返回 None"""
        nonexistent_repo = Path("/nonexistent/repositories")
        scanner = RepositoryScanner(nonexistent_repo, {})
        scanner.scan_repositories()

        mekkablue_path = scanner.get_module_path("mekkablue")

        # 應該返回 None
        assert mekkablue_path is None

    def test_fallback_with_nonexistent_submodule(self) -> None:
        """測試 Submodule 路徑不存在時返回 None"""
        nonexistent_repo = Path("/nonexistent/repositories")
        fallback_paths = {
            "mekkablue": Path("/nonexistent/submodule/mekkablue"),
        }

        scanner = RepositoryScanner(nonexistent_repo, fallback_paths)
        scanner.scan_repositories()

        mekkablue_path = scanner.get_module_path("mekkablue")

        # Submodule 不存在，應該返回 None
        assert mekkablue_path is None

    def test_mixed_scenario_local_and_fallback(
        self, temp_local_repo: Path, temp_fallback_paths: dict[str, Path]
    ) -> None:
        """測試混合場景：部分本地安裝，部分使用 fallback"""
        # 移除本地的 vanilla 模組
        vanilla_local = temp_local_repo / "vanilla"
        if vanilla_local.exists():
            import shutil

            shutil.rmtree(vanilla_local)

        scanner = RepositoryScanner(temp_local_repo, temp_fallback_paths)
        scanner.scan_repositories()

        # mekkablue 使用本地安裝
        mekkablue_path = scanner.get_module_path("mekkablue")
        assert mekkablue_path == temp_local_repo / "mekkablue"

        # vanilla 使用 Submodule fallback
        vanilla_path = scanner.get_module_path("vanilla")
        assert vanilla_path == temp_fallback_paths["vanilla"]

    def test_multiple_module_resolution(self, temp_local_repo: Path, temp_fallback_paths: dict[str, Path]) -> None:
        """測試多個模組同時解析路徑"""
        scanner = RepositoryScanner(temp_local_repo, temp_fallback_paths)
        scanner.scan_repositories()

        # 同時取得多個模組路徑
        mekkablue_path = scanner.get_module_path("mekkablue")
        vanilla_path = scanner.get_module_path("vanilla")

        # 都應該使用本地安裝
        assert mekkablue_path == temp_local_repo / "mekkablue"
        assert vanilla_path == temp_local_repo / "vanilla"

        # 再次取得應該返回相同結果（快取測試）
        assert scanner.get_module_path("mekkablue") == mekkablue_path
        assert scanner.get_module_path("vanilla") == vanilla_path


class TestRepositoryFallbackRealWorld:
    """測試實際場景的 Fallback 機制"""

    def test_real_project_structure(self) -> None:
        """測試真實專案結構的 Submodule fallback"""
        project_root = Path(__file__).parent.parent
        fallback_paths = {
            "mekkablue": project_root / "data/official/mekkablue-scripts",
            "vanilla": project_root / "data/official/vanilla",
        }

        # 嘗試自動偵測
        scanner = RepositoryScanner.auto_detect()
        if scanner is None:
            # 如果無法自動偵測，使用假路徑測試 fallback
            scanner = RepositoryScanner(
                Path("/nonexistent/repositories"), fallback_paths
            )

        scanner.fallback_paths = fallback_paths
        scanner.scan_repositories()

        # 測試取得路徑（應該能取得其中一種）
        mekkablue_path = scanner.get_module_path("mekkablue")
        vanilla_path = scanner.get_module_path("vanilla")

        # 至少應該有一個路徑存在（本地或 Submodule）
        # 如果 Submodule 已初始化
        if (project_root / "data/official/mekkablue-scripts").exists():
            assert mekkablue_path is not None
        if (project_root / "data/official/vanilla").exists():
            assert vanilla_path is not None

    def test_fallback_paths_initialization(self) -> None:
        """測試 fallback_paths 可以在初始化後設定"""
        scanner = RepositoryScanner(Path("/nonexistent"))

        # 初始化時沒有 fallback_paths
        assert scanner.fallback_paths == {}

        # 後續設定 fallback_paths
        with tempfile.TemporaryDirectory() as tmpdir:
            fallback = Path(tmpdir) / "fallback_module"
            fallback.mkdir()
            (fallback / "__init__.py").write_text("# test")

            scanner.fallback_paths = {"test_module": fallback}
            scanner.scan_repositories()

            # 應該能使用 fallback
            path = scanner.get_module_path("test_module")
            assert path == fallback
