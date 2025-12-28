"""
測試 MetadataExtractor - 元資料提取器

TDD 紅燈階段：先撰寫測試，預期失敗
"""

import plistlib
from pathlib import Path

from glyphs_info_mcp.modules.glyphs_plugins.accessors.metadata_extractor import MetadataExtractor


class TestMetadataExtractor:
    """測試 MetadataExtractor 類別"""

    def test_extract_info_plist_success(self, tmp_path: Path) -> None:
        """測試成功提取 Info.plist"""
        # Arrange
        plist_data = {
            "CFBundleName": "ShowCrosshair",
            "CFBundleIdentifier": "com.mekkablue.ShowCrosshair",
            "CFBundleShortVersionString": "3.1.1",
            "NSHumanReadableCopyright": "© 2025 mekkablue",
        }
        plist_path = tmp_path / "Info.plist"
        with open(plist_path, "wb") as f:
            plistlib.dump(plist_data, f)

        # Act
        result = MetadataExtractor.extract_info_plist(plist_path)

        # Assert
        assert result == plist_data
        assert result["CFBundleName"] == "ShowCrosshair"
        assert result["CFBundleIdentifier"] == "com.mekkablue.ShowCrosshair"

    def test_extract_info_plist_not_found(self, tmp_path: Path) -> None:
        """測試 Info.plist 不存在時返回空字典"""
        # Arrange
        plist_path = tmp_path / "NonExistent.plist"

        # Act
        result = MetadataExtractor.extract_info_plist(plist_path)

        # Assert
        assert result == {}

    def test_extract_info_plist_invalid_format(self, tmp_path: Path) -> None:
        """測試 Info.plist 格式錯誤時返回空字典"""
        # Arrange
        plist_path = tmp_path / "Invalid.plist"
        plist_path.write_text("This is not a valid plist")

        # Act
        result = MetadataExtractor.extract_info_plist(plist_path)

        # Assert
        assert result == {}

    def test_extract_git_config_success(self, tmp_path: Path) -> None:
        """測試成功提取 .git/config"""
        # Arrange
        git_config_path = tmp_path / ".git" / "config"
        git_config_path.parent.mkdir(parents=True, exist_ok=True)
        git_config_content = """[core]
    repositoryformatversion = 0
[remote "origin"]
    url = https://github.com/mekkablue/ShowCrosshair
    fetch = +refs/heads/*:refs/remotes/origin/*
[branch "master"]
    remote = origin
    merge = refs/heads/master
"""
        git_config_path.write_text(git_config_content)

        # Act
        result = MetadataExtractor.extract_git_config(git_config_path)

        # Assert
        assert result["url"] == "https://github.com/mekkablue/ShowCrosshair"
        assert result["branch"] == "master"

    def test_extract_git_config_main_branch(self, tmp_path: Path) -> None:
        """測試提取 main 分支的 git config"""
        # Arrange
        git_config_path = tmp_path / ".git" / "config"
        git_config_path.parent.mkdir(parents=True, exist_ok=True)
        git_config_content = """[remote "origin"]
    url = https://github.com/user/repo
[branch "main"]
    remote = origin
"""
        git_config_path.write_text(git_config_content)

        # Act
        result = MetadataExtractor.extract_git_config(git_config_path)

        # Assert
        assert result["url"] == "https://github.com/user/repo"
        assert result["branch"] == "main"

    def test_extract_git_config_not_found(self, tmp_path: Path) -> None:
        """測試 .git/config 不存在時返回空字典"""
        # Arrange
        git_config_path = tmp_path / ".git" / "config"

        # Act
        result = MetadataExtractor.extract_git_config(git_config_path)

        # Assert
        assert result == {}

    def test_extract_readme_success(self, tmp_path: Path) -> None:
        """測試成功提取 README.md"""
        # Arrange
        readme_path = tmp_path / "README.md"
        readme_content = """# ShowCrosshair

This plugin shows a crosshair at the cursor position.

## Installation

Install via Plugin Manager.
"""
        readme_path.write_text(readme_content, encoding="utf-8")

        # Act
        result = MetadataExtractor.extract_readme(readme_path)

        # Assert
        assert "ShowCrosshair" in result
        assert "crosshair at the cursor position" in result
        assert "Plugin Manager" in result

    def test_extract_readme_truncation(self, tmp_path: Path) -> None:
        """測試 README.md 超過長度限制時截斷"""
        # Arrange
        readme_path = tmp_path / "README.md"
        long_content = "A" * 3000  # 超過預設 2000 字元限制
        readme_path.write_text(long_content, encoding="utf-8")

        # Act
        result = MetadataExtractor.extract_readme(readme_path, max_length=2000)

        # Assert
        assert len(result) <= 2020  # 2000 + "\n\n...(truncated)" 長度
        assert result.endswith("...(truncated)")

    def test_extract_readme_not_found(self, tmp_path: Path) -> None:
        """測試 README.md 不存在時返回空字串"""
        # Arrange
        readme_path = tmp_path / "README.md"

        # Act
        result = MetadataExtractor.extract_readme(readme_path)

        # Assert
        assert result == ""

    def test_extract_readme_custom_max_length(self, tmp_path: Path) -> None:
        """測試自訂最大長度"""
        # Arrange
        readme_path = tmp_path / "README.md"
        content = "B" * 1000
        readme_path.write_text(content, encoding="utf-8")

        # Act
        result = MetadataExtractor.extract_readme(readme_path, max_length=500)

        # Assert
        assert len(result) <= 520
        assert result.endswith("...(truncated)")
