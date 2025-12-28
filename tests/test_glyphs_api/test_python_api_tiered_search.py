"""
測試 Python API 分層搜尋策略

Issue #70: 實作分層搜尋，讓 userData 等類別屬性也能被搜尋到。

分層搜尋策略：
- 第一層：搜尋符號索引（類別、函數、常數）- 快速
- 第二層：若無結果，搜尋類別成員（屬性、方法）- 較慢但完整
"""

import pytest
from typing import Generator
from unittest.mock import Mock, patch

from glyphs_info_mcp.modules.glyphs_api.api.python_api_native import PythonAPIManager


class TestTieredSearchStrategy:
    """測試分層搜尋策略"""

    @pytest.fixture
    def mock_accessor(self) -> Mock:
        """建立模擬的 accessor"""
        accessor = Mock()
        accessor.symbols = {
            'classes': ['GSFont', 'GSGlyph', 'GSLayer'],
            'functions': ['divideCurve', 'scaleOfPath'],
            'constants': ['GSOFFCURVE', 'GSCURVE']
        }
        return accessor

    @pytest.fixture
    def manager(self, mock_accessor: Mock) -> Generator[PythonAPIManager, None, None]:
        """建立 PythonAPIManager 實例"""
        # 使用 patch 避免實際載入檔案
        with patch.object(PythonAPIManager, '__init__', lambda self, init_file: None):
            manager = PythonAPIManager.__new__(PythonAPIManager)
            manager.accessor = mock_accessor
            yield manager

    def test_first_layer_search_finds_class(self, manager: PythonAPIManager) -> None:
        """測試第一層搜尋可以找到類別"""
        # 模擬第一層搜尋結果
        manager.accessor.search.return_value = [  # type: ignore[attr-defined]
            {'type': 'class', 'name': 'GSFont', 'score': 1.0}
        ]

        result = manager.search('GSFont')

        # 應該呼叫 accessor.search
        manager.accessor.search.assert_called_once_with('GSFont', symbol_type='all')  # type: ignore[attr-defined]

        # 結果應該包含 GSFont
        assert 'GSFont' in result
        assert 'class' in result.lower()

    def test_first_layer_search_finds_function(self, manager: PythonAPIManager) -> None:
        """測試第一層搜尋可以找到函數"""
        manager.accessor.search.return_value = [  # type: ignore[attr-defined]
            {'type': 'function', 'name': 'divideCurve', 'score': 1.0}
        ]

        result = manager.search('divideCurve')

        assert 'divideCurve' in result
        assert 'function' in result.lower()

    def test_second_layer_triggered_when_first_layer_empty(
        self, manager: PythonAPIManager
    ) -> None:
        """測試第一層無結果時觸發第二層搜尋"""
        # 第一層無結果
        manager.accessor.search.return_value = []  # type: ignore[attr-defined]

        # 模擬 get_class 返回類別成員
        manager.accessor.get_class.return_value = {  # type: ignore[attr-defined]
            'properties': ['userData', 'masters', 'glyphs'],
            'methods': ['save', 'close']
        }

        result = manager.search('userData')

        # 應該找到 userData 屬性
        assert 'userData' in result
        assert 'property' in result.lower()
        assert 'member' in result.lower()  # 新格式使用 Member Layer 標示

    def test_both_layers_searched_when_scope_is_all(
        self, manager: PythonAPIManager
    ) -> None:
        """測試 scope='all' 時同時搜尋兩層（新行為）"""
        manager.accessor.search.return_value = [  # type: ignore[attr-defined]
            {'type': 'class', 'name': 'GSFont', 'score': 1.0}
        ]
        manager.accessor.get_class.return_value = {  # type: ignore[attr-defined]
            'properties': ['fonts'],
            'methods': []
        }

        result = manager.search('font')

        # 應該呼叫 get_class（第二層搜尋）
        manager.accessor.get_class.assert_called()  # type: ignore[attr-defined]
        # 結果應該包含兩層
        assert 'GSFont' in result
        assert 'symbol' in result.lower()

    def test_max_results_limits_output(self, manager: PythonAPIManager) -> None:
        """測試 max_results 限制結果數量"""
        # 第一層無結果
        manager.accessor.search.return_value = []  # type: ignore[attr-defined]

        # 模擬多個匹配的成員
        manager.accessor.get_class.return_value = {  # type: ignore[attr-defined]
            'properties': ['userData', 'userDataForKey', 'userDataKeys'],
            'methods': ['setUserData', 'removeUserData']
        }

        result = manager.search('userData', max_results=3)

        # 計算結果中的項目數量（通過計算編號）
        import re
        items = re.findall(r'^\d+\.', result, re.MULTILINE)
        assert len(items) <= 3

    def test_no_results_shows_suggestion(self, manager: PythonAPIManager) -> None:
        """測試無結果時顯示建議"""
        manager.accessor.search.return_value = []  # type: ignore[attr-defined]
        manager.accessor.get_class.return_value = {  # type: ignore[attr-defined]
            'properties': [],
            'methods': []
        }

        result = manager.search('nonexistent')

        assert 'no' in result.lower() and 'found' in result.lower()
        assert 'suggestion' in result.lower()


