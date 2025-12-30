"""
Tests for TOC Parser - Issue #17

Tests the parsing of Handbook table of contents from single-page version.
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

# Import will be created in Phase 2
from glyphs_info_mcp.modules.glyphs_handbook.handbook.toc_parser import (
    TocEntry,
    parse_headings,
    build_title_file_mapping,
    build_toc_tree,
)


class TestParseHeadings:
    """Tests for parse_headings function"""

    def test_parse_level_2_headings(self) -> None:
        """Should parse ## headings as level 2"""
        content = """# Glyphs Handbook

## Glyphs

Some content here.

## Create

More content.
"""
        headings = parse_headings(content)

        assert len(headings) == 2
        assert headings[0] == ("## Glyphs", 2)
        assert headings[1] == ("## Create", 2)

    def test_parse_level_3_headings(self) -> None:
        """Should parse ### headings as level 3"""
        content = """## Glyphs

### Glyphs Mini

Some content.

### Community

More content.
"""
        headings = parse_headings(content)

        assert len(headings) == 3
        assert headings[0] == ("## Glyphs", 2)
        assert headings[1] == ("### Glyphs Mini", 3)
        assert headings[2] == ("### Community", 3)

    def test_parse_level_4_headings(self) -> None:
        """Should parse #### headings as level 4"""
        content = """### Drawing Paths

#### Draw Tool

Content.

#### Pencil Tool

Content.
"""
        headings = parse_headings(content)

        assert len(headings) == 3
        assert headings[0] == ("### Drawing Paths", 3)
        assert headings[1] == ("#### Draw Tool", 4)
        assert headings[2] == ("#### Pencil Tool", 4)

    def test_skip_level_1_headings(self) -> None:
        """Should skip # headings (document title)"""
        content = """# Glyphs Handbook

## First Chapter

Content.
"""
        headings = parse_headings(content)

        assert len(headings) == 1
        assert headings[0] == ("## First Chapter", 2)

    def test_empty_content(self) -> None:
        """Should return empty list for empty content"""
        headings = parse_headings("")
        assert headings == []

    def test_no_headings(self) -> None:
        """Should return empty list when no headings found"""
        content = "Just some plain text without any headings."
        headings = parse_headings(content)
        assert headings == []


class TestBuildTitleFileMapping:
    """Tests for build_title_file_mapping function"""

    def test_build_mapping_from_files(self) -> None:
        """Should build mapping from first line of each file"""
        with TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)

            # Create test files
            (cache_dir / "glyphs.md").write_text("## Glyphs\n\nContent here.")
            (cache_dir / "create.md").write_text("## Create\n\nMore content.")
            (cache_dir / "palette_fit-curve.md").write_text(
                "### Fit Curve\n\nPalette content."
            )

            mapping = build_title_file_mapping(cache_dir)

            assert mapping["## Glyphs"] == "glyphs.md"
            assert mapping["## Create"] == "create.md"
            assert mapping["### Fit Curve"] == "palette_fit-curve.md"

    def test_skip_non_md_files(self) -> None:
        """Should only process .md files"""
        with TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)

            (cache_dir / "glyphs.md").write_text("## Glyphs\n\nContent.")
            (cache_dir / "cache-info.json").write_text('{"version": "1.0"}')
            (cache_dir / "readme.txt").write_text("## Not a chapter")

            mapping = build_title_file_mapping(cache_dir)

            assert len(mapping) == 1
            assert "## Glyphs" in mapping

    def test_empty_directory(self) -> None:
        """Should return empty mapping for empty directory"""
        with TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            mapping = build_title_file_mapping(cache_dir)
            assert mapping == {}


