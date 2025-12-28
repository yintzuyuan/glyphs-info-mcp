## [Transformations](#palette/transformations)

![](https://handbook.glyphsapp.com/v/content/images/root/transformation-palette.svg)

The `Transformations` section transforms points, paths, components, anchors, guides, images, and more.
The following transformations are supported:

- mirror the selection horizontally ![](https://handbook.glyphsapp.com/v/content/icons/mirror-horizontally.svg) or vertically ![](https://handbook.glyphsapp.com/v/content/icons/mirror-vertically.svg);
- scale ![](https://handbook.glyphsapp.com/v/content/icons/scale.svg) or reverse scale ![](https://handbook.glyphsapp.com/v/content/icons/reverse-scale.svg) the selection;
- rotate the selection clockwise ![](https://handbook.glyphsapp.com/v/content/icons/rotate-cw.svg) or counterclockwise ![](https://handbook.glyphsapp.com/v/content/icons/rotate-ccw.svg);
- slant the selection left ![](https://handbook.glyphsapp.com/v/content/icons/skew-left.svg), right ![](https://handbook.glyphsapp.com/v/content/icons/skew-right.svg), down ![](https://handbook.glyphsapp.com/v/content/icons/skew-down.svg), or up ![](https://handbook.glyphsapp.com/v/content/icons/skew-up.svg);
- align the selection left ![](https://handbook.glyphsapp.com/v/content/icons/align-left.svg), right ![](https://handbook.glyphsapp.com/v/content/icons/align-right.svg), to the top ![](https://handbook.glyphsapp.com/v/content/icons/align-top.svg) or bottom ![](https://handbook.glyphsapp.com/v/content/icons/align-bottom.svg), center it vertically ![](https://handbook.glyphsapp.com/v/content/icons/align-horizontal-center.svg) or horizontally ![](https://handbook.glyphsapp.com/v/content/icons/align-vertical-center.svg);
- perform boolean operations (![](https://handbook.glyphsapp.com/v/content/icons/boolean-operation-or.svg) union, ![](https://handbook.glyphsapp.com/v/content/icons/boolean-operation-not.svg) subtraction, ![](https://handbook.glyphsapp.com/v/content/icons/boolean-operation-and.svg) intersection) on paths.

Transformations can be applied in both Font View and Edit View.
According to the selection, the transformation applies to segments, paths, or complete glyph layers.

The buttons to the left and right of text fields perform opposite transformations.
For example, clicking ![rotate counterclockwise](https://handbook.glyphsapp.com/v/content/icons/rotate-ccw.svg) undoes the transformation caused by clicking ![rotate clockwise](https://handbook.glyphsapp.com/v/content/icons/rotate-cw.svg).
These opposing transformations are not subject to rounding errors that might be introduced by the unit grid.
See [Grid Spacing & Subdivision](https://handbook.glyphsapp.com/single-page/#grid-spacing-and-subdivision "Font Info ⯈ Other Settings ⯈ Grid Spacing & Subdivision") for details on the unit grid.

### [Transformation Origin](#transformation-origin)

All transformations (except for alignment) are performed with respect to a transformation origin.
The top row of the `Transformation` palette controls this origin point.

The transformation box ![](https://handbook.glyphsapp.com/v/content/icons/transformation-origin-box-center.svg) places the transformation origin with respect to the selection bounding box.
Either one of the four corners, or the center of one of the four edges, or the center of the selection box can be defined as the transformation origin.

The reference point ![](https://handbook.glyphsapp.com/v/content/icons/transformation-origin-reference.svg) uses the transformation origin as defined by the Scale tool (`S`) or the Rotate tool (`R`).
Using one of those tools, click on the canvas to define the transformation origin.
The point is indicated as a red ring ![](https://handbook.glyphsapp.com/v/content/icons/reference-point.svg) with a crosshair when using the Scale/Rotate tool, and just as a crosshair ![](https://handbook.glyphsapp.com/v/content/icons/reference-point-crosshair.svg) when using any other tool.

The metrics point ![](https://handbook.glyphsapp.com/v/content/icons/transformation-origin-metrics-x-height.svg) places the transformation origin at one of the metrics defined in `File → Font Info… → Masters → Metrics`.
Choose either the baseline, half or full x-height, or half or full cap height.
For CJK glyphs, the layer dimensions control ![](https://handbook.glyphsapp.com/v/content/icons/transformation-origin-metrics-cjk.svg) is displayed instead.
It places the transformation origin at the center of the layer (half of the width and centered between the ascender and the descender).

### [Mirroring](#mirroring)

The mirror buttons ![](https://handbook.glyphsapp.com/v/content/icons/mirror-horizontally.svg)/![](https://handbook.glyphsapp.com/v/content/icons/mirror-vertically.svg) reflect the selection to the other side of the transformation origin.
Horizontal ![](https://handbook.glyphsapp.com/v/content/icons/mirror-horizontally.svg) mirroring reflects across the horizontal center of the layer when a metrics point defines the transformation origin.

Mirror with the transformation origin positioned in the metrics point control at either half the x-height or half the cap height to preserve overshoots.
For example, mirroring an `n` that overshoots the x-height will result in an `u` shape that overshoots the baseline.

Mirroring a corner component (see [Corner Components](https://handbook.glyphsapp.com/single-page/#components/corner "Reusing Shapes ⯈ Corner Components")) will turn a left corner into a right corner and vice versa.
Mirroring a glyph component upside-down will reverse the assignment of top and bottom anchors in the original glyph.
This way, a top mark can be used as a bottom mark by mirroring the component.

### [Scaling](#scaling)

![](https://handbook.glyphsapp.com/v/content/images/root/scaling-transform-origins.svg)

Scaling by 120 % using an origin of ![transformation box center](https://handbook.glyphsapp.com/v/content/icons/transformation-origin-box-inset-center.svg) and ![transformation box bottom-left](https://handbook.glyphsapp.com/v/content/icons/transformation-origin-box-inset-bottom-left.svg).

Click the scale ![](https://handbook.glyphsapp.com/v/content/icons/scale.svg) button to scale the selection by the specified percentage.
Percentages larger than 100 % increase the selection size, percentages smaller than 100 % decrease the size, and a percentage of 100 % does not change the size.
The scaling factor along the horizontal axis (top field) and the vertical axis (bottom field) can be defined independently.
The top field is used for both axes if the lock ![](https://handbook.glyphsapp.com/v/content/icons/lock-locked.svg) icon is locked.

Reverse scaling is helpful since a scale of 120 % would not be undone by simply scaling to 80 %, but by scaling to 83.3… % (= 100 %/120 %).

The reverse scale ![](https://handbook.glyphsapp.com/v/content/icons/reverse-scale.svg) button undoes a scaling operation.
This is not the same as scaling down:
Scaling with ![the scale button](https://handbook.glyphsapp.com/v/content/icons/scale.svg) by a percentage smaller than 100 % (for example, 75 %) shrinks the selection.
Scaling with ![the reverse-scale button](https://handbook.glyphsapp.com/v/content/icons/reverse-scale.svg) by the same percentage returns the selection to its original size.
Similarly, a selection that was enlarged to a value larger than 100 % with ![the scale button](https://handbook.glyphsapp.com/v/content/icons/scale.svg) can be undone using ![the reverse-scale button](https://handbook.glyphsapp.com/v/content/icons/reverse-scale.svg).

### [Rotating & Slanting](#rotating-and-slanting)

*Slanting* is sometimes also referred to as *skewing*.

Rotate the selection with ![rotate counterclockwise](https://handbook.glyphsapp.com/v/content/icons/rotate-ccw.svg) and ![rotate clockwise](https://handbook.glyphsapp.com/v/content/icons/rotate-cw.svg).
Slant the selection with ![slant left](https://handbook.glyphsapp.com/v/content/icons/skew-left.svg), ![slant right](https://handbook.glyphsapp.com/v/content/icons/skew-right.svg), ![slant down](https://handbook.glyphsapp.com/v/content/icons/skew-down.svg), and ![slant up](https://handbook.glyphsapp.com/v/content/icons/skew-up.svg).
Note that slanting a selection twice by a certain amount does *not* yield
the same result as slanting it once with double the amount.

### [Aligning](#palette/aligning)

The align buttons (![left](https://handbook.glyphsapp.com/v/content/icons/align-left.svg), ![horizontal center](https://handbook.glyphsapp.com/v/content/icons/align-horizontal-center.svg), ![right](https://handbook.glyphsapp.com/v/content/icons/align-right.svg), ![top](https://handbook.glyphsapp.com/v/content/icons/align-top.svg), ![vertical center](https://handbook.glyphsapp.com/v/content/icons/align-vertical-center.svg), ![bottom](https://handbook.glyphsapp.com/v/content/icons/align-bottom.svg)) can be used on points, complete and partial paths, anchors, and components.
Aligning is always done relative to the bounding box of the selection.

Quickly align the selected points with `Path → Align Selection` (`Cmd-Shift-A`).
This command respects the setting for the transformation origin.
See [Editing Paths](https://handbook.glyphsapp.com/single-page/#editing-paths "Edit View ⯈ Editing Paths") for more details.

### [Boolean Operations](#boolean-operations)

The bottom row of buttons combines closed paths with boolean operations: ![](https://handbook.glyphsapp.com/v/content/icons/boolean-operation-or.svg) union, ![](https://handbook.glyphsapp.com/v/content/icons/boolean-operation-not.svg) subtraction, and ![](https://handbook.glyphsapp.com/v/content/icons/boolean-operation-and.svg) intersection.

From left to right: two overlapping paths, union, subtraction, and intersection.

![](https://handbook.glyphsapp.com/v/content/images/root/boolean-operations.svg)

Union removes the overlaps in all selected paths (or all paths of the layer if there is no selection).
Subtraction removes the selected paths from the unselected paths.
Paths involved in the subtract operation are merged first to achieve consistent results.
Intersection keeps only the parts where the selected paths overlap the unselected paths.
Both subtraction and intersection use the frontmost path as the selected path if there is no selection.

A union operation can be applied to all glyphs on export using the `Remove Overlap` option.
See [Options](https://handbook.glyphsapp.com/single-page/#export/opentype/options "Import & Export ⯈ Exporting Font Files ⯈ OpenType Export ⯈ Options") for details.

# [Font View](#font-view)

Font View provides an overview of all glyphs of a font.
It is displayed when a new Glyphs file is created.
If multiple tabs are open, jump to Font View by clicking the leftmost tab or pressing `Cmd-Opt-1`.