class TestSearchClassMembers:
    """測試 _search_class_members 方法"""

    @pytest.fixture
    def manager(self) -> Generator[PythonAPIManager, None, None]:
        """建立 PythonAPIManager 實例"""
        with patch.object(PythonAPIManager, '__init__', lambda self, init_file: None):
            manager = PythonAPIManager.__new__(PythonAPIManager)
            manager.accessor = Mock()
            manager.accessor.symbols = {
                'classes': ['GSFont', 'GSGlyph', 'GSLayer']
            }
            yield manager

    def test_finds_property_by_name(self, manager: PythonAPIManager) -> None:
        """測試可以找到屬性名稱"""
        manager.accessor.get_class.return_value = {  # type: ignore[attr-defined]
            'properties': ['userData', 'masters', 'glyphs'],
            'methods': []
        }

        results = manager._search_class_members('userData', max_results=10)

        # 應該找到 userData
        assert len(results) >= 1
        assert results[0]['name'] == 'userData'
        assert results[0]['type'] == 'property'
        assert results[0]['class'] == 'GSFont'

    def test_finds_method_by_name(self, manager: PythonAPIManager) -> None:
        """測試可以找到方法名稱"""
        manager.accessor.get_class.return_value = {  # type: ignore[attr-defined]
            'properties': [],
            'methods': ['save', 'close', 'addGlyph']
        }

        results = manager._search_class_members('save', max_results=10)

        assert len(results) >= 1
        assert results[0]['name'] == 'save'
        assert results[0]['type'] == 'method'

    def test_partial_match(self, manager: PythonAPIManager) -> None:
        """測試部分匹配"""
        manager.accessor.get_class.return_value = {  # type: ignore[attr-defined]
            'properties': ['userData', 'tempData', 'fontData'],
            'methods': []
        }

        results = manager._search_class_members('data', max_results=10)

        # 應該找到所有包含 'data' 的屬性
        names = [r['name'] for r in results]
        assert 'userData' in names
        assert 'tempData' in names
        assert 'fontData' in names

    def test_case_insensitive(self, manager: PythonAPIManager) -> None:
        """測試不區分大小寫"""
        manager.accessor.get_class.return_value = {  # type: ignore[attr-defined]
            'properties': ['userData'],
            'methods': []
        }

        results = manager._search_class_members('USERDATA', max_results=10)

        assert len(results) >= 1
        assert results[0]['name'] == 'userData'

    def test_exact_match_has_higher_score(self, manager: PythonAPIManager) -> None:
        """測試精確匹配有更高評分"""
        manager.accessor.get_class.return_value = {  # type: ignore[attr-defined]
            'properties': ['userData', 'userDataForKey'],
            'methods': []
        }

        results = manager._search_class_members('userData', max_results=10)

        # 結果應該按評分排序
        exact_match = next(r for r in results if r['name'] == 'userData')
        partial_match = next(r for r in results if r['name'] == 'userDataForKey')

        assert exact_match['score'] > partial_match['score']

    def test_early_termination_on_max_results(self, manager: PythonAPIManager) -> None:
        """測試達到 max_results 時提早終止"""
        # 每個類別都有很多屬性
        manager.accessor.get_class.return_value = {  # type: ignore[attr-defined]
            'properties': ['data1', 'data2', 'data3', 'data4', 'data5'],
            'methods': ['getData1', 'getData2', 'getData3']
        }

        results = manager._search_class_members('data', max_results=3)

        # 結果應該不超過 max_results
        assert len(results) <= 3

    def test_handles_get_class_exception(self, manager: PythonAPIManager) -> None:
        """測試處理 get_class 異常"""
        manager.accessor.get_class.side_effect = Exception("Test error")  # type: ignore[attr-defined]

        # 不應該拋出異常
        results = manager._search_class_members('userData', max_results=10)

        # 應該返回空列表
        assert results == []
