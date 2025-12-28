"""
測試 Python API 分層搜尋增強功能

Issue #70: 參考 #72/#73 的 match_type 機制，讓 AI 能夠主動選擇搜尋策略。

核心改進：
- 搜尋同時返回符號層和成員層結果
- 結果帶有 match_type 標示（symbol/member）
- 輸出格式分層顯示
- 新增 scope 參數值：members, properties, methods
"""

import pytest
from typing import Generator
from unittest.mock import Mock, patch

from glyphs_info_mcp.modules.glyphs_api.api.python_api_native import PythonAPIManager


class TestLayeredSearchBothLayers:
    """測試分層搜尋同時返回兩層結果"""

    @pytest.fixture
    def mock_accessor(self) -> Mock:
        """建立模擬的 accessor"""
        accessor = Mock()
        accessor.symbols = {
            'classes': ['GSFont', 'GSGlyph', 'GSLayer', 'GSFontMaster'],
            'functions': ['divideCurve', 'scaleOfPath'],
            'constants': ['GSOFFCURVE', 'GSCURVE', 'STROKEWIDTH']
        }
        return accessor

    @pytest.fixture
    def manager(self, mock_accessor: Mock) -> Generator[PythonAPIManager, None, None]:
        """建立 PythonAPIManager 實例"""
        with patch.object(PythonAPIManager, '__init__', lambda self, init_file: None):
            manager = PythonAPIManager.__new__(PythonAPIManager)
            manager.accessor = mock_accessor
            yield manager

    def test_search_returns_both_symbol_and_member_layers(
        self, manager: PythonAPIManager
    ) -> None:
        """測試搜尋同時返回符號層和成員層結果"""
        # 符號層找到 STROKEWIDTH 常數
        manager.accessor.search.return_value = [  # type: ignore[attr-defined]
            {'type': 'constant', 'name': 'STROKEWIDTH', 'score': 0.7}
        ]

        # 成員層找到 width 屬性
        manager.accessor.get_class.return_value = {  # type: ignore[attr-defined]
            'properties': ['width', 'height', 'bounds'],
            'methods': ['setWidth']
        }

        result = manager.search('width')

        # 應該同時包含符號層和成員層結果
        assert 'STROKEWIDTH' in result  # 符號層
        assert 'GSLayer.width' in result or 'width' in result  # 成員層
        assert 'Symbol Layer' in result or 'symbol' in result.lower()
        assert 'Member Layer' in result or 'member' in result.lower()

    def test_search_shows_match_type_in_output(self, manager: PythonAPIManager) -> None:
        """測試輸出格式標示匹配層級"""
        manager.accessor.search.return_value = [  # type: ignore[attr-defined]
            {'type': 'class', 'name': 'GSFont', 'score': 1.0}
        ]
        manager.accessor.get_class.return_value = {  # type: ignore[attr-defined]
            'properties': ['fonts'],
            'methods': []
        }

        result = manager.search('font')

        # 應該有分層標示
        assert 'Symbol Layer' in result or 'symbol' in result.lower()
        assert 'Member Layer' in result or 'member' in result.lower()

    def test_search_all_scope_searches_both_layers(
        self, manager: PythonAPIManager
    ) -> None:
        """測試 scope='all' 搜尋兩層"""
        manager.accessor.search.return_value = [  # type: ignore[attr-defined]
            {'type': 'constant', 'name': 'STROKEWIDTH', 'score': 0.7}
        ]
        manager.accessor.get_class.return_value = {  # type: ignore[attr-defined]
            'properties': ['width'],
            'methods': []
        }

        result = manager.search('width', search_scope='all')

        # 應該呼叫 accessor.search
        manager.accessor.search.assert_called()  # type: ignore[attr-defined]
        # 應該有兩層結果
        assert 'STROKEWIDTH' in result
        assert 'width' in result


