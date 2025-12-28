#!/usr/bin/env python3
"""
測試 Response Format 功能
"""

import json
import sys
from pathlib import Path

import pytest

# 添加共享核心庫路徑
shared_core_path = str(Path(__file__).parent.parent / "src" / "shared")
if shared_core_path not in sys.path:
    sys.path.insert(0, shared_core_path)

from glyphs_info_mcp.shared.core.response_utils import (
    ResponseFormat,
    format_as_json,
    format_as_markdown,
    format_response,
    format_search_results,
)


class TestResponseFormat:
    """測試回應格式枚舉"""

    def test_response_format_enum(self) -> None:
        """測試 ResponseFormat 枚舉值"""
        assert ResponseFormat.JSON.value == "json"
        assert ResponseFormat.MARKDOWN.value == "markdown"

    def test_response_format_from_string(self) -> None:
        """測試從字串建立枚舉"""
        assert ResponseFormat("json") == ResponseFormat.JSON
        assert ResponseFormat("markdown") == ResponseFormat.MARKDOWN


class TestFormatAsJSON:
    """測試 JSON 格式化"""

    def test_format_dict_as_json(self) -> None:
        """測試字典轉 JSON"""
        data = {
            "name": "GSFont",
            "type": "class",
            "properties": ["masters", "glyphs"],
        }
        result = format_as_json(data)

        # 驗證是合法的 JSON
        parsed = json.loads(result)
        assert parsed["name"] == "GSFont"
        assert parsed["type"] == "class"
        assert len(parsed["properties"]) == 2

    def test_format_list_as_json(self) -> None:
        """測試列表轉 JSON"""
        data = [
            {"name": "GSFont", "type": "class"},
            {"name": "GSLayer", "type": "class"},
        ]
        result = format_as_json(data)

        # 驗證是合法的 JSON 陣列
        parsed = json.loads(result)
        assert len(parsed) == 2
        assert parsed[0]["name"] == "GSFont"

    def test_json_with_unicode(self) -> None:
        """測試 JSON 支援 Unicode"""
        data = {"title": "中文標題", "content": "內容"}
        result = format_as_json(data)

        # ensure_ascii=False 應該保留中文
        assert "中文標題" in result
        assert "內容" in result


class TestFormatAsMarkdown:
    """測試 Markdown 格式化"""

    def test_format_simple_dict(self) -> None:
        """測試簡單字典轉 Markdown"""
        data = {
            "title": "GSFont Class",
            "type": "class",
            "description": "A font object",
        }
        result = format_as_markdown(data)

        assert "# GSFont Class" in result
        assert "**Type**: class" in result
        assert "**Description**: A font object" in result

    def test_format_dict_with_list(self) -> None:
        """測試包含列表的字典"""
        data = {
            "title": "API Methods",
            "methods": ["addMaster", "removeMaster", "save"],
        }
        result = format_as_markdown(data)

        assert "# API Methods" in result
        assert "**Methods**:" in result
        assert "- addMaster" in result
        assert "- removeMaster" in result

    def test_format_nested_dict(self) -> None:
        """測試嵌套字典"""
        data = {
            "title": "Class Info",
            "metadata": {"version": "3.0", "stable": True},
        }
        result = format_as_markdown(data)

        assert "# Class Info" in result
        assert "**Metadata**:" in result
        assert "**Version**: 3.0" in result
        assert "**Stable**: Yes" in result  # bool 轉換

    def test_format_list_of_dicts(self) -> None:
        """測試字典列表轉 Markdown"""
        data = [
            {"title": "GSFont", "type": "class"},
            {"title": "GSLayer", "type": "class"},
        ]
        result = format_as_markdown(data)

        assert "## Search Results (2 items)" in result
        assert "### 1. GSFont" in result
        assert "### 2. GSLayer" in result

    def test_format_empty_list(self) -> None:
        """測試空列表"""
        result = format_as_markdown([])
        assert "No results" in result

    def test_boolean_formatting(self) -> None:
        """測試布林值格式化"""
        data = {"title": "Test", "is_active": True, "is_deprecated": False}
        result = format_as_markdown(data)

        assert "**Is Active**: Yes" in result
        assert "**Is Deprecated**: No" in result

    def test_none_value_formatting(self) -> None:
        """測試 None 值格式化"""
        data = {"title": "Test", "optional_field": None}
        result = format_as_markdown(data)

        assert "**Optional Field**: N/A" in result


