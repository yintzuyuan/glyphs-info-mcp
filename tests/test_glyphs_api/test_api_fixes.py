"""
測試 API 工具修復

驗證以下三個問題的修復：
1. GSAnchor 查詢異常：_find_class_block 支援 class ____ 模式
2. GSLayer.width 描述錯誤：類別範圍感知屬性搜尋
3. api_navigate_structure 後台錯誤：contains 分支缺少 path_lines.extend
"""

import pytest
from pathlib import Path
from typing import Generator
from unittest.mock import Mock, patch, MagicMock

from glyphs_info_mcp.shared.core.python_api_native_accessor import (
    PythonAPINativeAccessor,
)
from glyphs_info_mcp.modules.glyphs_api.unified_api_module import (
    UnifiedAPIModule,
)


class TestGSAnchorClassPattern:
    """測試 GSAnchor 類別定義模式支援"""

    @pytest.fixture
    def accessor(self) -> Generator[PythonAPINativeAccessor, None, None]:
        """建立 PythonAPINativeAccessor 實例"""
        # 使用 patch 避免實際載入檔案
        with patch.object(
            PythonAPINativeAccessor, "__init__", lambda self, init_file: None
        ):
            accessor = PythonAPINativeAccessor.__new__(PythonAPINativeAccessor)
            accessor.init_file = Path("/fake/path/__init__.py")
            accessor.symbols = {"classes": ["GSAnchor"], "functions": [], "constants": []}
            yield accessor

    def test_find_class_block_supports_def_pattern(
        self, accessor: PythonAPINativeAccessor
    ) -> None:
        """測試 _find_class_block 支援 def ____ 模式"""
        # 模擬 grep 結果：找到 def ____GSFont____
        with patch.object(accessor, "_grep_line") as mock_grep:
            mock_grep.side_effect = lambda pattern: (
                [100] if "def ____GSFont____" in pattern else []
            )

            result = accessor._find_class_block("GSFont")

            assert result == 100
            mock_grep.assert_called_with("def ____GSFont____")

    def test_find_class_block_supports_class_pattern(
        self, accessor: PythonAPINativeAccessor
    ) -> None:
        """測試 _find_class_block 支援 class ____ 模式（GSAnchor）"""
        # 模擬 grep 結果：def 找不到，但 class 找得到
        with patch.object(accessor, "_grep_line") as mock_grep:
            mock_grep.side_effect = lambda pattern: (
                [200] if "class ____GSAnchor____" in pattern else []
            )

            result = accessor._find_class_block("GSAnchor")

            assert result == 200
            # 應該先嘗試 def，再嘗試 class
            assert mock_grep.call_count == 2

    def test_find_class_block_prefers_def_over_class(
        self, accessor: PythonAPINativeAccessor
    ) -> None:
        """測試 _find_class_block 優先使用 def 模式"""
        # 如果 def 和 class 都找得到，應該返回 def 的結果
        with patch.object(accessor, "_grep_line") as mock_grep:
            mock_grep.side_effect = lambda pattern: (
                [100] if "def ____" in pattern else [200]
            )

            result = accessor._find_class_block("TestClass")

            assert result == 100  # 應該返回 def 的結果
            mock_grep.assert_called_once_with("def ____TestClass____")


class TestWidthDescriptionFix:
    """測試 width 屬性描述修復（類別範圍感知）"""

    @pytest.fixture
    def accessor(self) -> Generator[PythonAPINativeAccessor, None, None]:
        """建立 PythonAPINativeAccessor 實例"""
        with patch.object(
            PythonAPINativeAccessor, "__init__", lambda self, init_file: None
        ):
            accessor = PythonAPINativeAccessor.__new__(PythonAPINativeAccessor)
            accessor.init_file = Path("/fake/path/__init__.py")
            accessor.symbols = {
                "classes": ["GSLayer", "GSFontMaster"],
                "functions": [],
                "constants": [],
            }
            yield accessor

    def test_get_property_uses_class_range(
        self, accessor: PythonAPINativeAccessor
    ) -> None:
        """測試 get_property 使用類別範圍篩選屬性文檔"""
        # 模擬情境：
        # - GSLayer 區塊在 9000-9500 行
        # - widthClass 文檔在 6239 行（不在 GSLayer 範圍內）
        # - width 文檔在 9060 行（在 GSLayer 範圍內）

        with patch.object(
            accessor, "_find_class_block_range", return_value=(9000, 9500)
        ):
            with patch.object(accessor, "_find_property_assignment", return_value=None):
                with patch.object(
                    accessor, "_find_property_doc", return_value=[6239, 9060]
                ):
                    with patch.object(
                        accessor,
                        "_read_until_marker",
                        return_value=".. attribute:: width\n正確的描述\n'''",
                    ):
                        # 清除 LRU 快取
                        accessor.get_property.cache_clear()

                        result = accessor.get_property("GSLayer", "width")

                        # 應該選擇 9060（在類別範圍內），而不是 6239
                        accessor._read_until_marker.assert_called_with(  # type: ignore[attr-defined]
                            9060, marker="'''", max_lines=100
                        )

    def test_get_property_fallback_when_no_class_range(
        self, accessor: PythonAPINativeAccessor
    ) -> None:
        """測試當無法確定類別範圍時，回退到第一個匹配"""
        with patch.object(accessor, "_find_class_block_range", return_value=None):
            with patch.object(accessor, "_find_property_assignment", return_value=None):
                with patch.object(
                    accessor, "_find_property_doc", return_value=[6239, 9060]
                ):
                    with patch.object(
                        accessor,
                        "_read_until_marker",
                        return_value=".. attribute:: width\n描述\n'''",
                    ):
                        accessor.get_property.cache_clear()

                        result = accessor.get_property("GSLayer", "width")

                        # 無法確定範圍時，應該使用第一個匹配
                        accessor._read_until_marker.assert_called_with(  # type: ignore[attr-defined]
                            6239, marker="'''", max_lines=100
                        )