class TestBuildTocTree:
    """Tests for build_toc_tree function"""

    def test_build_flat_tree(self) -> None:
        """Should build flat tree for same-level headings"""
        headings = [
            ("## Glyphs", 2),
            ("## Create", 2),
            ("## Settings", 2),
        ]
        mapping = {
            "## Glyphs": "glyphs.md",
            "## Create": "create.md",
            "## Settings": "settings.md",
        }

        tree = build_toc_tree(headings, mapping)

        assert len(tree) == 3
        assert tree[0].title == "Glyphs"
        assert tree[0].level == 2
        assert tree[0].file == "glyphs.md"
        assert tree[0].children == []

    def test_build_nested_tree(self) -> None:
        """Should build nested tree with parent-child relationships"""
        headings = [
            ("## Glyphs", 2),
            ("### Glyphs Mini", 3),
            ("### Community", 3),
            ("## Create", 2),
        ]
        mapping = {
            "## Glyphs": "glyphs.md",
            "### Glyphs Mini": "glyphs_glyphs-mini.md",
            "### Community": "glyphs_community.md",
            "## Create": "create.md",
        }

        tree = build_toc_tree(headings, mapping)

        assert len(tree) == 2  # Two top-level entries

        # First entry has children
        glyphs = tree[0]
        assert glyphs.title == "Glyphs"
        assert len(glyphs.children) == 2
        assert glyphs.children[0].title == "Glyphs Mini"
        assert glyphs.children[1].title == "Community"

        # Second entry has no children
        create = tree[1]
        assert create.title == "Create"
        assert create.children == []

    def test_build_deeply_nested_tree(self) -> None:
        """Should handle multiple nesting levels"""
        headings = [
            ("## Drawing Paths", 2),
            ("### Tools", 3),
            ("#### Draw Tool", 4),
            ("#### Pencil Tool", 4),
            ("### Techniques", 3),
        ]
        mapping = {
            "## Drawing Paths": "drawing-paths.md",
            "### Tools": "drawing-paths_tools.md",
            "#### Draw Tool": "drawing-paths_tools_draw-tool.md",
            "#### Pencil Tool": "drawing-paths_tools_pencil-tool.md",
            "### Techniques": "drawing-paths_techniques.md",
        }

        tree = build_toc_tree(headings, mapping)

        assert len(tree) == 1

        drawing_paths = tree[0]
        assert drawing_paths.title == "Drawing Paths"
        assert len(drawing_paths.children) == 2  # Tools and Techniques

        tools = drawing_paths.children[0]
        assert tools.title == "Tools"
        assert len(tools.children) == 2  # Draw Tool and Pencil Tool
        assert tools.children[0].title == "Draw Tool"
        assert tools.children[1].title == "Pencil Tool"

    def test_filter_entries_without_files(self) -> None:
        """Should skip entries without files by default"""
        headings = [
            ("## Glyphs", 2),
            ("### Unmapped Section", 3),  # No file mapping
            ("## Create", 2),
        ]
        mapping = {
            "## Glyphs": "glyphs.md",
            "## Create": "create.md",
            # No mapping for "### Unmapped Section"
        }

        tree = build_toc_tree(headings, mapping)

        # Only 2 entries (Glyphs and Create), Unmapped Section is filtered out
        assert len(tree) == 2
        assert tree[0].title == "Glyphs"
        assert tree[0].file == "glyphs.md"
        assert tree[0].children == []  # No children because Unmapped was filtered
        assert tree[1].title == "Create"

    def test_include_all_entries(self) -> None:
        """Should include entries without files when include_all=True"""
        headings = [
            ("## Glyphs", 2),
            ("### Unmapped Section", 3),
        ]
        mapping = {
            "## Glyphs": "glyphs.md",
            # No mapping for "### Unmapped Section"
        }

        tree = build_toc_tree(headings, mapping, include_all=True)

        assert tree[0].file == "glyphs.md"
        assert len(tree[0].children) == 1
        assert tree[0].children[0].file is None
        assert tree[0].children[0].title == "Unmapped Section"


class TestTocEntry:
    """Tests for TocEntry dataclass"""

    def test_create_entry(self) -> None:
        """Should create TocEntry with all fields"""
        entry = TocEntry(
            title="Glyphs",
            level=2,
            file="glyphs.md",
            children=[],
        )

        assert entry.title == "Glyphs"
        assert entry.level == 2
        assert entry.file == "glyphs.md"
        assert entry.children == []

    def test_to_dict(self) -> None:
        """Should convert to dictionary"""
        child = TocEntry(title="Mini", level=3, file="mini.md", children=[])
        entry = TocEntry(
            title="Glyphs",
            level=2,
            file="glyphs.md",
            children=[child],
        )

        d = entry.to_dict()

        assert d["title"] == "Glyphs"
        assert d["level"] == 2
        assert d["file"] == "glyphs.md"
        assert len(d["children"]) == 1
        assert d["children"][0]["title"] == "Mini"

    def test_to_dict_with_none_file(self) -> None:
        """Should handle None file in to_dict"""
        entry = TocEntry(title="Unmapped", level=3, file=None, children=[])

        d = entry.to_dict()

        assert d["file"] is None