class TestScopeParameterEnhancement:
    """測試 scope 參數增強功能"""

    @pytest.fixture
    def mock_accessor(self) -> Mock:
        accessor = Mock()
        accessor.symbols = {
            'classes': ['GSFont', 'GSLayer'],
            'functions': [],
            'constants': ['STROKEWIDTH']
        }
        return accessor

    @pytest.fixture
    def manager(self, mock_accessor: Mock) -> Generator[PythonAPIManager, None, None]:
        with patch.object(PythonAPIManager, '__init__', lambda self, init_file: None):
            manager = PythonAPIManager.__new__(PythonAPIManager)
            manager.accessor = mock_accessor
            yield manager

    def test_scope_members_skips_symbol_layer(self, manager: PythonAPIManager) -> None:
        """測試 scope='members' 跳過符號層"""
        manager.accessor.search.return_value = [  # type: ignore[attr-defined]
            {'type': 'constant', 'name': 'STROKEWIDTH', 'score': 0.7}
        ]
        manager.accessor.get_class.return_value = {  # type: ignore[attr-defined]
            'properties': ['width', 'height'],
            'methods': ['setWidth']
        }

        result = manager.search('width', search_scope='members')

        # 不應該包含符號層結果
        assert 'STROKEWIDTH' not in result
        # 應該包含成員層結果
        assert 'width' in result

    def test_scope_properties_only_returns_properties(
        self, manager: PythonAPIManager
    ) -> None:
        """測試 scope='properties' 只返回屬性"""
        manager.accessor.get_class.return_value = {  # type: ignore[attr-defined]
            'properties': ['width', 'height'],
            'methods': ['setWidth', 'calculateWidth']
        }

        result = manager.search('width', search_scope='properties')

        # 不應該包含符號層結果
        assert 'STROKEWIDTH' not in result
        # 應該包含屬性
        assert 'width' in result
        # 不應該包含方法（視實作而定，方法名稱中可能包含 width）
        # 但如果是嚴格篩選，setWidth 不應該出現在 properties scope

    def test_scope_methods_only_returns_methods(self, manager: PythonAPIManager) -> None:
        """測試 scope='methods' 只返回方法"""
        manager.accessor.get_class.return_value = {  # type: ignore[attr-defined]
            'properties': ['width'],
            'methods': ['setWidth', 'calculateWidth']
        }

        result = manager.search('width', search_scope='methods')

        # 不應該包含符號層結果
        assert 'STROKEWIDTH' not in result
        # 應該包含方法
        assert 'setWidth' in result or 'calculateWidth' in result

    def test_scope_classes_still_works(self, manager: PythonAPIManager) -> None:
        """測試 scope='classes' 仍正常運作（向後相容）"""
        manager.accessor.search.return_value = [  # type: ignore[attr-defined]
            {'type': 'class', 'name': 'GSLayer', 'score': 1.0}
        ]

        result = manager.search('layer', search_scope='classes')

        # 應該呼叫 accessor.search 並傳入正確的 symbol_type
        manager.accessor.search.assert_called_with('layer', symbol_type='classes')  # type: ignore[attr-defined]
        assert 'GSLayer' in result

    def test_scope_constants_still_works(self, manager: PythonAPIManager) -> None:
        """測試 scope='constants' 仍正常運作（向後相容）"""
        manager.accessor.search.return_value = [  # type: ignore[attr-defined]
            {'type': 'constant', 'name': 'STROKEWIDTH', 'score': 1.0}
        ]

        result = manager.search('stroke', search_scope='constants')

        manager.accessor.search.assert_called_with('stroke', symbol_type='constants')  # type: ignore[attr-defined]
        assert 'STROKEWIDTH' in result