class TestFormatResponse:
    """測試統一格式化函數"""

    def test_format_response_json(self) -> None:
        """測試指定 JSON 格式"""
        data = {"name": "Test", "value": 123}
        result = format_response(data, ResponseFormat.JSON)

        # 應該是合法的 JSON
        parsed = json.loads(result)
        assert parsed["name"] == "Test"

    def test_format_response_markdown(self) -> None:
        """測試指定 Markdown 格式"""
        data = {"title": "Test", "value": 123}
        result = format_response(data, ResponseFormat.MARKDOWN)

        # 應該包含 Markdown 標記
        assert "#" in result
        assert "**" in result

    def test_format_response_string_param(self) -> None:
        """測試使用字串參數指定格式"""
        data = {"name": "Test"}

        # 測試字串 "json"
        result_json = format_response(data, "json")
        assert json.loads(result_json)  # 應該是合法 JSON

        # 測試字串 "markdown"
        result_md = format_response(data, "markdown")
        assert "**" in result_md


class TestFormatSearchResults:
    """測試搜尋結果格式化"""

    def test_format_search_results_markdown(self) -> None:
        """測試 Markdown 格式的搜尋結果"""
        results = [
            {"title": "GSFont", "type": "class", "content": "Font class"},
            {"title": "GSLayer", "type": "class", "content": "Layer class"},
        ]
        result = format_search_results(
            results, query="font", response_format="markdown"
        )

        assert '# Search Results: "font"' in result
        assert "**Found**: 2 items" in result
        assert "## 1. GSFont" in result
        assert "## 2. GSLayer" in result

    def test_format_search_results_json(self) -> None:
        """測試 JSON 格式的搜尋結果"""
        results = [
            {"title": "GSFont", "type": "class"},
        ]
        result = format_search_results(results, query="font", response_format="json")

        parsed = json.loads(result)
        assert parsed["query"] == "font"
        assert parsed["count"] == 1
        assert len(parsed["results"]) == 1

    def test_format_search_results_with_metadata(self) -> None:
        """測試帶元數據的搜尋結果"""
        results = [{"title": "Item 1"}]
        metadata = {"total_count": 100, "has_more": True, "offset": 0}

        result = format_search_results(
            results, query="test", response_format="markdown", metadata=metadata
        )

        assert "**Total**: 100 items" in result
        assert "More results available" in result

    def test_format_empty_search_results(self) -> None:
        """測試空搜尋結果"""
        result = format_search_results([], query="nonexistent")

        assert "No matching results found" in result or "No results" in result

    def test_long_content_truncation_in_markdown(self) -> None:
        """測試 Markdown 中過長內容的截斷"""
        results = [
            {
                "title": "Long Content",
                "content": "x" * 1000,  # 很長的內容
            }
        ]
        result = format_search_results(results, response_format="markdown")

        # 內容應該被截斷
        assert "x" * 500 in result  # 前 500 個字元
        assert "..." in result  # 截斷標記


class TestFormatIntegration:
    """測試格式化整合場景"""

    def test_real_world_api_response(self) -> None:
        """測試真實 API 回應格式化"""
        api_response = {
            "class": "GSFont",
            "properties": [
                {"name": "masters", "type": "list"},
                {"name": "glyphs", "type": "list"},
            ],
            "methods": [
                {"name": "save", "params": [], "returns": "bool"},
                {"name": "close", "params": [], "returns": "None"},
            ],
        }

        # JSON 格式
        json_result = format_response(api_response, "json")
        parsed = json.loads(json_result)
        assert parsed["class"] == "GSFont"

        # Markdown 格式
        md_result = format_response(api_response, "markdown")
        assert "**Class**: GSFont" in md_result
        assert "**Properties**:" in md_result

    def test_consistency_between_formats(self) -> None:
        """測試不同格式包含相同資訊"""
        data = {
            "title": "Test",
            "count": 5,
            "items": ["a", "b", "c"],
        }

        json_result = format_response(data, "json")
        md_result = format_response(data, "markdown")

        # JSON 應該包含完整資料
        parsed = json.loads(json_result)
        assert parsed["count"] == 5
        assert len(parsed["items"]) == 3

        # Markdown 應該也包含相同資訊
        assert "5" in md_result
        assert "a" in md_result
        assert "b" in md_result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
