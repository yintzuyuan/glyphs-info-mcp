"""
Section Parser 單元測試

測試 Markdown 段落解析器的功能：
- 解析 ##, ###, #### 標題結構
- 找出特定行所屬的段落
- 智慧截取段落內容
"""

import pytest

from glyphs_info_mcp.modules.glyphs_handbook.handbook.section_parser import (
    Section,
    MarkdownSectionParser,
)


# =============================================================================
# 測試資料
# =============================================================================

SAMPLE_MARKDOWN = """## [Anchors](#anchors)

Anchors are special points that fulfill multiple tasks in Glyphs.

### [Adding, Editing, & Removing Anchors](#anchors/adding)

Insert an anchor by `Control`-clicking or right-clicking the Edit View canvas.
An anchor named `new anchor` will be placed at the click position.
Its name is already selected for renaming.

Double-click an anchor to rename it.

### [Mark to Base Positioning](#mark-to-base-positioning)

Glyphs can automatically build the `mark` feature using anchors.
The combining diacritical marks must contain underscore-anchors.

### [Cursive Attachment](#cursive-attachment)

Enable proper cursive attachment in Arabic typesetting.
"""

LONG_SECTION_MARKDOWN = """## [Components](#components)

Components are glyphs used as shapes inside other glyphs.

### [Building Composites](#building-composites)

When adding a new composite glyph, Glyphs will automatically add the necessary components.
For example, adding an `eacute` glyph to a font will automatically build it.
Line 3 of the section.
Line 4 of the section.
Line 5 of the section.
Line 6 of the section.
Line 7 of the section.
Line 8 of the section.
Line 9 of the section.
Line 10 of the section.
Line 11 of the section.
Line 12 of the section.
Line 13 of the section.
Line 14 of the section.
Line 15 of the section.
Line 16 of the section.
Line 17 of the section with keyword composite here.
Line 18 of the section.
Line 19 of the section.
Line 20 of the section.

### [Next Section](#next-section)

This is the next section.
"""


# =============================================================================
# Phase 1: Section Parser 基礎架構測試
# =============================================================================

class TestSectionDataStructure:
    """測試 Section 資料結構"""

    def test_section_has_required_fields(self) -> None:
        """Section 應包含必要欄位"""
        section = Section(
            level=3,
            title="Test Section",
            anchor="test-section",
            start_line=0,
            end_line=10,
        )
        assert section.level == 3
        assert section.title == "Test Section"
        assert section.anchor == "test-section"
        assert section.start_line == 0
        assert section.end_line == 10


class TestParseSections:
    """測試 parse_sections() 方法"""

    def test_parse_empty_content(self) -> None:
        """空內容應返回空列表"""
        parser = MarkdownSectionParser()
        sections = parser.parse_sections("")
        assert sections == []

    def test_parse_single_h2_section(self) -> None:
        """解析單一 ## 標題"""
        content = "## [Title](#anchor)\n\nSome content here."
        parser = MarkdownSectionParser()
        sections = parser.parse_sections(content)

        assert len(sections) == 1
        assert sections[0].level == 2
        assert sections[0].title == "Title"
        assert sections[0].anchor == "anchor"
        assert sections[0].start_line == 0

    def test_parse_h3_sections(self) -> None:
        """解析 ### 子章節"""
        parser = MarkdownSectionParser()
        sections = parser.parse_sections(SAMPLE_MARKDOWN)

        # 應該有 1 個 ## 和 3 個 ###
        assert len(sections) == 4

        # 驗證第一個 ## 標題
        assert sections[0].level == 2
        assert sections[0].title == "Anchors"

        # 驗證第一個 ### 標題
        assert sections[1].level == 3
        assert sections[1].title == "Adding, Editing, & Removing Anchors"
        assert sections[1].anchor == "anchors/adding"

        # 驗證第二個 ### 標題
        assert sections[2].level == 3
        assert sections[2].title == "Mark to Base Positioning"

        # 驗證第三個 ### 標題
        assert sections[3].level == 3
        assert sections[3].title == "Cursive Attachment"

    def test_parse_section_boundaries(self) -> None:
        """驗證段落邊界正確"""
        parser = MarkdownSectionParser()
        sections = parser.parse_sections(SAMPLE_MARKDOWN)

        # 第一個段落應在第二個段落開始前結束
        assert sections[0].end_line < sections[1].start_line
        # 第二個段落應在第三個段落開始前結束
        assert sections[1].end_line < sections[2].start_line

    def test_parse_title_without_anchor(self) -> None:
        """解析沒有錨點的標題"""
        content = "## Simple Title\n\nContent here."
        parser = MarkdownSectionParser()
        sections = parser.parse_sections(content)

        assert len(sections) == 1
        assert sections[0].title == "Simple Title"
        assert sections[0].anchor == ""  # 沒有錨點


