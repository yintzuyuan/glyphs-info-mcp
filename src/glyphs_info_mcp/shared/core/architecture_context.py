"""
🏗️ Glyphs Architecture Context Enhancer

Injects architecture-related context information into API query results,
helping AI better understand the API's position and relationships within the overall architecture.
"""

# mypy: ignore-errors

import logging
import re

logger = logging.getLogger(__name__)

# Try to import the ID connection guide
try:
    from .id_connection_guide import (
        analyze_api_connections,
        get_smart_connection_suggestions,
    )

    ID_GUIDE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ID connection guide not available: {e}")
    ID_GUIDE_AVAILABLE = False


class ArchitectureContextEnhancer:
    """Architecture context enhancer"""

    def __init__(self):
        self.architecture_map = self._build_architecture_map()
        self.id_connections = self._build_id_connections()
        self.common_patterns = self._build_common_patterns()
        self.safety_checks = self._build_safety_checks()

    def _build_architecture_map(self) -> dict[str, dict]:
        """Build the architecture mapping table"""
        return {
            # Level 1: Application
            "Glyphs": {
                "level": 1,
                "category": "Application",
                "description": "Application root object",
                "children": ["GSFont"],
                "properties": ["font", "fonts", "currentDocument"],
                "common_operations": ["Access current font", "Manage multiple fonts"],
            },
            # Level 2: Font
            "GSFont": {
                "level": 2,
                "category": "Font",
                "description": "Font object containing all glyphs and settings",
                "children": [
                    "GSGlyph",
                    "GSFontMaster",
                    "GSAxis",
                    "GSFeature",
                    "GSClass",
                ],
                "properties": ["glyphs", "masters", "axes", "features", "classes"],
                "id_connections": [
                    "masterID connects to GSLayer",
                    "axisID connects to AxisValues",
                ],
                "common_operations": ["Iterate glyphs", "Manage masters", "Configure axes"],
            },
            # Level 3: Glyph
            "GSGlyph": {
                "level": 3,
                "category": "Glyph",
                "description": "Single glyph containing multiple layers (one per master)",
                "parent": "GSFont",
                "children": ["GSLayer"],
                "properties": [
                    "layers",
                    "name",
                    "unicode",
                    "leftMetricsKey",
                    "rightMetricsKey",
                ],
                "id_connections": ["Each layer connects to its master via masterID"],
                "common_operations": ["Iterate layers", "Set spacing", "Manage Unicode values"],
            },
            # Master
            "GSFontMaster": {
                "level": 3,
                "category": "Master",
                "description": "Design master defining a design variant of the font",
                "parent": "GSFont",
                "children": ["GSLayer"],
                "properties": [
                    "id",
                    "name",
                    "weight",
                    "width",
                    "isItalic",
                    "axesValues",
                ],
                "id_connections": [
                    "Connects to GSLayer via masterID",
                    "Connects to axis values via axisID",
                ],
                "common_operations": ["Set weight values", "Manage axis values", "Define design parameters"],
            },
            # Axis
            "GSAxis": {
                "level": 3,
                "category": "Axis",
                "description": "Variation axis defining the font's variation range",
                "parent": "GSFont",
                "children": ["AxisValues"],
                "properties": ["axisId", "name", "axisTag", "minValue", "maxValue"],
                "id_connections": ["Connects to master.axesValues via axisID"],
                "common_operations": ["Set variation range", "Assign axis values to masters"],
            },
            # Level 4: Layer
            "GSLayer": {
                "level": 4,
                "category": "Layer",
                "description": "Glyph layer for a specific master containing actual shapes",
                "parent": "GSGlyph",
                "children": ["GSPath", "GSComponent", "GSAnchor", "GSGuide", "GSHint"],
                "properties": [
                    "shapes",
                    "anchors",
                    "guides",
                    "hints",
                    "width",
                    "associatedMasterId",
                ],
                "id_connections": ["Connects to GSFontMaster via associatedMasterId"],
                "common_operations": ["Process shapes", "Manage anchors", "Set layer width"],
            },
            # Level 5: Shapes
            "GSPath": {
                "level": 5,
                "category": "Shape",
                "description": "Path shape composed of nodes forming curves",
                "parent": "GSLayer",
                "children": ["GSNode"],
                "properties": ["nodes", "closed", "direction"],
                "common_operations": ["Edit nodes", "Calculate bounds", "Transform path"],
            },
            "GSComponent": {
                "level": 5,
                "category": "Shape",
                "description": "Component referencing shapes from other glyphs",
                "parent": "GSLayer",
                "children": [],
                "properties": ["componentName", "transform"],
                "id_connections": ["References other GSGlyph via componentName"],
                "common_operations": ["Set transformation matrix", "Validate reference validity"],
            },
            "GSAnchor": {
                "level": 5,
                "category": "Guide",
                "description": "Anchor for glyph positioning and alignment",
                "parent": "GSLayer",
                "properties": ["name", "position"],
                "common_operations": ["Set position", "Manage anchor names"],
            },
            # Level 6: Nodes
            "GSNode": {
                "level": 6,
                "category": "Node",
                "description": "Path node defining curve control points",
                "parent": "GSPath",
                "properties": ["position", "type", "smooth"],
                "common_operations": ["Move position", "Set node type", "Adjust smoothness"],
            },
        }

    def _build_id_connections(self) -> dict[str, list[dict]]:
        """Build ID connection relationships"""
        return {
            "masterID": [
                {
                    "from": "GSFontMaster",
                    "to": "GSLayer",
                    "property": "associatedMasterId",
                    "description": "Each layer must be associated with a master",
                    "validation": "Ensure layer.associatedMasterId exists in font.masters",
                    "common_error": "Using non-existent masterID causes program errors",
                }
            ],
            "axisID": [
                {
                    "from": "GSAxis",
                    "to": "GSFontMaster.axesValues",
                    "property": "axisId",
                    "description": "Each master must specify values for each axis",
                    "validation": "Ensure all axis IDs have corresponding values in all masters",
                    "common_error": "Missing axis values affects variable font generation",
                }
            ],
            "componentName": [
                {
                    "from": "GSComponent",
                    "to": "GSGlyph",
                    "property": "componentName",
                    "description": "Component references other glyphs by name",
                    "validation": "Ensure componentName corresponds to an existing glyph in the font",
                    "common_error": "Referencing non-existent glyphs causes rendering issues",
                }
            ],
        }

    def _build_common_patterns(self) -> dict[str, dict]:
        """Build common programming patterns"""
        return {
            "safe_layer_iteration": {
                "description": "Safe layer iteration pattern",
                "template": """
for layer in glyph.layers:
    master = font.masters[layer.associatedMasterId]
    if master:
        # Process layer logic
        process_layer(layer, master)
""",
                "applies_to": ["GSGlyph", "GSLayer", "GSFontMaster"],
            },
            "safe_shape_processing": {
                "description": "Safe shape processing pattern",
                "template": """
if layer.shapes:
    for shape in layer.shapes:
        if shape.__class__.__name__ == 'GSPath':
            # Process path
            process_path(shape)
        elif shape.__class__.__name__ == 'GSComponent':
            # Process component
            process_component(shape)
""",
                "applies_to": ["GSLayer", "GSPath", "GSComponent"],
            },
            "component_validation": {
                "description": "Component reference validation pattern",
                "template": """
referenced_glyph = font.glyphs[component.componentName]
if referenced_glyph:
    # Safely process component
    process_component(component, referenced_glyph)
else:
    print(f"⚠️  Referenced glyph '{component.componentName}' not found")
""",
                "applies_to": ["GSComponent", "GSGlyph"],
            },
            "axis_value_management": {
                "description": "Axis value management pattern",
                "template": """
for axis in font.axes:
    for master in font.masters:
        if axis.axisId in master.axesValues:
            value = master.axesValues[axis.axisId]
            # Process axis value
            process_axis_value(axis, master, value)
        else:
            print(f"⚠️  Master '{master.name}' missing value for axis '{axis.name}'")
""",
                "applies_to": ["GSAxis", "GSFontMaster"],
            },
        }

    def _build_safety_checks(self) -> dict[str, dict]:
        """Build safety check recommendations"""
        return {
            "GSLayer": {
                "before_shape_access": "Ensure layer.shapes exists and is not empty",
                "before_anchor_access": "Ensure layer.anchors exists",
                "master_id_validation": "Validate that layer.associatedMasterId corresponds to an existing master",
            },
            "GSPath": {
                "before_node_access": "Ensure path.nodes exists and is not empty",
                "bounds_calculation": "Check that path has valid nodes before calculating bounds",
            },
            "GSComponent": {
                "before_reference": "Validate that componentName corresponds to an existing glyph",
                "transform_validation": "Ensure transformation matrix format is correct",
            },
            "GSFontMaster": {
                "axis_value_check": "Ensure all axes have corresponding values",
                "id_uniqueness": "Ensure master.id is unique within the font",
            },
        }

    def enhance_api_response(
        self, api_name: str, original_response: str, search_context: dict | None = None
    ) -> str:
        """
        Add architecture context to API response

        Args:
            api_name: API name (e.g., "GSFont", "GSGlyph")
            original_response: Original response content
            search_context: Search context information

        Returns:
            Enhanced response content
        """
        # Identify related architecture elements
        related_classes = self._identify_related_classes(api_name)

        # Build architecture context
        context_info = self._build_context_info(api_name, related_classes)

        # Add programming pattern suggestions
        pattern_suggestions = self._get_pattern_suggestions(api_name)

        # Add safety check reminders
        safety_reminders = self._get_safety_reminders(api_name)

        # 🔗 Add ID connection guidance
        id_guidance = []
        if ID_GUIDE_AVAILABLE:
            try:
                # Analyze connections in API content
                connection_analysis = analyze_api_connections(
                    api_name, original_response
                )
                if connection_analysis:
                    id_guidance.extend(connection_analysis)

                # Provide smart suggestions based on class and member
                class_match = re.search(r"(GS\w+)", api_name)
                if class_match:
                    class_name = class_match.group(1)
                    member_match = re.search(r"\.(\w+)", api_name)
                    member_name = member_match.group(1) if member_match else None

                    smart_suggestions = get_smart_connection_suggestions(
                        class_name, member_name
                    )
                    id_guidance.extend(smart_suggestions)

            except Exception as e:
                logger.warning(f"Failed to get ID guidance: {e}")

        # Compose enhanced response
        enhanced_response = self._compose_enhanced_response(
            original_response,
            context_info,
            pattern_suggestions,
            safety_reminders,
            id_guidance,
        )

        return enhanced_response

    def _identify_related_classes(self, api_name: str) -> list[str]:
        """Identify related architecture classes"""
        related = set()

        # Direct match
        if api_name in self.architecture_map:
            arch_info = self.architecture_map[api_name]
            related.update(arch_info.get("children", []))
            if "parent" in arch_info:
                related.add(arch_info["parent"])

        # Fuzzy match (handles properties like GSFont.glyphs)
        for class_name in self.architecture_map:
            if api_name.startswith(class_name) or class_name in api_name:
                related.add(class_name)

        return list(related)

    def _build_context_info(self, api_name: str, related_classes: list[str]) -> dict:
        """Build architecture context information"""
        context = {
            "architecture_position": None,
            "related_objects": [],
            "id_connections": [],
            "hierarchy_level": None,
        }

        # Find the main class
        main_class = None
        for class_name in [api_name] + related_classes:
            if class_name in self.architecture_map:
                main_class = class_name
                break

        if main_class:
            arch_info = self.architecture_map[main_class]

            context["architecture_position"] = {
                "class": main_class,
                "level": arch_info["level"],
                "category": arch_info["category"],
                "description": arch_info["description"],
            }

            context["hierarchy_level"] = arch_info["level"]

            # Related objects
            if "children" in arch_info:
                context["related_objects"].extend(
                    [
                        {"relation": "child", "class": child}
                        for child in arch_info["children"]
                    ]
                )

            if "parent" in arch_info:
                context["related_objects"].append(
                    {"relation": "parent", "class": arch_info["parent"]}
                )

            # ID connection information
            if "id_connections" in arch_info:
                context["id_connections"] = arch_info["id_connections"]

        return context

    def _get_pattern_suggestions(self, api_name: str) -> list[dict]:
        """Get applicable programming pattern suggestions"""
        suggestions = []

        for pattern_name, pattern_info in self.common_patterns.items():
            if any(
                api_name.startswith(cls) or cls in api_name
                for cls in pattern_info.get("applies_to", [])
            ):
                suggestions.append(
                    {
                        "name": pattern_name,
                        "description": pattern_info["description"],
                        "template": pattern_info["template"],
                    }
                )

        return suggestions

    def _get_safety_reminders(self, api_name: str) -> list[str]:
        """Get safety check reminders"""
        reminders = []

        for class_name, safety_info in self.safety_checks.items():
            if api_name.startswith(class_name) or class_name in api_name:
                for check_name, check_desc in safety_info.items():
                    reminders.append(f"🛡️ {check_desc}")

        return reminders

    def _compose_enhanced_response(
        self,
        original: str,
        context: dict,
        patterns: list[dict],
        safety: list[str],
        id_guidance: list[dict] = None,
    ) -> str:
        """Compose enhanced response"""
        sections = [original]

        # Architecture position information
        if context.get("architecture_position"):
            pos = context["architecture_position"]
            sections.append(
                f"""

## 🏗️ Architecture Position

**Class**: {pos['class']} (Level {pos['level']} - {pos['category']})
**Description**: {pos['description']}"""
            )

        # Related objects
        if context.get("related_objects"):
            sections.append("\n## 🔗 Architecture Relationships")
            for rel in context["related_objects"]:
                relation_icon = "⬆️" if rel["relation"] == "parent" else "⬇️"
                sections.append(
                    f"- {relation_icon} **{rel['relation'].title()}**: `{rel['class']}`"
                )

        # ID connection information
        if context.get("id_connections"):
            sections.append("\n## 🔑 Important Connections")
            for connection in context["id_connections"]:
                sections.append(f"- 🔗 {connection}")

        # Programming patterns
        if patterns:
            sections.append("\n## 💡 Recommended Programming Patterns")
            for pattern in patterns[:2]:  # Limit display count
                sections.append(
                    f"""
### {pattern['description']}
```python{pattern['template']}
```"""
                )

        # Safety reminders
        if safety:
            sections.append("\n## ⚠️ Safety Check Reminders")
            for reminder in safety[:3]:  # Limit display count
                sections.append(f"- {reminder}")

        # 🔗 ID connection guidance
        if id_guidance:
            sections.append("\n## 🔗 ID Connection & Related Object Guidance")

            # Categorize ID guidance display
            connection_msgs = [
                g
                for g in id_guidance
                if isinstance(g, dict)
                and g.get("type") in ["masterID", "axisID", "componentName"]
            ]
            smart_suggestions = [
                g for g in id_guidance if isinstance(g, dict) and g.get("category")
            ]

            if connection_msgs:
                sections.append("\n### 🔑 ID Connection Reminders")
                for msg in connection_msgs[:2]:  # Limit display count
                    sections.append(f"- {msg.get('message', '')}")
                    if msg.get("pattern"):
                        sections.append(f"  ```python\n  {msg['pattern']}\n  ```")

            if smart_suggestions:
                sections.append("\n### 💡 Smart Programming Suggestions")
                for suggestion in smart_suggestions[:2]:  # Limit display count
                    if suggestion.get("importance") == "critical":
                        icon = "🚨"
                    elif suggestion.get("importance") == "high":
                        icon = "⚠️"
                    else:
                        icon = "💡"

                    sections.append(
                        f"- {icon} **{suggestion.get('category', 'General')}**: {suggestion.get('message', '')}"
                    )
                    if suggestion.get("code_template"):
                        sections.append(
                            f"  ```python{suggestion['code_template']}\n  ```"
                        )

        # Architecture best practices
        sections.append(
            """

## 🎯 Architecture Best Practices

1. **Follow hierarchy structure**: Access in order Font → Glyph → Layer → Shape → Path → Node
2. **Validate ID connections**: Confirm corresponding objects exist before using masterID or axisID
3. **Defensive programming**: Check existence at each level before accessing nested objects
4. **Type checking**: Distinguish between GSPath and GSComponent, use appropriate processing methods

📖 **Complete architecture reference**: See `docs/GLYPHS_ARCHITECTURE.md`
🔗 **ID connection patterns**: See `src/shared/core/glyphs_patterns.py`"""
        )

        return "".join(sections)

    def get_architecture_hints(self, class_names: list[str]) -> list[str]:
        """Get architecture hints"""
        hints = []

        for class_name in class_names:
            if class_name in self.architecture_map:
                arch_info = self.architecture_map[class_name]

                # Position hint
                hints.append(
                    f"🏗️ {class_name} is at architecture level {arch_info['level']} "
                    f"({arch_info['category']})"
                )

                # Common operations hint
                if "common_operations" in arch_info:
                    ops = ", ".join(arch_info["common_operations"])
                    hints.append(f"🔧 Common operations: {ops}")

                # ID connection hints
                if "id_connections" in arch_info:
                    for conn in arch_info["id_connections"]:
                        hints.append(f"🔗 {conn}")

        return hints


# Global instance
architecture_enhancer = ArchitectureContextEnhancer()


def enhance_api_response(
    api_name: str, original_response: str, search_context: dict | None = None
) -> str:
    """Convenience function to quickly enhance API response"""
    return architecture_enhancer.enhance_api_response(
        api_name, original_response, search_context
    )


def get_architecture_hints(class_names: list[str]) -> list[str]:
    """Convenience function to quickly get architecture hints"""
    return architecture_enhancer.get_architecture_hints(class_names)
