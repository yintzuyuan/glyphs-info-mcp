#!/usr/bin/env python3
"""
測試 Vanilla Local Accessor - TDD 紅燈階段
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
from glyphs_info_mcp.shared.core.vanilla_local_accessor import VanillaLocalAccessor


class TestVanillaLocalAccessor:
    """測試 Vanilla Local Accessor 基本功能"""

    @pytest.fixture
    def mock_vanilla_module(self) -> Generator[Path, None, None]:
        """建立模擬的 vanilla 模組結構"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 建立 Repositories/vanilla 結構
            repo_path = Path(tmpdir) / "Repositories"
            vanilla_path = repo_path / "vanilla" / "Lib" / "vanilla"
            vanilla_path.mkdir(parents=True)

            # 建立 __init__.py
            init_content = """
from vanilla.vanillaButton import Button
from vanilla.vanillaTextBox import TextBox
from vanilla.vanillaWindow import Window

__all__ = ["Button", "TextBox", "Window"]
"""
            (vanilla_path / "__init__.py").write_text(init_content)

            # 建立 Button 類別
            button_content = '''
from AppKit import NSButton

class Button:
    """
    A standard button widget.

    posSize: Tuple of form (left, top, width, height)
    title: The text to be displayed on the button
    callback: The method to be called when button is pressed
    """

    def __init__(self, posSize, title, callback=None, sizeStyle="regular"):
        """Initialize a Button."""
        self.posSize = posSize
        self.title = title
        self.callback = callback
        self.sizeStyle = sizeStyle

    def setTitle(self, title):
        """Set the button title."""
        self.title = title

    def getTitle(self):
        """Get the button title."""
        return self.title
'''
            (vanilla_path / "vanillaButton.py").write_text(button_content)

            # 建立 TextBox 類別
            textbox_content = '''
class TextBox:
    """
    A text display widget.

    posSize: Tuple of form (left, top, width, height)
    text: The text to display
    """

    def __init__(self, posSize, text="", alignment="left"):
        self.posSize = posSize
        self.text = text
        self.alignment = alignment

    def set(self, text):
        """Set the text."""
        self.text = text

    def get(self):
        """Get the text."""
        return self.text
'''
            (vanilla_path / "vanillaTextBox.py").write_text(textbox_content)

            # 建立 Window 類別
            window_content = '''
class Window:
    """
    A standard window.

    posSize: Tuple of form (width, height) or (left, top, width, height)
    title: The window title
    """

    def __init__(self, posSize, title="", minSize=None, maxSize=None):
        self.posSize = posSize
        self.title = title
        self.minSize = minSize
        self.maxSize = maxSize

    def open(self):
        """Open the window."""
        pass

    def close(self):
        """Close the window."""
        pass
'''
            (vanilla_path / "vanillaWindow.py").write_text(window_content)

            yield repo_path

    @pytest.fixture
    def vanilla_accessor(self, mock_vanilla_module: Path) -> VanillaLocalAccessor:
        """建立 VanillaLocalAccessor 實例"""
        scanner = RepositoryScanner(mock_vanilla_module)
        scanner.scan_repositories()
        accessor = VanillaLocalAccessor(scanner)
        return accessor

    def test_accessor_initialization(self, vanilla_accessor: VanillaLocalAccessor) -> None:
        """測試 Accessor 正確初始化"""
        assert vanilla_accessor is not None
        assert vanilla_accessor.is_available()

    def test_accessor_unavailable_when_no_vanilla(self) -> None:
        """測試當 vanilla 不存在時 is_available() 返回 False"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "Repositories"
            repo_path.mkdir()

            scanner = RepositoryScanner(repo_path)
            scanner.scan_repositories()
            accessor = VanillaLocalAccessor(scanner)

            assert not accessor.is_available()

    def test_list_vanilla_classes(self, vanilla_accessor: VanillaLocalAccessor) -> None:
        """測試列出所有 Vanilla UI 元件"""
        classes = vanilla_accessor.list_vanilla_classes()

        assert isinstance(classes, list)
        assert len(classes) > 0
        assert "Button" in classes
        assert "TextBox" in classes
        assert "Window" in classes

    def test_get_vanilla_class_button(self, vanilla_accessor: VanillaLocalAccessor) -> None:
        """測試取得 Button 類別的完整資訊"""
        button_info = vanilla_accessor.get_vanilla_class("Button")

        assert button_info is not None
        assert "class_name" in button_info
        assert button_info["class_name"] == "Button"
        assert "source" in button_info
        assert "methods" in button_info
        assert "docstring" in button_info

        # 檢查文檔字串
        assert "standard button widget" in button_info["docstring"].lower()

        # 檢查方法
        method_names = [m["name"] for m in button_info["methods"]]
        assert "__init__" in method_names
        assert "setTitle" in method_names
        assert "getTitle" in method_names

    def test_get_vanilla_class_not_found(self, vanilla_accessor: VanillaLocalAccessor) -> None:
        """測試取得不存在的類別"""
        result = vanilla_accessor.get_vanilla_class("NonExistentClass")
        assert result is None

    def test_search_vanilla_classes_by_name(self, vanilla_accessor: VanillaLocalAccessor) -> None:
        """測試按名稱搜尋 UI 元件"""
        results = vanilla_accessor.search_vanilla_classes("button")

        assert isinstance(results, list)
        assert len(results) > 0
        assert any("Button" in r["class_name"] for r in results)

    def test_search_vanilla_classes_by_docstring(self, vanilla_accessor: VanillaLocalAccessor) -> None:
        """測試按文檔字串搜尋"""
        results = vanilla_accessor.search_vanilla_classes("display")

        assert isinstance(results, list)
        # TextBox 的文檔包含 "display"
        assert any("TextBox" in r["class_name"] for r in results)

    def test_search_vanilla_classes_no_results(self, vanilla_accessor: VanillaLocalAccessor) -> None:
        """測試搜尋無結果"""
        results = vanilla_accessor.search_vanilla_classes("nonexistent_widget")

        assert isinstance(results, list)
        assert len(results) == 0

    def test_search_vanilla_classes_case_insensitive(self, vanilla_accessor: VanillaLocalAccessor) -> None:
        """測試搜尋不區分大小寫"""
        results_lower = vanilla_accessor.search_vanilla_classes("button")
        results_upper = vanilla_accessor.search_vanilla_classes("BUTTON")
        results_mixed = vanilla_accessor.search_vanilla_classes("BuTtOn")

        assert len(results_lower) == len(results_upper) == len(results_mixed)

    def test_get_vanilla_class_with_parameters(self, vanilla_accessor: VanillaLocalAccessor) -> None:
        """測試取得類別時包含參數資訊"""
        button_info = vanilla_accessor.get_vanilla_class("Button")
        assert button_info is not None

        # 檢查 __init__ 方法的參數
        init_method = next(
            (m for m in button_info["methods"] if m["name"] == "__init__"), None
        )
        assert init_method is not None
        assert "parameters" in init_method

        # 檢查參數名稱
        param_names = [p["name"] for p in init_method["parameters"]]
        assert "posSize" in param_names
        assert "title" in param_names
        assert "callback" in param_names

    def test_cache_mechanism(self, vanilla_accessor: VanillaLocalAccessor) -> None:
        """測試快取機制"""
        # 第一次呼叫
        classes1 = vanilla_accessor.list_vanilla_classes()

        # 第二次應該使用快取
        classes2 = vanilla_accessor.list_vanilla_classes()

        assert classes1 == classes2


class TestVanillaLocalAccessorEdgeCases:
    """測試邊界情況"""

    def test_malformed_init_file(self) -> None:
        """測試處理格式錯誤的 __init__.py"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "Repositories"
            vanilla_path = repo_path / "vanilla" / "Lib" / "vanilla"
            vanilla_path.mkdir(parents=True)

            # 建立格式錯誤的 __init__.py
            (vanilla_path / "__init__.py").write_text("import syntax error!!!")

            scanner = RepositoryScanner(repo_path)
            scanner.scan_repositories()
            accessor = VanillaLocalAccessor(scanner)

            # 應該優雅處理錯誤
            classes = accessor.list_vanilla_classes()
            assert isinstance(classes, list)

    def test_missing_class_file(self) -> None:
        """測試類別檔案不存在的情況"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "Repositories"
            vanilla_path = repo_path / "vanilla" / "Lib" / "vanilla"
            vanilla_path.mkdir(parents=True)

            # __init__.py 引用不存在的類別
            (vanilla_path / "__init__.py").write_text(
                """
from vanilla.vanillaMissing import MissingClass
__all__ = ["MissingClass"]
"""
            )

            scanner = RepositoryScanner(repo_path)
            scanner.scan_repositories()
            accessor = VanillaLocalAccessor(scanner)

            # 應該優雅處理錯誤
            result = accessor.get_vanilla_class("MissingClass")
            assert result is None
