"""
🏗️ Glyphs.app Architecture-Aware Programming Patterns Library

This module contains standard programming patterns based on the Glyphs.app object model,
providing AI with safe, efficient, and best-practice compliant Glyphs code.

All patterns strictly follow the official architecture:
Font → Glyphs → Layers → Shapes → Paths → Nodes
      └─ Masters ─masterID─→ Layers
      └─ Axes ─axisID─→ AxisValues
"""

# mypy: ignore-errors
# This file is the Glyphs.app architecture pattern library, containing dynamic type Glyphs API calls
# Temporarily ignore type checking to maintain pattern code readability and flexibility

import logging
from collections.abc import Callable

logger = logging.getLogger(__name__)


class ArchitectureAwarePatterns:
    """Architecture-aware programming pattern collection"""

    # =============================================================================
    # Pattern 1: Safe Object Hierarchy Traversal
    # =============================================================================

    @staticmethod
    def safe_glyph_iterator(
        font, processor_func: Callable, error_handler: Callable | None = None
    ):
        """
        Safe glyph iterator

        Args:
            font: GSFont object
            processor_func: Processing function, receives (glyph, layer, master) parameters
            error_handler: Error handling function, optional

        Returns:
            List[Any]: List of processing results
        """
        if not font or not font.glyphs:
            return []

        results = []
        for glyph in font.glyphs:
            try:
                glyph_results = ArchitectureAwarePatterns._process_glyph_layers(
                    font, glyph, processor_func
                )
                results.extend(glyph_results)
            except Exception as e:
                if error_handler:
                    error_result = error_handler(glyph, e)
                    results.append(error_result)
                else:
                    logger.error(f"Error processing glyph {glyph.name}: {e}")
                    results.append(None)

        return [r for r in results if r is not None]

    @staticmethod
    def _process_glyph_layers(font, glyph, processor_func):
        """Process all layers of a glyph"""
        if not glyph.layers:
            return []

        layer_results = []
        for layer in glyph.layers:
            # Validate masterID connection
            master = ArchitectureAwarePatterns.get_master_for_layer(font, layer)
            if master:
                result = processor_func(glyph, layer, master)
                layer_results.append(result)
            else:
                logger.warning(
                    f"Invalid master ID {layer.associatedMasterId} for glyph {glyph.name}"
                )

        return layer_results

    # =============================================================================
    # Pattern 2: masterID Connection Validation and Management
    # =============================================================================

    @staticmethod
    def get_master_for_layer(font, layer):
        """
        Safely get the master corresponding to a layer

        Args:
            font: GSFont object
            layer: GSLayer object

        Returns:
            GSFontMaster: Corresponding master, or None if not found
        """
        try:
            for master in font.masters:
                if master.id == layer.associatedMasterId:
                    return master
        except (AttributeError, TypeError):
            pass

        return None

    @staticmethod
    def get_layer_for_master(glyph, master):
        """
        Get the layer of a glyph in a specific master

        Args:
            glyph: GSGlyph object
            master: GSFontMaster object

        Returns:
            GSLayer: Corresponding layer, or None if not found
        """
        if not glyph.layers:
            return None

        for layer in glyph.layers:
            if layer.associatedMasterId == master.id:
                return layer

        return None

    @staticmethod
    def sync_layers_with_masters(font, glyph):
        """
        Synchronize glyph layers with font masters

        Args:
            font: GSFont object
            glyph: GSGlyph object

        Returns:
            Dict: Synchronization result statistics
        """
        if not font.masters:
            return {"error": "No masters in font"}

        master_ids = [master.id for master in font.masters]
        existing_master_ids = [layer.associatedMasterId for layer in glyph.layers]

        # Remove invalid layers
        valid_layers = []
        removed_count = 0

        for layer in glyph.layers:
            if layer.associatedMasterId in master_ids:
                valid_layers.append(layer)
            else:
                removed_count += 1

        glyph.layers = valid_layers

        # Add missing layers
        current_master_ids = [layer.associatedMasterId for layer in valid_layers]
        missing_master_ids = set(master_ids) - set(current_master_ids)

        added_count = 0
        for master_id in missing_master_ids:
            try:
                from glyphs import GSLayer  # Dynamic import to avoid dependency issues

                new_layer = GSLayer()
                new_layer.associatedMasterId = master_id
                glyph.layers.append(new_layer)
                added_count += 1
            except ImportError:
                logger.error("GSLayer class not available")
                break

        return {
            "removed_invalid_layers": removed_count,
            "added_missing_layers": added_count,
            "total_layers": len(glyph.layers),
        }

    # =============================================================================
    # Pattern 3: Safe Shape Processing
    # =============================================================================

    @staticmethod
    def safe_shape_processor(
        layer,
        path_processor: Callable | None = None,
        component_processor: Callable | None = None,
    ):
        """
        Safe shape processor, distinguishes between paths and components

        Args:
            layer: GSLayer object
            path_processor: Path processing function, receives GSPath parameter
            component_processor: Component processing function, receives GSComponent parameter

        Returns:
            Dict: Processing result
        """
        if not layer.shapes:
            return {"paths": [], "components": [], "total": 0}

        path_results = []
        component_results = []

        for shape in layer.shapes:
            try:
                shape_class = shape.__class__.__name__

                if shape_class == "GSPath" and path_processor:
                    result = path_processor(shape)
                    path_results.append(result)

                elif shape_class == "GSComponent" and component_processor:
                    result = component_processor(shape)
                    component_results.append(result)

            except Exception as e:
                logger.error(f"Error processing shape: {e}")

        return {
            "paths": path_results,
            "components": component_results,
            "total": len(path_results) + len(component_results),
        }

    @staticmethod
    def analyze_path_structure(path):
        """
        Standard pattern for analyzing path structure

        Args:
            path: GSPath object

        Returns:
            Dict: Path analysis result
        """
        if not path.nodes:
            return {
                "node_count": 0,
                "is_closed": path.closed if hasattr(path, "closed") else None,
                "node_types": {},
                "bounds": None,
            }

        # Count node types
        node_types = {}
        for node in path.nodes:
            node_type = getattr(node, "type", "unknown")
            node_types[node_type] = node_types.get(node_type, 0) + 1

        # Calculate bounds
        bounds = None
        try:
            if hasattr(path, "bounds") and path.bounds:
                bounds = {
                    "x": path.bounds.origin.x,
                    "y": path.bounds.origin.y,
                    "width": path.bounds.size.width,
                    "height": path.bounds.size.height,
                }
        except (AttributeError, TypeError):
            pass

        return {
            "node_count": len(path.nodes),
            "is_closed": getattr(path, "closed", None),
            "node_types": node_types,
            "bounds": bounds,
        }

    @staticmethod
    def validate_component_reference(font, component):
        """
        Validate the validity of a component reference

        Args:
            font: GSFont object
            component: GSComponent object

        Returns:
            Dict: Validation result
        """
        component_name = getattr(component, "componentName", None)
        if not component_name:
            return {"valid": False, "error": "Component has no componentName"}

        # Check if the referenced glyph exists
        referenced_glyph = None
        try:
            referenced_glyph = font.glyphs[component_name]
        except (KeyError, TypeError):
            pass

        if not referenced_glyph:
            return {
                "valid": False,
                "error": f"Referenced glyph '{component_name}' not found",
            }

        # Check transform matrix
        transform_info = {}
        try:
            if hasattr(component, "transform"):
                transform = component.transform
                transform_info = {
                    "scale_x": transform[0],
                    "scale_y": transform[3],
                    "offset_x": transform[4],
                    "offset_y": transform[5],
                }
        except (AttributeError, IndexError, TypeError):
            transform_info = {"error": "Invalid transform"}

        return {
            "valid": True,
            "referenced_glyph": component_name,
            "transform": transform_info,
        }

    # =============================================================================
    # Pattern 4: Variation Axis (axisID) Management
    # =============================================================================

    @staticmethod
    def validate_axis_values(font):
        """
        Validate the consistency of variation axis values

        Args:
            font: GSFont object

        Returns:
            Dict: Validation result
        """
        if not font.axes:
            return {"valid": True, "message": "No variation axes defined"}

        issues = []

        for axis in font.axes:
            axis_issues = []

            # Check if each master has a value for this axis
            for master in font.masters:
                axis_values = getattr(master, "axesValues", {})

                if axis.axisId not in axis_values:
                    axis_issues.append(
                        f"Master '{master.name}' missing value for axis '{axis.name}'"
                    )
                else:
                    value = axis_values[axis.axisId]
                    if not (axis.minValue <= value <= axis.maxValue):
                        axis_issues.append(
                            f"Master '{master.name}' axis '{axis.name}' value {value} "
                            f"outside range [{axis.minValue}, {axis.maxValue}]"
                        )

            if axis_issues:
                issues.extend(axis_issues)

        return {"valid": len(issues) == 0, "issues": issues}

    @staticmethod
    def fix_axis_value_inconsistencies(font):
        """
        Fix variation axis value inconsistencies

        Args:
            font: GSFont object

        Returns:
            Dict: Fix result
        """
        if not font.axes:
            return {"message": "No axes to fix", "fixes": []}

        fixes = []

        for axis in font.axes:
            for master in font.masters:
                axis_values = getattr(master, "axesValues", {})

                if axis.axisId not in axis_values:
                    # Set default value
                    default_value = getattr(axis, "defaultValue", axis.minValue)
                    axis_values[axis.axisId] = default_value
                    fixes.append(
                        f"Set default value {default_value} for {master.name} on axis {axis.name}"
                    )

                else:
                    value = axis_values[axis.axisId]
                    if not (axis.minValue <= value <= axis.maxValue):
                        # Correct to within range
                        corrected_value = max(axis.minValue, min(axis.maxValue, value))
                        axis_values[axis.axisId] = corrected_value
                        fixes.append(
                            f"Corrected {master.name} axis {axis.name} from {value} to {corrected_value}"
                        )

        return {"fixes": fixes, "total_fixes": len(fixes)}

    # =============================================================================
    # Pattern 5: Component Dependency Management
    # =============================================================================

    @staticmethod
    def analyze_component_dependencies(font):
        """
        Analyze all component dependencies

        Args:
            font: GSFont object

        Returns:
            Dict: Dependency graph
        """
        dependencies = {}

        for glyph in font.glyphs:
            glyph_dependencies = set()

            for layer in glyph.layers:
                if layer.shapes:
                    for shape in layer.shapes:
                        if shape.__class__.__name__ == "GSComponent":
                            component_name = getattr(shape, "componentName", None)
                            if component_name:
                                glyph_dependencies.add(component_name)

            if glyph_dependencies:
                dependencies[glyph.name] = list(glyph_dependencies)

        return dependencies

    @staticmethod
    def find_circular_dependencies(font):
        """
        Detect circular component dependencies

        Args:
            font: GSFont object

        Returns:
            List[List[str]]: Detected circular dependency paths
        """
        dependencies = ArchitectureAwarePatterns.analyze_component_dependencies(font)

        # Use depth-first search to detect cycles
        WHITE, GRAY, BLACK = 0, 1, 2
        colors = dict.fromkeys(dependencies, WHITE)
        cycles = []

        def dfs(node, path):
            if node not in colors:
                return  # Node does not exist in dependency graph

            if colors[node] == GRAY:
                # Found a cycle
                try:
                    cycle_start = path.index(node)
                    cycle = path[cycle_start:] + [node]
                    cycles.append(cycle)
                except ValueError:
                    pass
                return

            if colors[node] == BLACK:
                return

            colors[node] = GRAY
            path.append(node)

            for neighbor in dependencies.get(node, []):
                dfs(neighbor, path)

            path.pop()
            colors[node] = BLACK

        for node in dependencies:
            if colors[node] == WHITE:
                dfs(node, [])

        return cycles

    # =============================================================================
    # Pattern 6: Geometry Calculation and Transformation
    # =============================================================================

    @staticmethod
    def calculate_layer_bounds(layer):
        """
        Calculate the precise bounds of a layer

        Args:
            layer: GSLayer object

        Returns:
            Optional[Dict]: Bounds information, or None if no shapes
        """
        if not layer.shapes:
            return None

        min_x = min_y = float("inf")
        max_x = max_y = float("-inf")

        for shape in layer.shapes:
            if shape.__class__.__name__ == "GSPath" and shape.nodes:
                for node in shape.nodes:
                    try:
                        x, y = node.position.x, node.position.y
                        min_x, min_y = min(min_x, x), min(min_y, y)
                        max_x, max_y = max(max_x, x), max(max_y, y)
                    except (AttributeError, TypeError):
                        continue

        if min_x == float("inf"):  # No valid coordinates found
            return None

        return {
            "x": min_x,
            "y": min_y,
            "width": max_x - min_x,
            "height": max_y - min_y,
            "center_x": (min_x + max_x) / 2,
            "center_y": (min_y + max_y) / 2,
        }

    @staticmethod
    def move_layer_shapes(layer, dx, dy):
        """
        Move all shapes in a layer

        Args:
            layer: GSLayer object
            dx: x-axis displacement
            dy: y-axis displacement

        Returns:
            Dict: Movement result statistics
        """
        if not layer.shapes:
            return {"moved_shapes": 0, "moved_anchors": 0}

        moved_shapes = 0

        for shape in layer.shapes:
            try:
                if shape.__class__.__name__ == "GSPath" and shape.nodes:
                    for node in shape.nodes:
                        try:
                            from Foundation import NSPoint

                            node.position = NSPoint(
                                node.position.x + dx, node.position.y + dy
                            )
                        except (ImportError, AttributeError):
                            # Fallback method, set coordinates directly
                            if hasattr(node.position, "x") and hasattr(
                                node.position, "y"
                            ):
                                node.position.x += dx
                                node.position.y += dy
                    moved_shapes += 1

                elif shape.__class__.__name__ == "GSComponent":
                    # Move component
                    if hasattr(shape, "transform"):
                        transform = list(shape.transform)
                        transform[4] += dx  # x displacement
                        transform[5] += dy  # y displacement
                        shape.transform = transform
                        moved_shapes += 1

            except Exception as e:
                logger.error(f"Error moving shape: {e}")

        # Move anchors
        moved_anchors = 0
        if layer.anchors:
            for anchor in layer.anchors:
                try:
                    from Foundation import NSPoint

                    anchor.position = NSPoint(
                        anchor.position.x + dx, anchor.position.y + dy
                    )
                    moved_anchors += 1
                except (ImportError, AttributeError):
                    if hasattr(anchor.position, "x") and hasattr(anchor.position, "y"):
                        anchor.position.x += dx
                        anchor.position.y += dy
                        moved_anchors += 1
                except Exception as e:
                    logger.error(f"Error moving anchor: {e}")

        return {"moved_shapes": moved_shapes, "moved_anchors": moved_anchors}


