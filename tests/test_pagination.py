#!/usr/bin/env python3
"""
測試標準分頁系統
"""

import sys
from pathlib import Path

import pytest

# 添加共享核心庫路徑
shared_core_path = str(Path(__file__).parent.parent / "src" / "shared")
if shared_core_path not in sys.path:
    sys.path.insert(0, shared_core_path)

from glyphs_info_mcp.shared.core.response_utils import (
    DEFAULT_LIMIT,
    MAX_LIMIT,
    PaginationInfo,
    paginate_results,
    validate_pagination_params,
)


class TestPaginationInfo:
    """測試 PaginationInfo 類別"""

    def test_pagination_info_basic(self) -> None:
        """測試基本分頁資訊"""
        pagination = PaginationInfo(
            total_count=100, offset=0, limit=20, current_count=20
        )
        assert pagination.total_count == 100
        assert pagination.offset == 0
        assert pagination.limit == 20
        assert pagination.current_count == 20

    def test_has_more_true(self) -> None:
        """測試 has_more 為 True"""
        pagination = PaginationInfo(
            total_count=100, offset=0, limit=20, current_count=20
        )
        assert pagination.has_more is True

    def test_has_more_false(self) -> None:
        """測試 has_more 為 False"""
        pagination = PaginationInfo(
            total_count=100, offset=80, limit=20, current_count=20
        )
        assert pagination.has_more is False

    def test_has_more_last_page_partial(self) -> None:
        """測試最後一頁只有部分結果"""
        pagination = PaginationInfo(
            total_count=95, offset=80, limit=20, current_count=15
        )
        assert pagination.has_more is False

    def test_next_offset_with_more_results(self) -> None:
        """測試有更多結果時的 next_offset"""
        pagination = PaginationInfo(
            total_count=100, offset=0, limit=20, current_count=20
        )
        assert pagination.next_offset == 20

    def test_next_offset_last_page(self) -> None:
        """測試最後一頁時 next_offset 為 None"""
        pagination = PaginationInfo(
            total_count=100, offset=80, limit=20, current_count=20
        )
        assert pagination.next_offset is None

    def test_previous_offset_first_page(self) -> None:
        """測試第一頁時 previous_offset 為 None"""
        pagination = PaginationInfo(
            total_count=100, offset=0, limit=20, current_count=20
        )
        assert pagination.previous_offset is None

    def test_previous_offset_second_page(self) -> None:
        """測試第二頁時的 previous_offset"""
        pagination = PaginationInfo(
            total_count=100, offset=20, limit=20, current_count=20
        )
        assert pagination.previous_offset == 0

    def test_previous_offset_middle_page(self) -> None:
        """測試中間頁時的 previous_offset"""
        pagination = PaginationInfo(
            total_count=100, offset=40, limit=20, current_count=20
        )
        assert pagination.previous_offset == 20

    def test_total_pages(self) -> None:
        """測試總頁數計算"""
        # 100 項，每頁 20 項 = 5 頁
        pagination = PaginationInfo(
            total_count=100, offset=0, limit=20, current_count=20
        )
        assert pagination.total_pages == 5

    def test_total_pages_partial_last_page(self) -> None:
        """測試最後一頁不完整時的總頁數"""
        # 95 項，每頁 20 項 = 5 頁（最後一頁 15 項）
        pagination = PaginationInfo(
            total_count=95, offset=0, limit=20, current_count=20
        )
        assert pagination.total_pages == 5

    def test_current_page_first(self) -> None:
        """測試第一頁"""
        pagination = PaginationInfo(
            total_count=100, offset=0, limit=20, current_count=20
        )
        assert pagination.current_page == 1

    def test_current_page_second(self) -> None:
        """測試第二頁"""
        pagination = PaginationInfo(
            total_count=100, offset=20, limit=20, current_count=20
        )
        assert pagination.current_page == 2

    def test_current_page_last(self) -> None:
        """測試最後一頁"""
        pagination = PaginationInfo(
            total_count=100, offset=80, limit=20, current_count=20
        )
        assert pagination.current_page == 5

    def test_to_dict(self) -> None:
        """測試轉換為字典（JSON 格式）"""
        pagination = PaginationInfo(
            total_count=100, offset=20, limit=20, current_count=20
        )
        result = pagination.to_dict()

        assert result["total_count"] == 100
        assert result["offset"] == 20
        assert result["limit"] == 20
        assert result["count"] == 20  # 使用 "count" 而非 "current_count"
        assert result["has_more"] is True
        assert result["next_offset"] == 40
        assert result["previous_offset"] == 0
        assert result["total_pages"] == 5
        assert result["current_page"] == 2

    def test_to_dict_last_page(self) -> None:
        """測試最後一頁轉換為字典"""
        pagination = PaginationInfo(
            total_count=100, offset=80, limit=20, current_count=20
        )
        result = pagination.to_dict()

        assert result["has_more"] is False
        assert "next_offset" not in result  # 最後一頁沒有 next_offset
        assert result["previous_offset"] == 60

    def test_to_markdown_summary(self) -> None:
        """測試 Markdown 摘要"""
        pagination = PaginationInfo(
            total_count=100, offset=20, limit=20, current_count=20
        )
        summary = pagination.to_markdown_summary()

        assert "2/5" in summary  # Page number
        assert "21-40" in summary  # 項目範圍
        assert "100" in summary  # 總數
        assert "offset=40" in summary  # 下一頁提示

    def test_to_markdown_summary_last_page(self) -> None:
        """測試最後一頁的 Markdown 摘要"""
        pagination = PaginationInfo(
            total_count=100, offset=80, limit=20, current_count=20
        )
        summary = pagination.to_markdown_summary()

        assert "5/5" in summary  # Page number
        assert "81-100" in summary  # 項目範圍
        assert "offset=40" not in summary  # 最後一頁沒有下一頁提示


