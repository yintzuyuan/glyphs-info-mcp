"""Tests for class_hierarchy module."""

import pytest

from glyphs_info_mcp.data.class_hierarchy import (
    CLASS_NAMES,
    COMPOSITION,
    INHERITANCE,
    OFFICIAL_DIAGRAM_URL,
    PYTHON_TO_DISPLAY,
    REFERENCES,
    build_structure_dict,
    get_children,
    get_display_name,
    get_inheritance_children,
    get_inheritance_parent,
    get_parent,
    get_python_class,
)


class TestClassNames:
    """Tests for CLASS_NAMES mapping."""

    def test_core_classes_exist(self) -> None:
        """Core Glyphs classes should be in the mapping."""
        core_classes = [
            "Glyphs.app",
            "Fonts",
            "Glyphs",
            "Layers",
            "Masters",
            "Shapes",
            "Paths",
            "Nodes",
        ]
        for display_name in core_classes:
            assert display_name in CLASS_NAMES, f"{display_name} should be in CLASS_NAMES"

    def test_python_class_names_start_with_gs(self) -> None:
        """Python class names should start with GS (except Glyphs singleton)."""
        for display_name, python_class in CLASS_NAMES.items():
            if display_name == "Glyphs.app":
                assert python_class == "Glyphs"
            else:
                assert python_class.startswith("GS"), f"{python_class} should start with GS"

    def test_reverse_mapping_complete(self) -> None:
        """PYTHON_TO_DISPLAY should be complete reverse of CLASS_NAMES."""
        assert len(PYTHON_TO_DISPLAY) == len(CLASS_NAMES)
        for display_name, python_class in CLASS_NAMES.items():
            assert PYTHON_TO_DISPLAY[python_class] == display_name


class TestComposition:
    """Tests for COMPOSITION relationships."""

    def test_root_is_glyphs_app(self) -> None:
        """Glyphs.app should be the root of the hierarchy."""
        assert "Glyphs.app" in COMPOSITION
        # Glyphs.app should not be a child of anything
        for children in COMPOSITION.values():
            assert "Glyphs.app" not in children

    def test_fonts_children(self) -> None:
        """Fonts should contain expected children."""
        fonts_children = COMPOSITION.get("Fonts", [])
        assert "Glyphs" in fonts_children
        assert "Masters" in fonts_children
        assert "Axes" in fonts_children

    def test_layers_children(self) -> None:
        """Layers should contain Shapes, Anchors, Hints, Guides."""
        layers_children = COMPOSITION.get("Layers", [])
        assert "Shapes" in layers_children
        assert "Anchors" in layers_children
        assert "Hints" in layers_children
        assert "Guides" in layers_children

    def test_paths_contain_nodes(self) -> None:
        """Paths should contain Nodes."""
        assert "Nodes" in COMPOSITION.get("Paths", [])

    def test_no_orphan_children(self) -> None:
        """All children in COMPOSITION should be valid CLASS_NAMES keys."""
        for children in COMPOSITION.values():
            for child in children:
                assert child in CLASS_NAMES, f"Child '{child}' not in CLASS_NAMES"


class TestInheritance:
    """Tests for INHERITANCE relationships."""

    def test_shapes_inheritance(self) -> None:
        """Shapes should be parent of Paths and Components."""
        shapes_children = INHERITANCE.get("Shapes", [])
        assert "Paths" in shapes_children
        assert "Components" in shapes_children


class TestReferences:
    """Tests for REFERENCES relationships."""

    def test_axis_id_reference(self) -> None:
        """axisID should link Axes to AxisValues."""
        axis_refs = REFERENCES.get("axisID", [])
        assert ("Axes", "AxisValues") in axis_refs

    def test_master_id_reference(self) -> None:
        """masterID should link Masters to Layers."""
        master_refs = REFERENCES.get("masterID", [])
        assert ("Masters", "Layers") in master_refs


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_get_python_class(self) -> None:
        """get_python_class should return correct Python class."""
        assert get_python_class("Fonts") == "GSFont"
        assert get_python_class("Layers") == "GSLayer"
        assert get_python_class("Glyphs.app") == "Glyphs"
        assert get_python_class("NonExistent") is None

    def test_get_display_name(self) -> None:
        """get_display_name should return correct display name."""
        assert get_display_name("GSFont") == "Fonts"
        assert get_display_name("GSLayer") == "Layers"
        assert get_display_name("Glyphs") == "Glyphs.app"
        assert get_display_name("NonExistent") is None

    def test_get_children(self) -> None:
        """get_children should return composition children."""
        assert "Layers" in get_children("Glyphs")
        assert "Nodes" in get_children("Paths")
        assert get_children("Nodes") == []  # Leaf node

    def test_get_parent(self) -> None:
        """get_parent should return composition parent."""
        assert get_parent("Layers") == "Glyphs"
        assert get_parent("Nodes") == "Paths"
        assert get_parent("Glyphs.app") is None  # Root

    def test_get_inheritance_parent(self) -> None:
        """get_inheritance_parent should return inheritance parent."""
        assert get_inheritance_parent("Paths") == "Shapes"
        assert get_inheritance_parent("Components") == "Shapes"
        assert get_inheritance_parent("Layers") is None

    def test_get_inheritance_children(self) -> None:
        """get_inheritance_children should return inheritance children."""
        children = get_inheritance_children("Shapes")
        assert "Paths" in children
        assert "Components" in children
        assert get_inheritance_children("Paths") == []


class TestBuildStructureDict:
    """Tests for build_structure_dict function."""

    def test_returns_dict_with_classes(self) -> None:
        """build_structure_dict should return dict with classes key."""
        result = build_structure_dict()
        assert "classes" in result
        assert "source" in result
        assert result["source"] == OFFICIAL_DIAGRAM_URL

    def test_all_classes_included(self) -> None:
        """All CLASS_NAMES should be in the structure."""
        result = build_structure_dict()
        for python_class in CLASS_NAMES.values():
            assert python_class in result["classes"]

    def test_glyphs_is_singleton(self) -> None:
        """Glyphs should be marked as singleton."""
        result = build_structure_dict()
        assert result["classes"]["Glyphs"]["type"] == "singleton"

    def test_contains_relationship(self) -> None:
        """Classes should have contains relationship."""
        result = build_structure_dict()
        gsfont = result["classes"]["GSFont"]
        assert "contains" in gsfont
        assert "GSGlyph" in gsfont["contains"]

    def test_contained_by_relationship(self) -> None:
        """Classes should have contained_by relationship."""
        result = build_structure_dict()
        gsglyph = result["classes"]["GSGlyph"]
        assert "contained_by" in gsglyph
        assert "GSFont" in gsglyph["contained_by"]

    def test_inheritance_relationship(self) -> None:
        """GSPath should have GSShape as parent."""
        result = build_structure_dict()
        gspath = result["classes"]["GSPath"]
        assert gspath.get("parent") == "GSShape"

    def test_inheritance_children(self) -> None:
        """GSShape should have children."""
        result = build_structure_dict()
        gsshape = result["classes"]["GSShape"]
        assert "children" in gsshape
        assert "GSPath" in gsshape["children"]
        assert "GSComponent" in gsshape["children"]


class TestOfficialDiagramUrl:
    """Tests for OFFICIAL_DIAGRAM_URL."""

    def test_url_is_valid(self) -> None:
        """URL should be a valid HTTPS URL."""
        assert OFFICIAL_DIAGRAM_URL.startswith("https://")
        assert "docu.glyphsapp.com" in OFFICIAL_DIAGRAM_URL
        assert "objectmodel.png" in OFFICIAL_DIAGRAM_URL
