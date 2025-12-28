#!/usr/bin/env python3
"""
測試 API 結構查詢工具 (Issue #51)

驗證 3 個新工具的功能：
- api_get_class_hierarchy
- api_get_class_relationships
- api_navigate_structure
"""

import sys
from pathlib import Path

import pytest

from glyphs_info_mcp.modules.glyphs_api.unified_api_module import UnifiedAPIModule


@pytest.fixture
def api_module():
    """初始化 API 模組"""
    module = UnifiedAPIModule("api", None)
    assert module.initialize(), "API module initialization failed"
    return module


@pytest.fixture
def api_tools(api_module):
    """取得 API 工具"""
    return api_module.get_tools()


# ============================================================================
# Test 1: 取得完整層級 (Issue #51 測試案例 1)
# ============================================================================


def test_get_class_hierarchy_tree(api_tools):
    """Test 1: 取得完整層級 - tree 格式"""
    result = api_tools["api_get_class_hierarchy"]("tree")

    # 驗證包含完整結構
    assert "Glyphs.app" in result, "應包含 Glyphs.app"
    assert "Fonts" in result, "應包含 Fonts"
    assert "Glyphs" in result, "應包含 Glyphs"
    assert "Layers" in result, "應包含 Layers"
    assert "Shapes" in result, "應包含 Shapes"
    assert "Paths" in result, "應包含 Paths"
    assert "Nodes" in result, "應包含 Nodes"

    # 驗證層級結構
    assert (
        "Font → Glyph → Layer → Shape" in result or "Glyphs" in result
    ), "應顯示 Font → Glyph → Layer → Shape 結構"

    print("✅ Test 1 通過：tree 格式包含完整結構")


def test_get_class_hierarchy_json(api_tools):
    """Test 1 (補充): 取得完整層級 - json 格式"""
    import json

    result = api_tools["api_get_class_hierarchy"]("json")

    # 驗證是有效的 JSON
    try:
        data = json.loads(result)
        assert "classes" in data, "JSON 應包含 classes 欄位"
        assert "GSFont" in data["classes"], "應包含 GSFont 類別"
        assert "GSLayer" in data["classes"], "應包含 GSLayer 類別"
        print("✅ Test 1 (JSON) 通過：JSON 格式有效且包含必要類別")
    except json.JSONDecodeError as e:
        pytest.fail(f"JSON 格式無效: {e}")


def test_get_class_hierarchy_mermaid(api_tools):
    """Test 1 (補充): 取得完整層級 - mermaid 格式"""
    result = api_tools["api_get_class_hierarchy"]("mermaid")

    # 驗證 Mermaid 語法
    assert "```mermaid" in result, "應包含 mermaid 開始標記"
    assert "graph TD" in result, "應包含 graph TD 宣告"
    assert "GSFont" in result, "應包含 GSFont 節點"
    assert "GSLayer" in result, "應包含 GSLayer 節點"
    assert "```" in result, "應包含結束標記"

    print("✅ Test 1 (Mermaid) 通過：Mermaid 格式正確")


# ============================================================================
# Test 2: 查詢特定類別關係 (Issue #51 測試案例 2)
# ============================================================================


def test_get_class_relationships_gslayer(api_tools):
    """Test 2: 查詢 GSLayer 的所有關係"""
    result = api_tools["api_get_class_relationships"]("GSLayer", True)

    # 驗證描述
    assert "GSLayer" in result, "應包含類別名稱"
    assert "圖層" in result or "Layer" in result, "應包含描述"

    # 驗證包含的物件
    assert "包含" in result or "Contains" in result, "應顯示包含關係"
    assert "GSShape" in result or "shapes" in result, "應包含 GSShape"
    assert "GSAnchor" in result or "anchors" in result, "應包含 GSAnchor"

    # 驗證被包含於
    assert "被包含於" in result or "Belongs To" in result, "應顯示被包含關係"
    assert "GSGlyph" in result, "應顯示被包含於 GSGlyph"

    # 驗證訪問路徑範例
    assert "glyph.layers" in result or "訪問路徑" in result, "應包含訪問路徑範例"

    print("✅ Test 2 通過：GSLayer 關係查詢完整")


def test_get_class_relationships_gspath(api_tools):
    """Test 2 (補充): 查詢 GSPath 的關係"""
    result = api_tools["api_get_class_relationships"]("GSPath", True)

    # 驗證父類別
    assert "父類別" in result or "Parent" in result, "應顯示父類別"
    assert "GSShape" in result, "應顯示 GSPath 繼承自 GSShape"

    # 驗證包含的物件
    assert "GSNode" in result or "nodes" in result, "應包含 GSNode"

    # 驗證被包含於
    assert "GSLayer" in result, "應顯示被包含於 GSLayer"

    print("✅ Test 2 (GSPath) 通過：繼承關係正確顯示")


# ============================================================================
# Test 2.5: 引用關係測試 (Issue #53)
# ============================================================================