class GlyphsArchitectureValidator:
    """Glyphs Architecture Validator"""

    def __init__(self, font):
        self.font = font
        self.issues = []

    def validate_all(self):
        """Execute complete architecture validation"""
        self.issues = []

        # Validate master-layer connections
        self._validate_master_layer_links()

        # Validate variation axis setup
        self._validate_axis_setup()

        # Validate component references
        self._validate_component_references()

        # Check circular dependencies
        self._check_circular_dependencies()

        return {
            "valid": len(self.issues) == 0,
            "issues": self.issues,
            "total_issues": len(self.issues),
        }

    def _validate_master_layer_links(self):
        """Validate master-layer connections"""
        if not self.font.masters:
            self.issues.append("Font has no masters defined")
            return

        master_ids = {master.id for master in self.font.masters}

        for glyph in self.font.glyphs:
            for layer in glyph.layers:
                if layer.associatedMasterId not in master_ids:
                    self.issues.append(
                        f"Glyph '{glyph.name}' has layer with invalid master ID: {layer.associatedMasterId}"
                    )

    def _validate_axis_setup(self):
        """Validate variation axis setup"""
        axis_result = ArchitectureAwarePatterns.validate_axis_values(self.font)
        if not axis_result["valid"]:
            self.issues.extend(axis_result["issues"])

    def _validate_component_references(self):
        """Validate component references"""
        for glyph in self.font.glyphs:
            for layer in glyph.layers:
                if layer.shapes:
                    for shape in layer.shapes:
                        if shape.__class__.__name__ == "GSComponent":
                            validation = (
                                ArchitectureAwarePatterns.validate_component_reference(
                                    self.font, shape
                                )
                            )
                            if not validation["valid"]:
                                self.issues.append(
                                    f"Glyph '{glyph.name}': {validation['error']}"
                                )

    def _check_circular_dependencies(self):
        """Check circular dependencies"""
        cycles = ArchitectureAwarePatterns.find_circular_dependencies(self.font)
        for cycle in cycles:
            self.issues.append(f"Circular component dependency: {' -> '.join(cycle)}")