class TestFindSectionForLine:
    """測試 find_section_for_line() 方法"""

    def test_find_section_for_line_in_first_section(self) -> None:
        """找出第一個段落內的行"""
        parser = MarkdownSectionParser()
        sections = parser.parse_sections(SAMPLE_MARKDOWN)

        # 第 2 行（索引 2）應該在第一個 ## 段落內
        section = parser.find_section_for_line(sections, 2)
        assert section is not None
        assert section.title == "Anchors"

    def test_find_section_for_line_in_subsection(self) -> None:
        """找出子章節內的行"""
        parser = MarkdownSectionParser()
        sections = parser.parse_sections(SAMPLE_MARKDOWN)

        # 找到 "Mark to Base Positioning" 段落的行
        lines = SAMPLE_MARKDOWN.split('\n')
        mark_line = None
        for i, line in enumerate(lines):
            if "Mark to Base Positioning" in line:
                mark_line = i + 2  # 標題後兩行的內容行
                break

        if mark_line:
            section = parser.find_section_for_line(sections, mark_line)
            assert section is not None
            assert section.title == "Mark to Base Positioning"

    def test_find_section_for_line_not_found(self) -> None:
        """找不到段落時返回 None"""
        parser = MarkdownSectionParser()
        sections = parser.parse_sections(SAMPLE_MARKDOWN)

        # 超出範圍的行號
        section = parser.find_section_for_line(sections, 9999)
        assert section is None


# =============================================================================
# Phase 2: 智慧截取邏輯測試
# =============================================================================

class TestExtractSmartExcerpt:
    """測試 extract_smart_excerpt() 方法"""

    def test_short_section_returns_complete(self) -> None:
        """短段落（≤15 行）應返回完整內容"""
        parser = MarkdownSectionParser()
        sections = parser.parse_sections(SAMPLE_MARKDOWN)
        lines = SAMPLE_MARKDOWN.split('\n')

        # "Cursive Attachment" 是短段落
        cursive_section = None
        for s in sections:
            if s.title == "Cursive Attachment":
                cursive_section = s
                break

        assert cursive_section is not None
        excerpt = parser.extract_smart_excerpt(cursive_section, "cursive", lines)

        # 應包含標題
        assert "Cursive Attachment" in excerpt
        # 應包含內容
        assert "Arabic typesetting" in excerpt

    def test_long_section_truncated_with_marker(self) -> None:
        """長段落應截取並標示省略"""
        parser = MarkdownSectionParser()
        sections = parser.parse_sections(LONG_SECTION_MARKDOWN)
        lines = LONG_SECTION_MARKDOWN.split('\n')

        # "Building Composites" 是長段落（超過 15 行）
        building_section = None
        for s in sections:
            if s.title == "Building Composites":
                building_section = s
                break

        assert building_section is not None
        excerpt = parser.extract_smart_excerpt(building_section, "composite", lines)

        # 應包含標題
        assert "Building Composites" in excerpt
        # 應包含省略標記
        assert "..." in excerpt or "省略" in excerpt

    def test_excerpt_centers_on_match(self) -> None:
        """截取應以匹配位置為中心"""
        parser = MarkdownSectionParser()
        sections = parser.parse_sections(LONG_SECTION_MARKDOWN)
        lines = LONG_SECTION_MARKDOWN.split('\n')

        building_section = None
        for s in sections:
            if s.title == "Building Composites":
                building_section = s
                break

        assert building_section is not None
        # 搜尋在第 17 行的關鍵字
        excerpt = parser.extract_smart_excerpt(building_section, "keyword", lines)

        # 應包含關鍵字所在行
        assert "keyword" in excerpt.lower()

    def test_excerpt_preserves_title(self) -> None:
        """截取的內容應保留段落標題"""
        parser = MarkdownSectionParser()
        sections = parser.parse_sections(LONG_SECTION_MARKDOWN)
        lines = LONG_SECTION_MARKDOWN.split('\n')

        building_section = None
        for s in sections:
            if s.title == "Building Composites":
                building_section = s
                break

        assert building_section is not None
        excerpt = parser.extract_smart_excerpt(building_section, "composite", lines)

        # 第一行應是標題
        first_line = excerpt.split('\n')[0]
        assert "Building Composites" in first_line or "###" in first_line


# =============================================================================
# 整合測試
# =============================================================================

class TestIntegration:
    """整合測試"""

    def test_full_workflow(self) -> None:
        """完整工作流程測試"""
        parser = MarkdownSectionParser()

        # 1. 解析段落
        sections = parser.parse_sections(SAMPLE_MARKDOWN)
        assert len(sections) > 0

        # 2. 搜尋關鍵字並找到對應段落
        lines = SAMPLE_MARKDOWN.split('\n')
        for i, line in enumerate(lines):
            if "cursive" in line.lower():
                section = parser.find_section_for_line(sections, i)
                assert section is not None

                # 3. 截取內容
                excerpt = parser.extract_smart_excerpt(section, "cursive", lines)
                assert "Cursive" in excerpt
                break