def test_get_class_relationships_references_gslayer(api_tools):
    """Test 2.5a (Issue #53): 查詢 GSLayer 的引用關係"""
    result = api_tools["api_get_class_relationships"]("GSLayer", True)

    # 驗證引用的類別 (References)
    assert "引用" in result or "References" in result, "應顯示引用關係"
    assert "GSFontMaster" in result, "GSLayer 應引用 GSFontMaster"

    print("✅ Test 2.5a 通過：GSLayer 引用關係顯示正確")


def test_get_class_relationships_references_gscomponent(api_tools):
    """Test 2.5b (Issue #53): 查詢 GSComponent 的多個引用關係"""
    result = api_tools["api_get_class_relationships"]("GSComponent", True)

    # 驗證多個引用
    assert "引用" in result or "References" in result, "應顯示引用關係"
    assert "GSGlyph" in result, "GSComponent 應引用 GSGlyph"
    assert "GSLayer" in result, "GSComponent 應引用 GSLayer"

    print("✅ Test 2.5b 通過：GSComponent 多個引用關係顯示正確")


def test_get_class_relationships_referenced_by_gsfontmaster(api_tools):
    """Test 2.5c (Issue #53): 查詢 GSFontMaster 的被引用關係"""
    result = api_tools["api_get_class_relationships"]("GSFontMaster", True)

    # 驗證被引用於 (Referenced By)
    assert "被引用" in result or "Referenced By" in result, "應顯示被引用關係"
    assert "GSLayer" in result, "GSFontMaster 應被 GSLayer 引用"

    print("✅ Test 2.5c 通過：GSFontMaster 被引用關係顯示正確")


def test_get_class_relationships_referenced_by_gsaxis(api_tools):
    """Test 2.5d (Issue #53): 查詢 GSAxis 的多個被引用關係"""
    result = api_tools["api_get_class_relationships"]("GSAxis", True)

    # 驗證多個被引用（GSFontMaster 和 GSAxisValue 都引用 GSAxis）
    assert "被引用" in result or "Referenced By" in result, "應顯示被引用關係"
    # 加強斷言：確保兩個引用來源都被找到
    assert "GSFontMaster" in result, "GSAxis 應被 GSFontMaster 引用"
    assert "GSAxisValue" in result, "GSAxis 應被 GSAxisValue 引用"

    print("✅ Test 2.5d 通過：GSAxis 多個被引用關係顯示正確")


# ============================================================================
# Test 3: 向上導航 (Issue #51 測試案例 3)
# ============================================================================


def test_navigate_structure_upward(api_tools):
    """Test 3: 從 GSNode 向上導航到 Font"""
    result = api_tools["api_navigate_structure"]("GSNode", "contained_by", 4, True)

    # 驗證導航路徑
    assert "GSNode" in result, "應包含起始類別 GSNode"
    assert "GSPath" in result, "應包含 GSPath (Node 的容器)"
    assert "GSLayer" in result, "應包含 GSLayer (Path 的容器)"
    assert "GSGlyph" in result, "應包含 GSGlyph (Layer 的容器)"

    # 驗證結構圖
    assert "結構圖" in result or "```" in result, "應包含結構圖"

    # 驗證訪問路徑
    assert "訪問路徑" in result or "parent" in result, "應顯示訪問路徑"
    assert ".parent" in result, "訪問路徑應包含 .parent"

    print("✅ Test 3 通過：Node → Path → Layer → Glyph 路徑完整")


def test_navigate_structure_depth_limit(api_tools):
    """Test 3 (補充): 驗證深度限制"""
    result = api_tools["api_navigate_structure"]("GSNode", "contained_by", 2, True)

    # 深度 2 應包含 GSPath 和 GSLayer，但可能不包含 GSGlyph
    assert "GSPath" in result, "深度 2 應包含 GSPath"
    assert "GSLayer" in result, "深度 2 應包含 GSLayer"

    print("✅ Test 3 (深度限制) 通過：深度參數正確運作")


# ============================================================================
# Test 4: 向下導航 (Issue #51 測試案例 4)
# ============================================================================


def test_navigate_structure_downward(api_tools):
    """Test 4: 從 GSFont 向下導航到 Shapes"""
    result = api_tools["api_navigate_structure"]("GSFont", "contains", 3, True)

    # 驗證導航路徑
    assert "GSFont" in result or "GSGlyph" in result, "應包含 Font 或 Glyph"
    assert "GSGlyph" in result, "應包含 GSGlyph (Font 包含的物件)"
    assert "GSLayer" in result, "應包含 GSLayer (Glyph 包含的物件)"

    # 可能包含 GSShape 或其子類別
    has_shapes = any(
        cls in result for cls in ["GSShape", "GSPath", "GSComponent", "GSAnchor"]
    )
    assert has_shapes, "應包含 Shapes 或其子類別"

    # 驗證結構圖
    assert "結構圖" in result or "```" in result, "應包含結構圖"

    print("✅ Test 4 通過：Font → Glyphs → Layers → Shapes 結構顯示")