class TestPaginateResults:
    """測試 paginate_results 函數"""

    def test_paginate_first_page(self) -> None:
        """測試第一頁"""
        items = list(range(100))
        page_items, pagination = paginate_results(items, offset=0, limit=20)

        assert len(page_items) == 20
        assert page_items == list(range(20))
        assert pagination.total_count == 100
        assert pagination.offset == 0
        assert pagination.has_more is True

    def test_paginate_second_page(self) -> None:
        """測試第二頁"""
        items = list(range(100))
        page_items, pagination = paginate_results(items, offset=20, limit=20)

        assert len(page_items) == 20
        assert page_items == list(range(20, 40))
        assert pagination.offset == 20
        assert pagination.has_more is True

    def test_paginate_last_page_full(self) -> None:
        """測試最後一頁（完整）"""
        items = list(range(100))
        page_items, pagination = paginate_results(items, offset=80, limit=20)

        assert len(page_items) == 20
        assert page_items == list(range(80, 100))
        assert pagination.has_more is False
        assert pagination.next_offset is None

    def test_paginate_last_page_partial(self) -> None:
        """測試最後一頁（部分結果）"""
        items = list(range(95))
        page_items, pagination = paginate_results(items, offset=80, limit=20)

        assert len(page_items) == 15
        assert page_items == list(range(80, 95))
        assert pagination.has_more is False
        assert pagination.current_count == 15

    def test_paginate_default_limit(self) -> None:
        """測試預設 limit"""
        items = list(range(100))
        page_items, pagination = paginate_results(items)

        assert len(page_items) == DEFAULT_LIMIT
        assert pagination.limit == DEFAULT_LIMIT

    def test_paginate_negative_offset(self) -> None:
        """測試負數 offset 自動修正"""
        items = list(range(100))
        page_items, pagination = paginate_results(items, offset=-10, limit=20)

        assert pagination.offset == 0
        assert len(page_items) == 20

    def test_paginate_offset_beyond_end(self) -> None:
        """測試 offset 超過總數"""
        items = list(range(100))
        page_items, pagination = paginate_results(items, offset=200, limit=20)

        assert len(page_items) == 0
        assert pagination.has_more is False

    def test_paginate_limit_too_large(self) -> None:
        """測試 limit 超過 MAX_LIMIT"""
        items = list(range(100))
        page_items, pagination = paginate_results(items, offset=0, limit=500)

        assert pagination.limit == MAX_LIMIT

    def test_paginate_limit_too_small(self) -> None:
        """測試 limit 小於 1"""
        items = list(range(100))
        page_items, pagination = paginate_results(items, offset=0, limit=0)

        assert pagination.limit == 1

    def test_paginate_empty_list(self) -> None:
        """測試空列表"""
        items: list[int] = []
        page_items, pagination = paginate_results(items)

        assert len(page_items) == 0
        assert pagination.total_count == 0
        assert pagination.has_more is False

    def test_paginate_dict_list(self) -> None:
        """測試字典列表"""
        items = [{"id": i, "name": f"Item {i}"} for i in range(50)]
        page_items, pagination = paginate_results(items, offset=10, limit=5)

        assert len(page_items) == 5
        assert page_items[0]["id"] == 10
        assert page_items[-1]["id"] == 14
        assert pagination.total_count == 50


class TestValidatePaginationParams:
    """測試 validate_pagination_params 函數"""

    def test_validate_valid_params(self) -> None:
        """測試有效參數"""
        offset, limit, error = validate_pagination_params(0, 20)

        assert offset == 0
        assert limit == 20
        assert error is None

    def test_validate_negative_offset(self) -> None:
        """測試負數 offset"""
        offset, limit, error = validate_pagination_params(-10, 20)

        assert offset == 0
        assert limit == 20
        assert error is not None
        assert "offset must be >= 0" in error

    def test_validate_zero_limit(self) -> None:
        """測試 limit 為 0"""
        offset, limit, error = validate_pagination_params(0, 0)

        assert offset == 0
        assert limit == DEFAULT_LIMIT
        assert error is not None
        assert "limit must be >= 1" in error

    def test_validate_negative_limit(self) -> None:
        """測試負數 limit"""
        offset, limit, error = validate_pagination_params(0, -5)

        assert offset == 0
        assert limit == DEFAULT_LIMIT
        assert error is not None
        assert "limit must be >= 1" in error

    def test_validate_limit_exceeds_max(self) -> None:
        """測試 limit 超過最大值"""
        offset, limit, error = validate_pagination_params(0, 500)

        assert offset == 0
        assert limit == MAX_LIMIT
        assert error is not None
        assert f"limit cannot exceed {MAX_LIMIT}" in error

    def test_validate_limit_at_max(self) -> None:
        """測試 limit 等於最大值"""
        offset, limit, error = validate_pagination_params(0, MAX_LIMIT)

        assert offset == 0
        assert limit == MAX_LIMIT
        assert error is None

    def test_validate_multiple_errors(self) -> None:
        """測試多個錯誤（回報最後檢查到的錯誤）"""
        offset, limit, error = validate_pagination_params(-10, -5)

        assert offset == 0
        assert limit == DEFAULT_LIMIT
        assert error is not None
        # 實際實作中 limit 錯誤會覆蓋 offset 錯誤
        assert "limit" in error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
