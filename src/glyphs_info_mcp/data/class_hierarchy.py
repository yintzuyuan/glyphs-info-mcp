"""
Glyphs API Class Hierarchy

Source: https://docu.glyphsapp.com/_images/objectmodel.png

This module defines the class hierarchy relationships for Glyphs.app API,
derived from the official object model diagram.
"""

from typing import Final

# Official diagram URL for reference
OFFICIAL_DIAGRAM_URL: Final[str] = "https://docu.glyphsapp.com/_images/objectmodel.png"

# =============================================================================
# Composition Relationships (solid lines in diagram)
# Parent -> [Children]
# =============================================================================
# Note: In the official diagram, Shapes -> Paths/Components appears as a tree
# structure, but this represents inheritance (Paths/Components extend Shapes).
# For containment: Layers contains Shapes (abstract), and concretely contains
# Paths and Components. We model both relationships:
# - Layers contains Shapes, Paths, Components (Paths and Components are concrete)
# - Paths and Components inherit from Shapes (see INHERITANCE)
COMPOSITION: Final[dict[str, list[str]]] = {
    "Glyphs.app": ["Fonts", "Styles"],
    "Fonts": ["Glyphs", "Masters", "Axes", "Features", "Classes"],
    "Styles": ["AxisValues"],
    "Glyphs": ["Layers"],
    "Layers": ["Shapes", "Paths", "Components", "Anchors", "Hints", "Guides"],
    "Masters": ["AxisValues"],
    "Paths": ["Nodes"],
}

# =============================================================================
# Reference Relationships (dashed lines in diagram, linked via ID)
# ID name -> [(source, target)]
# =============================================================================
REFERENCES: Final[dict[str, list[tuple[str, str]]]] = {
    "axisID": [("Axes", "AxisValues")],
    "masterID": [("Masters", "Layers")],
}

# =============================================================================
# Inheritance Relationships
# Parent -> [Children]
# =============================================================================
INHERITANCE: Final[dict[str, list[str]]] = {
    "Shapes": ["Paths", "Components"],
}

# =============================================================================
# Class-level References (classes that reference other classes via ID or property)
# Class -> [Referenced classes]
# =============================================================================
CLASS_REFERENCES: Final[dict[str, list[str]]] = {
    "Layers": ["Masters"],  # GSLayer references GSFontMaster via masterID
    "Components": ["Glyphs", "Layers"],  # GSComponent references GSGlyph and GSLayer
    "Masters": ["Axes"],  # GSFontMaster references GSAxis via axisID
    "AxisValues": ["Axes"],  # GSAxisValue references GSAxis via axisId
}

# =============================================================================
# Class Name Mapping (Display name -> Python class name)
# =============================================================================
CLASS_NAMES: Final[dict[str, str]] = {
    "Glyphs.app": "Glyphs",
    "Fonts": "GSFont",
    "Styles": "GSInstance",
    "Glyphs": "GSGlyph",
    "Layers": "GSLayer",
    "Masters": "GSFontMaster",
    "Axes": "GSAxis",
    "AxisValues": "GSAxisValue",
    "Features": "GSFeature",
    "Classes": "GSClass",
    "Shapes": "GSShape",
    "Paths": "GSPath",
    "Components": "GSComponent",
    "Nodes": "GSNode",
    "Anchors": "GSAnchor",
    "Hints": "GSHint",
    "Guides": "GSGuide",
}

# Reverse mapping (Python class name -> Display name)
PYTHON_TO_DISPLAY: Final[dict[str, str]] = {v: k for k, v in CLASS_NAMES.items()}


# =============================================================================
# Helper Functions
# =============================================================================


def get_python_class(display_name: str) -> str | None:
    """Get Python class name from display name.

    Args:
        display_name: Display name (e.g., "Fonts", "Layers")

    Returns:
        Python class name (e.g., "GSFont", "GSLayer") or None if not found
    """
    return CLASS_NAMES.get(display_name)


def get_display_name(python_class: str) -> str | None:
    """Get display name from Python class name.

    Args:
        python_class: Python class name (e.g., "GSFont", "GSLayer")

    Returns:
        Display name (e.g., "Fonts", "Layers") or None if not found
    """
    return PYTHON_TO_DISPLAY.get(python_class)


def get_children(display_name: str) -> list[str]:
    """Get children of a class (composition relationship).

    Args:
        display_name: Display name of the parent class

    Returns:
        List of child display names
    """
    return COMPOSITION.get(display_name, [])


def get_parent(display_name: str) -> str | None:
    """Get parent of a class (composition relationship).

    Args:
        display_name: Display name of the child class

    Returns:
        Display name of parent or None if not found
    """
    for parent, children in COMPOSITION.items():
        if display_name in children:
            return parent
    return None


def get_inheritance_parent(display_name: str) -> str | None:
    """Get inheritance parent of a class.

    Args:
        display_name: Display name of the child class

    Returns:
        Display name of inheritance parent or None if not found
    """
    for parent, children in INHERITANCE.items():
        if display_name in children:
            return parent
    return None


def get_inheritance_children(display_name: str) -> list[str]:
    """Get inheritance children of a class.

    Args:
        display_name: Display name of the parent class

    Returns:
        List of child display names
    """
    return INHERITANCE.get(display_name, [])


def build_structure_dict() -> dict:
    """Build a structure dictionary compatible with the old api_structure.json format.

    This provides backward compatibility for existing code that expects
    the old JSON structure.

    Returns:
        Dictionary with class hierarchy information
    """
    classes: dict[str, dict[str, str | list[str]]] = {}

    for display_name, python_class in CLASS_NAMES.items():
        class_info: dict[str, str | list[str]] = {
            "type": "singleton" if display_name == "Glyphs.app" else "class",
            "python_class": python_class,
            "display_name": display_name,
        }

        # Add contains (composition children)
        children = get_children(display_name)
        if children:
            class_info["contains"] = [CLASS_NAMES.get(c, c) for c in children]

        # Add contained_by (composition parent)
        parent = get_parent(display_name)
        if parent:
            class_info["contained_by"] = [CLASS_NAMES.get(parent, parent)]

        # Add inheritance parent
        inherit_parent = get_inheritance_parent(display_name)
        if inherit_parent:
            class_info["parent"] = CLASS_NAMES.get(inherit_parent, inherit_parent)

        # Add inheritance children
        inherit_children = get_inheritance_children(display_name)
        if inherit_children:
            class_info["children"] = [CLASS_NAMES.get(c, c) for c in inherit_children]

        # Add references (classes this class references)
        refs = CLASS_REFERENCES.get(display_name, [])
        if refs:
            class_info["references"] = [CLASS_NAMES.get(r, r) for r in refs]

        classes[python_class] = class_info

    return {
        "source": OFFICIAL_DIAGRAM_URL,
        "classes": classes,
    }