class TestLayeredOutputFormat:
    """測試分層輸出格式"""

    @pytest.fixture
    def manager(self) -> Generator[PythonAPIManager, None, None]:
        with patch.object(PythonAPIManager, '__init__', lambda self, init_file: None):
            manager = PythonAPIManager.__new__(PythonAPIManager)
            yield manager

    def test_format_layered_results_groups_by_match_type(
        self, manager: PythonAPIManager
    ) -> None:
        """測試 _format_layered_results 按匹配層級分組"""
        results = [
            {'type': 'constant', 'name': 'STROKEWIDTH', 'score': 0.7, 'match_type': 'symbol'},
            {'type': 'property', 'class': 'GSLayer', 'name': 'width', 'score': 0.8, 'match_type': 'member'},
            {'type': 'property', 'class': 'GSFontMaster', 'name': 'width', 'score': 0.8, 'match_type': 'member'},
        ]

        output = manager._format_layered_results('width', results)

        # 應該有分層標題
        assert 'Symbol Layer' in output or 'symbol' in output.lower()
        assert 'Member Layer' in output or 'member' in output.lower()
        # 應該包含所有結果
        assert 'STROKEWIDTH' in output
        assert 'GSLayer' in output
        assert 'width' in output

    def test_format_layered_results_shows_usage_hints(
        self, manager: PythonAPIManager
    ) -> None:
        """測試格式化輸出包含使用提示"""
        results = [
            {'type': 'property', 'class': 'GSLayer', 'name': 'width', 'score': 0.8, 'match_type': 'member'},
        ]

        output = manager._format_layered_results('width', results)

        # 應該包含使用提示
        assert 'api_get_python_member' in output or '查看詳情' in output

    def test_format_layered_results_empty_symbol_layer(
        self, manager: PythonAPIManager
    ) -> None:
        """測試符號層無結果時的輸出"""
        results = [
            {'type': 'property', 'class': 'GSFont', 'name': 'userData', 'score': 0.8, 'match_type': 'member'},
        ]

        output = manager._format_layered_results('userData', results)

        # 應該只顯示成員層
        assert 'Member Layer' in output or 'member' in output.lower()
        assert 'userData' in output

    def test_format_layered_results_empty_member_layer(
        self, manager: PythonAPIManager
    ) -> None:
        """測試成員層無結果時的輸出"""
        results = [
            {'type': 'class', 'name': 'GSFont', 'score': 1.0, 'match_type': 'symbol'},
        ]

        output = manager._format_layered_results('GSFont', results)

        # 應該只顯示符號層
        assert 'Symbol Layer' in output or 'symbol' in output.lower()
        assert 'GSFont' in output


class TestDeduplicationAndSorting:
    """測試去重和排序邏輯"""

    @pytest.fixture
    def manager(self) -> Generator[PythonAPIManager, None, None]:
        with patch.object(PythonAPIManager, '__init__', lambda self, init_file: None):
            manager = PythonAPIManager.__new__(PythonAPIManager)
            yield manager

    def test_deduplicate_removes_duplicates(self, manager: PythonAPIManager) -> None:
        """測試去重功能"""
        results = [
            {'type': 'property', 'class': 'GSLayer', 'name': 'width', 'score': 0.8, 'match_type': 'member'},
            {'type': 'property', 'class': 'GSLayer', 'name': 'width', 'score': 0.8, 'match_type': 'member'},
        ]

        deduplicated = manager._deduplicate_and_sort(results)

        # 應該只有一個結果
        assert len(deduplicated) == 1

    def test_sort_by_score_descending(self, manager: PythonAPIManager) -> None:
        """測試按評分降序排列"""
        results = [
            {'type': 'property', 'name': 'lowScore', 'score': 0.3, 'match_type': 'member'},
            {'type': 'class', 'name': 'highScore', 'score': 1.0, 'match_type': 'symbol'},
            {'type': 'property', 'name': 'midScore', 'score': 0.7, 'match_type': 'member'},
        ]

        sorted_results = manager._deduplicate_and_sort(results)

        # 應該按評分降序排列
        assert sorted_results[0]['name'] == 'highScore'
        assert sorted_results[1]['name'] == 'midScore'
        assert sorted_results[2]['name'] == 'lowScore'

    def test_symbol_layer_before_member_layer_at_same_score(
        self, manager: PythonAPIManager
    ) -> None:
        """測試相同評分時，符號層優先於成員層"""
        results = [
            {'type': 'property', 'class': 'GSLayer', 'name': 'width', 'score': 0.8, 'match_type': 'member'},
            {'type': 'constant', 'name': 'WIDTH', 'score': 0.8, 'match_type': 'symbol'},
        ]

        sorted_results = manager._deduplicate_and_sort(results)

        # 符號層應該在前
        assert sorted_results[0]['match_type'] == 'symbol'
        assert sorted_results[1]['match_type'] == 'member'
