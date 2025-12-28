"""
🔗 Glyphs ID Connection Guide

A smart guidance system for handling masterID and axisID connections,
providing precise ID connection usage guidance for AI code generation.
"""

# mypy: ignore-errors

import logging
from typing import Any

logger = logging.getLogger(__name__)


class IDConnectionGuide:
    """ID Connection Smart Guide"""

    def __init__(self):
        self.master_id_patterns = self._build_master_id_patterns()
        self.axis_id_patterns = self._build_axis_id_patterns()
        self.component_ref_patterns = self._build_component_ref_patterns()
        self.validation_templates = self._build_validation_templates()

    def _build_master_id_patterns(self) -> dict[str, Any]:
        """Build masterID related patterns"""
        return {
            "connection": {
                "from": "GSFontMaster",
                "to": "GSLayer",
                "property": "associatedMasterId",
                "description": "Each layer connects to a specific master via associatedMasterId",
            },
            "common_usage": [
                {
                    "scenario": "Iterate all layers of a glyph",
                    "pattern": """
for layer in glyph.layers:
    master = font.masters[layer.associatedMasterId]
    print(f"Processing layer in {master.name}")
""",
                    "safety_check": "Validate master existence",
                },
                {
                    "scenario": "Get layer for a specific master",
                    "pattern": """
def get_layer_for_master(glyph, target_master):
    for layer in glyph.layers:
        if layer.associatedMasterId == target_master.id:
            return layer
    return None
""",
                    "safety_check": "Handle possibly non-existent layer",
                },
                {
                    "scenario": "Synchronize layers with masters",
                    "pattern": """
# Ensure each master has a corresponding layer
master_ids = [master.id for master in font.masters]
for master_id in master_ids:
    layer_exists = any(layer.associatedMasterId == master_id
                      for layer in glyph.layers)
    if not layer_exists:
        new_layer = GSLayer()
        new_layer.associatedMasterId = master_id
        glyph.layers.append(new_layer)
""",
                    "safety_check": "Check for duplicate layers",
                },
            ],
            "common_errors": [
                {
                    "error": "KeyError: 'master_id_not_found'",
                    "cause": "Using a non-existent masterID",
                    "solution": "First verify masterID exists in font.masters",
                },
                {
                    "error": "IndexError: list index out of range",
                    "cause": "Assuming font.masters is a fixed-index list",
                    "solution": "Use ID instead of index to match masters",
                },
            ],
            "best_practices": [
                "Always validate masterID validity",
                "Use master.id instead of array index",
                "Handle cases where masterID doesn't exist",
                "Synchronize related layers after modifying masters",
            ],
        }

    def _build_axis_id_patterns(self) -> dict[str, Any]:
        """Build axisID related patterns"""
        return {
            "connection": {
                "from": "GSAxis",
                "to": "GSFontMaster.axesValues",
                "property": "axisId",
                "description": "Variation axis connects to master's axis values via axisId",
            },
            "common_usage": [
                {
                    "scenario": "Set master axis values",
                    "pattern": """
for axis in font.axes:
    for master in font.masters:
        # Set values based on master characteristics
        if axis.axisTag == 'wght':  # Weight axis
            if 'Bold' in master.name:
                master.axesValues[axis.axisId] = 700
            else:
                master.axesValues[axis.axisId] = 400
""",
                    "safety_check": "Ensure value is within axis range",
                },
                {
                    "scenario": "Validate axis setup completeness",
                    "pattern": """
def validate_axis_setup(font):
    issues = []
    for axis in font.axes:
        for master in font.masters:
            if axis.axisId not in master.axesValues:
                issues.append(f"Master '{master.name}' missing axis '{axis.name}'")
            else:
                value = master.axesValues[axis.axisId]
                if not (axis.minValue <= value <= axis.maxValue):
                    issues.append(f"Axis value {value} out of range for {axis.name}")
    return issues
""",
                    "safety_check": "Check value range",
                },
                {
                    "scenario": "Create new variation axis",
                    "pattern": """
# Create weight axis
weight_axis = GSAxis()
weight_axis.name = "Weight"
weight_axis.axisTag = "wght"
weight_axis.minValue = 100
weight_axis.maxValue = 900
font.axes.append(weight_axis)

# Set values for all masters
for master in font.masters:
    master.axesValues[weight_axis.axisId] = 400  # Default value
""",
                    "safety_check": "Ensure axis ID is unique",
                },
            ],
            "common_errors": [
                {
                    "error": "KeyError: 'axis_id_not_found'",
                    "cause": "Master still retains old axisId after axis is deleted",
                    "solution": "Clean up invalid axis values",
                },
                {
                    "error": "ValueError: axis value out of range",
                    "cause": "Setting a value outside the axis range",
                    "solution": "Validate value is between minValue and maxValue",
                },
            ],
            "best_practices": [
                "Each master must have a value for each axis",
                "Axis values must be within the defined range",
                "Clean up related axis values when deleting an axis",
                "Use standard axis tags (wght, wdth, slnt, etc.)",
            ],
        }

    def _build_component_ref_patterns(self) -> dict[str, Any]:
        """Build component reference patterns"""
        return {
            "connection": {
                "from": "GSComponent",
                "to": "GSGlyph",
                "property": "componentName",
                "description": "Components reference other glyphs via componentName",
            },
            "common_usage": [
                {
                    "scenario": "Validate component reference",
                    "pattern": """
def validate_component(font, component):
    referenced_glyph = font.glyphs[component.componentName]
    if not referenced_glyph:
        return f"Referenced glyph '{component.componentName}' not found"
    return "Valid"
""",
                    "safety_check": "Check if referenced glyph exists",
                },
                {
                    "scenario": "Handle component transform",
                    "pattern": """
for shape in layer.shapes:
    if shape.__class__.__name__ == 'GSComponent':
        # Handle component transform
        transform = shape.transform
        scale_x, scale_y = transform[0], transform[3]
        offset_x, offset_y = transform[4], transform[5]

        print(f"Component {shape.componentName}: scale({scale_x}, {scale_y}) offset({offset_x}, {offset_y})")
""",
                    "safety_check": "Validate transform matrix format",
                },
                {
                    "scenario": "Detect circular dependencies",
                    "pattern": """
def find_component_cycles(font):
    dependencies = {}
    for glyph in font.glyphs:
        deps = set()
        for layer in glyph.layers:
            for shape in layer.shapes:
                if shape.__class__.__name__ == 'GSComponent':
                    deps.add(shape.componentName)
        if deps:
            dependencies[glyph.name] = deps

    # Use depth-first search to detect cycles
    # ... (cycle detection logic)
    return cycles
""",
                    "safety_check": "Avoid infinite recursion",
                },
            ],
            "common_errors": [
                {
                    "error": "KeyError: 'component_name_not_found'",
                    "cause": "Referencing a non-existent glyph",
                    "solution": "Verify the glyph for componentName exists",
                },
                {
                    "error": "RecursionError: maximum recursion depth exceeded",
                    "cause": "Circular component reference",
                    "solution": "Detect and avoid circular dependencies",
                },
            ],
            "best_practices": [
                "Verify target glyph exists before component reference",
                "Regularly check for circular dependencies",
                "Use transform matrix appropriately",
                "Avoid overly deep component nesting",
            ],
        }

    def _build_validation_templates(self) -> dict[str, str]:
        """Build validation templates"""
        return {
            "master_id_validation": """
def validate_master_id(font, layer):
    '''Validate the masterID validity of a layer'''
    for master in font.masters:
        if master.id == layer.associatedMasterId:
            return master
    return None

# Usage example
master = validate_master_id(font, layer)
if master:
    print(f"Valid master: {master.name}")
else:
    print(f"Invalid master ID: {layer.associatedMasterId}")
""",
            "axis_id_validation": """
def validate_axis_values(font):
    '''Validate the completeness of all axis values'''
    issues = []

    for axis in font.axes:
        for master in font.masters:
            if axis.axisId not in master.axesValues:
                issues.append({
                    'type': 'missing_value',
                    'axis': axis.name,
                    'master': master.name
                })
            else:
                value = master.axesValues[axis.axisId]
                if not (axis.minValue <= value <= axis.maxValue):
                    issues.append({
                        'type': 'out_of_range',
                        'axis': axis.name,
                        'master': master.name,
                        'value': value,
                        'range': [axis.minValue, axis.maxValue]
                    })

    return issues
""",
            "component_validation": """
def validate_all_components(font):
    '''Validate the validity of all component references'''
    issues = []

    for glyph in font.glyphs:
        for layer in glyph.layers:
            if layer.shapes:
                for shape in layer.shapes:
                    if shape.__class__.__name__ == 'GSComponent':
                        referenced = font.glyphs[shape.componentName]
                        if not referenced:
                            issues.append({
                                'glyph': glyph.name,
                                'component': shape.componentName,
                                'issue': 'referenced_glyph_missing'
                            })

    return issues
""",
        }

    def get_id_connection_guide(
        self, connection_type: str, scenario: str = "general"
    ) -> dict[str, Any]:
        """
        Get ID connection usage guidance

        Args:
            connection_type: Connection type ('masterID', 'axisID', 'componentName')
            scenario: Usage scenario ('general', 'validation', 'creation', 'sync')

        Returns:
            Dictionary containing guidance information
        """
        patterns_map = {
            "masterID": self.master_id_patterns,
            "axisID": self.axis_id_patterns,
            "componentName": self.component_ref_patterns,
        }

        if connection_type not in patterns_map:
            return {"error": f"Unknown connection type: {connection_type}"}

        patterns = patterns_map[connection_type]

        guide = {
            "connection_info": patterns["connection"],
            "common_usage": patterns["common_usage"],
            "common_errors": patterns["common_errors"],
            "best_practices": patterns["best_practices"],
        }

        # Filter examples based on scenario
        if scenario != "general":
            filtered_usage = [
                usage
                for usage in patterns["common_usage"]
                if scenario.lower() in usage["scenario"].lower()
            ]
            if filtered_usage:
                guide["common_usage"] = filtered_usage

        return guide

    def generate_validation_code(self, connection_type: str) -> str:
        """
        Generate validation code

        Args:
            connection_type: Connection type

        Returns:
            Validation code string
        """
        validation_key = f"{connection_type.lower()}_validation"
        return self.validation_templates.get(
            validation_key, "# No validation template available"
        )

    def analyze_api_for_connections(self, api_name: str, api_content: str) -> list[str]:
        """
        Analyze ID connections involved in API content

        Args:
            api_name: API name
            api_content: API content text

        Returns:
            List of related ID connection suggestions
        """
        suggestions = []

        # Detect masterID related
        if any(
            keyword in api_content.lower()
            for keyword in ["associatedmasterid", "master", "layer", "gslayer"]
        ):
            suggestions.append(
                {
                    "type": "masterID",
                    "message": "🔗 This API involves masterID connection",
                    "guidance": "Verify layer.associatedMasterId corresponds to an existing master",
                    "pattern": "master = font.masters[layer.associatedMasterId]",
                }
            )

        # Detect axisID related
        if any(
            keyword in api_content.lower()
            for keyword in ["axis", "axesvalues", "variation", "interpolat"]
        ):
            suggestions.append(
                {
                    "type": "axisID",
                    "message": "🔗 This API involves axisID connection",
                    "guidance": "Ensure all masters have corresponding axis value settings",
                    "pattern": "master.axesValues[axis.axisId] = value",
                }
            )

        # Detect component related
        if any(
            keyword in api_content.lower()
            for keyword in ["component", "componentname", "gscomponent"]
        ):
            suggestions.append(
                {
                    "type": "componentName",
                    "message": "🔗 This API involves component reference",
                    "guidance": "Verify componentName corresponds to an existing glyph before use",
                    "pattern": "referenced_glyph = font.glyphs[component.componentName]",
                }
            )

        return suggestions

    def get_smart_suggestions(
        self, class_name: str, member_name: str | None = None
    ) -> list[dict]:
        """
        Provide smart suggestions based on class and member name

        Args:
            class_name: Class name
            member_name: Member name (optional)

        Returns:
            Smart suggestions list
        """
        suggestions = []

        # GSLayer related suggestions
        if class_name == "GSLayer":
            suggestions.append(
                {
                    "category": "ID Connection",
                    "message": "🔗 GSLayer connects to GSFontMaster via associatedMasterId",
                    "code_template": """
# Safe master access pattern
for layer in glyph.layers:
    master = None
    for m in font.masters:
        if m.id == layer.associatedMasterId:
            master = m
            break

    if master:
        print(f"Processing layer in {master.name}")
    else:
        print(f"⚠️  Invalid master ID: {layer.associatedMasterId}")
""",
                    "importance": "high",
                }
            )

        # GSFontMaster related suggestions
        if class_name == "GSFontMaster":
            suggestions.append(
                {
                    "category": "ID Connection",
                    "message": "🔗 GSFontMaster connects to variation axes via axesValues",
                    "code_template": """
# Set master axis values
for axis in font.axes:
    if axis.axisId not in master.axesValues:
        # Set default value
        default_value = (axis.minValue + axis.maxValue) / 2
        master.axesValues[axis.axisId] = default_value
        print(f"Set {axis.name} default value: {default_value}")
""",
                    "importance": "high",
                }
            )

        # GSComponent related suggestions
        if class_name == "GSComponent":
            suggestions.append(
                {
                    "category": "Reference Validation",
                    "message": "🔗 GSComponent references other glyphs via componentName",
                    "code_template": """
# Validate component reference
if shape.__class__.__name__ == 'GSComponent':
    referenced_glyph = font.glyphs[shape.componentName]
    if referenced_glyph:
        # Safely process component
        transform = shape.transform
        print(f"Component {shape.componentName} transform: {transform}")
    else:
        print(f"⚠️  Referenced glyph does not exist: {shape.componentName}")
""",
                    "importance": "high",
                }
            )

        # Specific member suggestions
        if member_name:
            if member_name == "associatedMasterId":
                suggestions.append(
                    {
                        "category": "Property Usage",
                        "message": "⚠️  Must verify corresponding master exists when using associatedMasterId",
                        "code_template": """
# Correct usage of associatedMasterId
master_found = False
for master in font.masters:
    if master.id == layer.associatedMasterId:
        master_found = True
        # Perform operations with master
        break

if not master_found:
    print("Error: Could not find corresponding master")
""",
                        "importance": "critical",
                    }
                )

            elif member_name == "axesValues":
                suggestions.append(
                    {
                        "category": "Property Usage",
                        "message": "⚠️  Ensure values are within axis range when modifying axesValues",
                        "code_template": """
# Safely set axis values
for axis in font.axes:
    value = proposed_value  # The value you want to set
    if axis.minValue <= value <= axis.maxValue:
        master.axesValues[axis.axisId] = value
    else:
        print(f"Value {value} outside axis {axis.name} range [{axis.minValue}, {axis.maxValue}]")
""",
                        "importance": "critical",
                    }
                )

        return suggestions


# Global instance
id_connection_guide = IDConnectionGuide()


def get_id_connection_guidance(
    connection_type: str, scenario: str = "general"
) -> dict[str, Any]:
    """Convenience function to get ID connection guidance"""
    return id_connection_guide.get_id_connection_guide(connection_type, scenario)


def get_smart_connection_suggestions(
    class_name: str, member_name: str | None = None
) -> list[dict]:
    """Convenience function to get smart connection suggestions"""
    return id_connection_guide.get_smart_suggestions(class_name, member_name)


def analyze_api_connections(api_name: str, api_content: str) -> list[str]:
    """Convenience function to analyze API connections"""
    return id_connection_guide.analyze_api_for_connections(api_name, api_content)