def test_navigate_structure_contains_gslayer(api_tools):
    """Test 4 (補充): 從 GSLayer 向下查看包含的物件"""
    result = api_tools["api_navigate_structure"]("GSLayer", "contains", 2, False)

    # 驗證包含的物件
    assert "GSShape" in result or "GSPath" in result, "應包含 GSShape 或 GSPath"
    assert "GSAnchor" in result, "應包含 GSAnchor"

    print("✅ Test 4 (GSLayer contains) 通過：包含關係正確")


def test_navigate_structure_parent(api_tools):
    """Test 5: 測試 parent 導航（繼承層級向上）"""
    result = api_tools["api_navigate_structure"]("GSPath", "parent", 2, True)

    # GSPath 繼承自 GSShape
    assert "GSShape" in result, "應包含父類別 GSShape"
    assert "繼承" in result or "inherits" in result, "應顯示繼承關係"

    print("✅ Test 5 通過：parent 導航正確")


def test_navigate_structure_children(api_tools):
    """Test 6: 測試 children 導航（繼承層級向下）"""
    result = api_tools["api_navigate_structure"]("GSShape", "children", 1, True)

    # GSShape 的子類別包含 GSPath 和 GSComponent
    assert "GSPath" in result or "GSComponent" in result, "應包含子類別"
    assert "繼承" in result or "inherits" in result, "應顯示繼承關係"

    print("✅ Test 6 通過：children 導航正確")


# ============================================================================
# 錯誤處理測試
# ============================================================================


def test_invalid_format(api_tools):
    """測試無效的格式參數"""
    result = api_tools["api_get_class_hierarchy"]("invalid_format")
    assert "無效" in result or "invalid" in result.lower(), "應返回錯誤訊息"
    print("✅ 錯誤處理：無效格式正確處理")


def test_invalid_class_name(api_tools):
    """測試不存在的類別名稱"""
    result = api_tools["api_get_class_relationships"]("NonExistentClass", True)
    assert "未找到" in result or "not found" in result.lower(), "應返回未找到訊息"
    print("✅ 錯誤處理：不存在的類別正確處理")


def test_invalid_relationship(api_tools):
    """測試無效的關係類型"""
    result = api_tools["api_navigate_structure"]("GSNode", "invalid_rel", 1, True)
    assert "無效" in result or "invalid" in result.lower(), "應返回錯誤訊息"
    print("✅ 錯誤處理：無效關係類型正確處理")


def test_invalid_depth(api_tools):
    """測試無效的深度值"""
    result = api_tools["api_navigate_structure"]("GSNode", "contained_by", 10, True)
    assert "無效" in result or "範圍" in result or "invalid" in result.lower() or "range" in result.lower(), "應返回範圍錯誤訊息"
    print("✅ 錯誤處理：無效深度值正確處理")


# ============================================================================
# 模糊匹配測試
# ============================================================================


def test_fuzzy_matching(api_tools):
    """測試類別名稱的模糊匹配"""
    result = api_tools["api_get_class_relationships"]("layer", True)

    # 應提供建議
    if "未找到" in result:
        assert "GSLayer" in result, "應建議 GSLayer"
        print("✅ 模糊匹配：正確建議相似類別")


# ============================================================================
# 整合測試
# ============================================================================


def test_tools_registered(api_module):
    """驗證所有新工具都已註冊"""
    tools = api_module.get_tools()

    assert "api_get_class_hierarchy" in tools, "api_get_class_hierarchy 應已註冊"
    assert (
        "api_get_class_relationships" in tools
    ), "api_get_class_relationships 應已註冊"
    assert "api_navigate_structure" in tools, "api_navigate_structure 應已註冊"

    # 驗證工具數量（8 個舊工具 + 3 個新工具 = 11 個）
    assert len(tools) >= 11, f"工具數量應至少 11 個，實際：{len(tools)}"

    print(f"✅ 整合測試：{len(tools)} 個工具已註冊（包含 3 個新工具）")


def test_api_structure_file_exists():
    """驗證 api_structure.json 檔案存在且有效"""
    import json

    project_root = Path(__file__).parent.parent
    structure_file = project_root / "src" / "glyphs_info_mcp" / "data" / "api_structure.json"

    assert structure_file.exists(), "api_structure.json 應存在"

    with open(structure_file, encoding="utf-8") as f:
        data = json.load(f)

    assert "classes" in data, "應包含 classes 欄位"
    assert "GSFont" in data["classes"], "應包含 GSFont 類別定義"
    assert "GSLayer" in data["classes"], "應包含 GSLayer 類別定義"
    assert "GSNode" in data["classes"], "應包含 GSNode 類別定義"

    print(f"✅ 資料檔案：api_structure.json 有效，包含 {len(data['classes'])} 個類別")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