# =============================================================================
# Common Code Generation Templates
# =============================================================================


class GlyphsCodeTemplates:
    """Glyphs Code Generation Templates"""

    @staticmethod
    def generate_safe_glyph_processor_template():
        """Generate safe glyph processor template"""
        return '''
def process_glyphs_safely(font):
    """Template for safely processing all glyphs"""

    def process_single_glyph(glyph, layer, master):
        """Logic for processing a single glyph layer"""
        result = {
            'glyph_name': glyph.name,
            'master_name': master.name,
            'layer_width': layer.width,
            'shape_count': len(layer.shapes) if layer.shapes else 0
        }

        # Add specific processing logic here

        return result

    # Process using architecture-aware patterns
    results = ArchitectureAwarePatterns.safe_glyph_iterator(
        font,
        process_single_glyph
    )

    return results
'''

    @staticmethod
    def generate_component_analysis_template():
        """Generate component analysis template"""
        return '''
def analyze_font_components(font):
    """Analyze font component structure"""

    # Analyze dependencies
    dependencies = ArchitectureAwarePatterns.analyze_component_dependencies(font)

    # Check circular dependencies
    cycles = ArchitectureAwarePatterns.find_circular_dependencies(font)

    # Validate all component references
    component_issues = []
    for glyph in font.glyphs:
        for layer in glyph.layers:
            if layer.shapes:
                for shape in layer.shapes:
                    if shape.__class__.__name__ == 'GSComponent':
                        validation = ArchitectureAwarePatterns.validate_component_reference(font, shape)
                        if not validation["valid"]:
                            component_issues.append({
                                'glyph': glyph.name,
                                'issue': validation['error']
                            })

    return {
        'dependencies': dependencies,
        'circular_dependencies': cycles,
        'component_issues': component_issues
    }
'''

    @staticmethod
    def generate_variation_setup_template():
        """Generate variable font setup template"""
        return '''
def setup_font_variation(font, weight_range=(100, 900), width_range=(75, 125)):
    """Template for setting up font variation axes"""

    # Create weight axis
    weight_axis = GSAxis()
    weight_axis.name = "Weight"
    weight_axis.axisTag = "wght"
    weight_axis.minValue = weight_range[0]
    weight_axis.maxValue = weight_range[1]
    weight_axis.defaultValue = 400

    # Create width axis
    width_axis = GSAxis()
    width_axis.name = "Width"
    width_axis.axisTag = "wdth"
    width_axis.minValue = width_range[0]
    width_axis.maxValue = width_range[1]
    width_axis.defaultValue = 100

    # Add to font
    font.axes = [weight_axis, width_axis]

    # Assign axis values to each master
    for master in font.masters:
        # Infer values from master name
        weight_value = 400  # Default value
        width_value = 100   # Default value

        if 'Light' in master.name:
            weight_value = 300
        elif 'Bold' in master.name:
            weight_value = 700
        elif 'Black' in master.name:
            weight_value = 900

        if 'Condensed' in master.name:
            width_value = 75
        elif 'Expanded' in master.name:
            width_value = 125

        master.axesValues[weight_axis.axisId] = weight_value
        master.axesValues[width_axis.axisId] = width_value

    # Validate setup
    validation_result = ArchitectureAwarePatterns.validate_axis_values(font)

    return validation_result
'''