class TestNavigateStructureContainsFix:
    """測試 _navigate_recursive contains 分支修復"""

    @pytest.fixture
    def module(self) -> Generator[UnifiedAPIModule, None, None]:
        """建立 UnifiedAPIModule 模擬實例"""
        with patch.object(UnifiedAPIModule, "__init__", lambda self: None):
            module = UnifiedAPIModule.__new__(UnifiedAPIModule)
            yield module

    def test_contains_branch_extends_path_lines(self, module: UnifiedAPIModule) -> None:
        """測試 contains 分支正確擴展 path_lines"""
        # 設置測試結構
        structure = {
            "classes": {
                "GSLayer": {
                    "contains": ["GSPath", "GSComponent"],
                },
                "GSPath": {
                    "contains": [],
                },
                "GSComponent": {
                    "contains": [],
                },
            }
        }

        # 測試遞迴導航
        result = module._navigate_recursive(
            class_name="GSLayer",
            relationship="contains",
            max_depth=2,
            current_depth=0,
            structure=structure,
            path=[],
        )

        # 驗證 tree 和 paths 都有內容
        assert "tree" in result
        assert "paths" in result
        assert len(result["tree"]) >= 2  # GSPath 和 GSComponent
        # paths 應該不會拋出錯誤（之前的 bug 會導致 KeyError）

    def test_contains_branch_no_error_on_recursive(
        self, module: UnifiedAPIModule
    ) -> None:
        """測試 contains 分支遞迴時不會拋出錯誤"""
        structure = {
            "classes": {
                "GSFont": {
                    "contains": ["GSGlyph"],
                },
                "GSGlyph": {
                    "contains": ["GSLayer"],
                },
                "GSLayer": {
                    "contains": [],
                },
            }
        }

        # 這不應該拋出任何錯誤
        try:
            result = module._navigate_recursive(
                class_name="GSFont",
                relationship="contains",
                max_depth=3,
                current_depth=0,
                structure=structure,
                path=[],
            )
            assert "tree" in result
            assert "paths" in result
        except Exception as e:
            pytest.fail(f"_navigate_recursive 拋出異常: {e}")


class TestFindClassBlockRange:
    """測試 _find_class_block_range 輔助方法"""

    @pytest.fixture
    def accessor(self) -> Generator[PythonAPINativeAccessor, None, None]:
        """建立 PythonAPINativeAccessor 實例"""
        with patch.object(
            PythonAPINativeAccessor, "__init__", lambda self, init_file: None
        ):
            accessor = PythonAPINativeAccessor.__new__(PythonAPINativeAccessor)
            accessor.init_file = Path("/fake/path/__init__.py")
            accessor.symbols = {"classes": [], "functions": [], "constants": []}
            yield accessor

    def test_returns_none_when_class_not_found(
        self, accessor: PythonAPINativeAccessor
    ) -> None:
        """測試當類別不存在時返回 None"""
        with patch.object(accessor, "_find_class_block", return_value=None):
            result = accessor._find_class_block_range("NonExistent")
            assert result is None

    def test_returns_range_tuple(self, accessor: PythonAPINativeAccessor) -> None:
        """測試正常情況返回 (start, end) 元組"""
        # 模擬檔案內容
        fake_content = ["line\n"] * 100 + ["def ____NextClass____\n"] + ["line\n"] * 50

        with patch.object(accessor, "_find_class_block", return_value=50):
            with patch("builtins.open", create=True) as mock_open:
                mock_file = MagicMock()
                mock_file.readline.side_effect = fake_content[50:]
                mock_open.return_value.__enter__.return_value = mock_file

                result = accessor._find_class_block_range("TestClass")

                assert result is not None
                assert isinstance(result, tuple)
                assert len(result) == 2
                assert result[0] == 50  # 起始行
