## [Editing Paths](#editing-paths)

### [Selecting Nodes and Paths](#selecing-nodes-and-paths)

Click and drag with the Select tool ![](https://handbook.glyphsapp.com/v/content/icons/select-tool.svg) (shortcut `V`) to select nodes and handles inside a rectangular selection area.
Hold down the `Option` key to ignore the handles and only select on-curve nodes.

![](https://handbook.glyphsapp.com/v/content/images/root/selected-path-bounding-box.svg)

![](https://handbook.glyphsapp.com/v/content/images/root/slanted-selection.svg)

While dragging a selection, hold down the `Control` key to change the selection angle.
Release `Control` to resize the selection at its current angle.
Slanted selections are particularly helpful for italic designs.

Click a point or a segment to select it.
Hold down the `Shift` key to extend or reduce the selection.
Double-click near an outline segment to select the complete path.
Choose `Edit → Invert Selection` (`Cmd-Opt-Shift-I`) to select all unselected points, or `Edit → Deselect All` (`Cmd-Opt-A`) to cancel the selection.
Handles can be selected independently of the nodes.
`Shift`-select handles to create a non-contiguous selection.
When a single node or handle is selected, press the `Tab` key to select the following point on the path, or `Shift-Tab` to select the previous point.

### [Free-form Selections](#lasso-tool)

![](https://handbook.glyphsapp.com/v/content/images/root/lasso-tool.svg)

Use the Lasso tool ![](https://handbook.glyphsapp.com/v/content/icons/lasso-tool.svg) (shortcut `V` or `Shift-V`) to draw a non-rectangular selection.
This is particularly useful for glyphs with many points, where a rectangular selection would not be precise enough.

Activate the Lasso tool when it is not displayed in the toolbar by clicking and holding the Select tool ![](https://handbook.glyphsapp.com/v/content/icons/select-tool.svg) and choosing `Lasso Select` from the menu.
Alternatively, press `Shift-V` until the Lasso tool ![](https://handbook.glyphsapp.com/v/content/icons/lasso-tool.svg) icon is shown.

![](https://handbook.glyphsapp.com/v/content/images/root/tools-menu-select.png)

### [Moving Selected Nodes and Paths](#moving-selected-nodes-and-paths)

Move the selection using the mouse or the arrow keys.
Moving nodes will move the attached handles, even if they are not selected.
Hold down `Shift` for increments of 10, and `Command` for increments of 100.
Hold down `Option` to move only the selected points and not the attached handles.
While moving one or more nodes, hold down both `Control` and `Option` (or add `Option` after starting to drag) to nudge them, that is, to proportionally adjust the surrounding unselected handles at the same time.

**Left:** Original glyph outline with two selected nodes.   
**Center:** Move selected nodes, handles stay the same.   
**Right:** Nudge selected nodes, handles are adjusted.

![](https://handbook.glyphsapp.com/v/content/images/root/move-and-nudge-paths.svg)

Move a handle by dragging it with the mouse or pressing the arrow keys.
If multiple handles are selected, they all move simultaneously.
Moving one or more handles while holding down the `Option` key preserves their angles.
When using the keyboard, add the `Shift` key for increments of 10 or the `Command` key for increments of 100.

While moving a handle of a smooth ![](https://handbook.glyphsapp.com/v/content/icons/node-smooth-selected.svg) node, hold down `Control` and `Option` simultaneously to reproduce the length and angle of that handle to its matching one on the other side of the node.

Drag a segment to move both connected nodes and their handles.
`Option`-drag a segment to change the length of the handles but keep their respective angles.

### [Converting Nodes and Segments](#converting-nodes-and-segments)

Convert between smooth ![](https://handbook.glyphsapp.com/v/content/icons/node-smooth-selected.svg) connections and corners ![](https://handbook.glyphsapp.com/v/content/icons/node-corner-selected.svg) by double-clicking a node or selecting one or more nodes and pressing `Return`.

When converting from corner to smooth, ![](https://handbook.glyphsapp.com/v/content/icons/gradient-position-knob.svg) handles are added on either side of the node, possibly distorting the outline to keep the handles level.
Hold down the `Option` key while double-clicking or pressing `Return` to maintain the current outline.

Be careful when tidying up paths: In Multiple Master setups, superfluous points may be necessary for outline compatibility.

The `Path → Tidy up Paths` command (`Cmd-Shift-T`) applies heuristics to set the appropriate mode for all nodes at once or a selection of nodes.
It also removes superfluous points, for example, handles on a straight segment or an on-curve point exactly on the line between two others.
Hold down `Option` to choose `Path → Tidy up Paths for all Masters` (`Cmd-Opt-Shift-T`), applying the command on all masters of the selected glyphs.

`Option`-clicking a line segment converts it into a curve segment, and handles are added to the two bounding nodes.
Convert a curve back into a line segment by selecting and deleting one or both of its handles.

### [Nodes in Alignment Zones](#nodes-in-alignment-zones)

![](https://handbook.glyphsapp.com/v/content/images/root/nodes-in-alignment-zones.svg)

Nodes located exactly on a vertical [metric line](https://handbook.glyphsapp.com/single-page/#masters/metrics "Font Info ⯈ Masters ⯈ Metrics & Alignment Zones") are highlighted with a beige diamond ![](https://handbook.glyphsapp.com/v/content/icons/point-metric-line-highlight.svg).
Inside an alignment zone, the highlighting assumes the shape of a circle ![](https://handbook.glyphsapp.com/v/content/icons/point-alignment-zone-highlight.svg).
This helps to control the position of nodes even at small zoom scales.

### [Scaling & Rotating](#scaling-and-rotating)

The attributes of the current node selection are shown in the Info box (`View → Show Info`, `Cmd-Shift-I`):

**Tip:**

In all number input fields in Glyphs, use the up and down arrow keys to increase or decrease the value.

![](https://handbook.glyphsapp.com/v/content/images/root/info-box-selection.svg)

When multiple nodes are selected, scale and move the selection by changing the coordinates (`X` and `Y`) and the dimensions (![](https://handbook.glyphsapp.com/v/content/icons/horizontal-arrow.svg) width and ![](https://handbook.glyphsapp.com/v/content/icons/vertical-arrow.svg) height) in the Info box.
Set the transformation origin with the reference points ![](https://handbook.glyphsapp.com/v/content/icons/metrics-reference-point-center.svg) on the left.
Close the lock ![](https://handbook.glyphsapp.com/v/content/icons/lock-locked.svg) symbol to scale width and height proportionally.
Open the lock ![](https://handbook.glyphsapp.com/v/content/icons/lock-unlocked.svg) to scale width and height independently of each other.
Use the `Up` and `Down` arrow keys to step through the numbers.
Hold down `Shift` for increments of 10.

When multiple points are selected, the solid square ![](https://handbook.glyphsapp.com/v/content/icons/square-filled.svg) indicates the number of selected points.
The number next to the outlined square ![](https://handbook.glyphsapp.com/v/content/icons/square-clear.svg) represents the total number of points on the current glyph layer.

Rotate and scale the selection manually with the Rotate tool ![](https://handbook.glyphsapp.com/v/content/icons/rotate-tool.svg) (shortcut `R`) and the Scale tool ![](https://handbook.glyphsapp.com/v/content/icons/scale-tool.svg) (shortcut `S`).
With one of these tools active, click anywhere on the canvas to set the transformation origin, and then click and drag to transform the current selection.
Hold down the `Shift` key to rotate in steps of 90° or to scale proportionally.

![](https://handbook.glyphsapp.com/v/content/images/root/bounding-box.svg)

When multiple nodes are selected, a bounding box is displayed with transformation knobs on all four sides and corners.
Drag a knob to scale the selected points with respect to the opposite knob.
Hold down `Shift` to scale proportionally, and hold down `Option` to use the center of the box as the transformation origin.

Toggle the display of the bounding box with `View → Show Bounding Box` (`Cmd-Opt-Shift-B`).
More path transformations are possible [via the Palette](https://handbook.glyphsapp.com/single-page/#palette/transformations "Palette ⯈ Transformations").

### [Aligning](#align-selection)

Choose `Path → Align Selection` (`Cmd-Shift-A`) to quickly align all selected points.
The command aligns nodes, handles, and anchors.
Glyphs will automatically choose between horizontal and vertical alignment, whichever is smaller for the current selection.
The `Align Selection` command respects the [transformation origin](https://handbook.glyphsapp.com/single-page/#transformation-origin "Palette ⯈ Transformations ⯈ Transformation Origin") of the transformation palette:

`Align Selection` for different transformation origins.

![](https://handbook.glyphsapp.com/v/content/images/root/align-points-transformation-origin.svg)

Alternatively, set the width or the height value of two or more selected points to zero in the Info box.
Align an anchor horizontally above a point with the `Align Selection` command while exactly one anchor and one path point are selected, or center an anchor between two points while two points and one anchor are selected.
Glyphs respects the italic angle when aligning anchors to nodes.

Using the `Align Selection` command while exactly one point and one component are selected will align the origin point of the component to the selected node.
The node keeps its position.
The origin point is where the baseline crosses the left sidebearing if the italic angle is zero.
If the component glyph contains an `origin` anchor, its position is used as the origin point instead.

If the italic angle is not zero, instead of the left sidebearing, an imaginary vertical line crossing the slanted LSB at half x-height is used.
In that case, the origin point is where this line crosses the baseline.

Applying `Path → Align Selection` on a single node will try to move the node over the nearest node in the background.
Align partial paths, complete paths, or components to each other using the [Transformations section](https://handbook.glyphsapp.com/single-page/#palette/transformations "Palette ⯈ Transformations") in the Palette (`Cmd-Opt-P`).

### [Duplicating Paths](#duplicating-paths)

Quickly duplicate the current selection by holding down `Option` while dragging a copy of the paths into their new position.
Alternatively, copy (`Cmd-C`) and paste (`Cmd-V`) the selection.

`Option`-dragging partial paths will duplicate the selected segments.
This can be helpful when replicating glyph parts like serifs or spurs.

### [Deleting Nodes](#deleting-nodes)

Select a node and press the `Delete` key to delete it.

**Note:**

If the Erase tool ![](https://handbook.glyphsapp.com/v/content/icons/erase-tool-secondary.svg) icon is not visible, press `Shift-E` or click and hold the [Knife tool](https://handbook.glyphsapp.com/single-page/#knife-tool "Edit View ⯈ Editing Paths ⯈ Cutting Paths") ![](https://handbook.glyphsapp.com/v/content/icons/knife-tool-secondary.svg) icon and choose `Erase`.

Alternatively, choose the Erase tool ![](https://handbook.glyphsapp.com/v/content/icons/erase-tool.svg) (shortcut `E`) and click a node to delete it.
Glyphs will keep the path closed and will try to reconstruct the same path segment without the node:

![](https://handbook.glyphsapp.com/v/content/images/root/delete-node.svg)

Press `Opt-Delete` to break the path by removing the node and both path segments surrounding the node:

![](https://handbook.glyphsapp.com/v/content/images/root/delete-node-delete-segment.svg)

Delete a single segment between on-curve nodes with the Erase tool by `Option`-clicking it.
Delete all selected segments by pressing `Opt-Delete`.
Alternatively, select a handle and erase its segment by pressing `Opt-Delete`.

![](https://handbook.glyphsapp.com/v/content/images/root/delete-segment.svg)

### [Opening and Closing Paths](#opening-paths)

With the Draw tool ![](https://handbook.glyphsapp.com/v/content/icons/draw-tool.svg) (shortcut `P`), click a node to open the path at the node position.
Short blue perpendicular lines mark open path endings.
Drag the path ends apart using the Select tool ![](https://handbook.glyphsapp.com/v/content/icons/select-tool.svg) (shortcut `V`).

![](https://handbook.glyphsapp.com/v/content/images/root/open-node.svg)

Close a path by dragging an open line ending on top of another with the Select tool.
Select two path endings and choose `Connect Nodes` from the context menu to add a connecting line segment between the nodes: ![](https://handbook.glyphsapp.com/v/content/icons/connecting-paths-open.svg) → ![](https://handbook.glyphsapp.com/v/content/icons/connecting-paths-connected.svg).
Choose `Close Open Paths` to close the selected paths fully: ![](https://handbook.glyphsapp.com/v/content/icons/connecting-paths-open.svg) → ![](https://handbook.glyphsapp.com/v/content/icons/connecting-paths-closed.svg).

### [Cutting Paths](#knife-tool)

With the Knife tool ![](https://handbook.glyphsapp.com/v/content/icons/knife-tool.svg) (shortcut `E` or `Shift-E`), click and drag a line across a path to cut the outline into two separate outlines.
Glyphs will close the two resulting paths along the cutting line.
Cutting across several overlapping paths will rewire the segments with each other.

**Tip:**

When multiple tools share one icon in the toolbar, such as the Knife and Erase tools, add `Shift` to the tool shortcut to toggle between the tools.

![](https://handbook.glyphsapp.com/v/content/images/root/knife-cut.svg)

Activate the Knife tool by clicking and holding the Erase tool ![](https://handbook.glyphsapp.com/v/content/icons/erase-tool.svg) and choosing `Knife` from the menu.
Alternatively, press `Shift-E`.

![](https://handbook.glyphsapp.com/v/content/images/root/tools-menu-erase.png)

### [Re-segmenting Outlines](#resegmenting-outlines)

Open corners and reconnected nodes offer finer control and allow manipulating path segments independently of each other.
This control also makes interpolating between masters easier.

Open a corner node into two nodes by selecting it and choosing `Open Corner` from the context menu:

The top-left corner of the counter is opened with `Open Corner`.
Opening corners only works on corner nodes.

![](https://handbook.glyphsapp.com/v/content/images/root/open-corner.svg)

Choose `Reconnect Nodes` from the context menu to the two nodes of an open corner to get back to the original corner node.
Select an even number of nodes and apply `Reconnect Nodes` to reconnect each node with its closest neighbor:

![](https://handbook.glyphsapp.com/v/content/images/root/reconnect-nodes.svg)

The size of the created overlap will be approximately half the first values entered for vertical and horizontal stems in `File → Font Info → Masters` (`Cmd-I`).

![](https://handbook.glyphsapp.com/v/content/images/root/open-corner-terminals-lowercase-s.svg)

Thus, the reconnected nodes should extend comfortably into the stem (when used on counterforms such as the B in the image above) or outside the outline, such as the `s` on the left.

Opened corners are considered invisible if the triangular overlaps are small enough in relation to the neighboring visible outline segments.
That way, opened corners can also be placed on the outside of paths.
If the overlap size goes beyond the threshold size, they will be visible.
These outwards facing open corners are useful for editing bent terminals, as in a sans serif lowercase s.
Select a path segment and open the two nodes on its extremities with the `Open Corner` command.

### [Controlling Path Direction](#controlling-path-direction)

![](https://handbook.glyphsapp.com/v/content/images/root/open-path.svg)

The starting point of a closed path is displayed as an arrowhead ![](https://handbook.glyphsapp.com/v/content/icons/path-start-corner.svg) (or ![a green arrowhead](https://handbook.glyphsapp.com/v/content/icons/path-start-smooth.svg) for a smooth node) following the path direction.
The end nodes of an open path are displayed as short perpendicular blue lines, where a light blue arrowhead indicates the first node.
On a closed path, make any on-curve node the first node by choosing `Make Node First` from the node context menu.

**Tip:**

Quickly create a punched through counterform by overlapping two paths and pressing `Cmd-Shift-R` (`Path → Correct Path Direction`).

All outer paths need to run counterclockwise, while enclosed paths (such as the inner path of an `O`) must go clockwise.
Change the path direction of a path by selecting it and choosing `Path → Reverse Contours` or `Reverse Selected Contours` from the context menu.
Hold down `Option` to change the direction in all masters.
When no path is selected, use `Path → Reverse Contours` from the menu bar or `Reverse All Contours` from the context menu to toggle all path directions in a glyph.

![](https://handbook.glyphsapp.com/v/content/images/root/reverse-selected-contours.svg)

`Path → Correct Path Direction` (`Cmd-Shift-R`) will perform an informed guess and find the right path directions for all paths on the current glyph layer or all selected glyph layers.
This will also rearrange the shape order and reset the starting points of all paths to their bottom-left node.
Holding down the `Option` key changes the command to `Correct Path Direction for all Masters` (`Cmd-Opt-Shift-R`).
As the name indicates, it will include all master layers, all [Alternate](https://handbook.glyphsapp.com/single-page/#alternate-layers "Interpolation ⯈ Switching Shapes ⯈ Alternate Layers"), and [Intermediate layers](https://handbook.glyphsapp.com/single-page/#intermediate-layers "Interpolation ⯈ Intermediate Layers").
The command ignores all other non-master layers.
This is useful in a Multiple Master setup.

For successful interpolations, the path order, starting points, and path directions must be compatible and consistent throughout all font masters.
See [Correcting Path Direction](https://handbook.glyphsapp.com/single-page/#correcting-path-direction "Interpolation ⯈ Outline Compatibility ⯈ Correcting Path Direction") for details on fixing the path direction for interpolation.

### [Extremes & Inflections](#extremes-and-inflections)

![](https://handbook.glyphsapp.com/v/content/images/root/extrema-and-inflections.svg)

Extrema are the positions on a path with a completely horizontal or vertical tangent.
Inflections are positions in path segments where the segment changes its bend from clockwise to counterclockwise or vice versa.

It is considered good practice to have nodes on extremum points.
Some font technologies, like hinting, require nodes at extremum positions.
Some operations, like [offsetting a curve](https://handbook.glyphsapp.com/single-page/#filters/offset-curve "Filters ⯈ Built-in Filters ⯈ Offset Curve"), work better with inflection points placed on the undulating curves.
Also, some font renderers may behave unexpectedly if such nodes are not in place.
Furthermore, inflection points pose a problem for outline interpolation since they can easily cause kinks in outlines.

Insert nodes on extremum and inflection points by `Shift`-clicking a segment with the Draw tool ![](https://handbook.glyphsapp.com/v/content/icons/draw-tool.svg) (`P`).
A node will be inserted at the nearest extremum or inflection.

Alternatively, choose `Path → Add Extremes`, and nodes will be added at extremes on all paths of the active layer.
Glyphs will not add an extreme if the resulting segment were very short.
In this case, it assumes that the node placement was intentional.
Force Glyphs to add all extremes by opening the `Path` menu, holding down `Option`, and choosing `Force Extremes`.
When a node is only slightly off the extremum position, Glyphs will attempt to preserve the outline shape while moving the node into the extremum position and turning the surrounding handles entirely vertical or horizontal.

Extremes are added automatically at export time with a `Filter` custom parameter called `AddExtremes`.
See [Add Extremes](https://handbook.glyphsapp.com/single-page/#filters/add-extremes "Filters ⯈ Built-in Filters ⯈ Add Extremes") for details.
This can be useful for shallow curves or certain Multiple Master situations, where adding extremes would make editing or interpolating unnecessarily complex.

### [Duplicate Nodes](#duplicate-nodes)

When two adjacent on-curve nodes share the same coordinates, they are highlighted with a red circle.
Merge these nodes with `Path → Tidy up Paths` (`Cmd-Shift-T`).

![](https://handbook.glyphsapp.com/v/content/images/root/duplicate-nodes.svg)

### [Focusing & Locking](#focusing-locking)

Prevent accidental edits with focusing and locking.

![](https://handbook.glyphsapp.com/v/content/images/root/focus-on-path.svg)

Focus on one or multiple paths by selecting at least one point for each path and choosing `Focus on Selected Path` from the context menu.
Focusing on a path hides the controls for all other paths.
Use path focusing to exclusively work on a single path, even in complex glyphs.
Filters, plug-ins, and other scripts may still operate on all paths; only the Edit View controls are hidden.
Release the focus by choosing `Clear Focus on Paths` from the context menu.

The reverse is possible by locking paths:
Lock a path by `Control`-clicking or right-clicking one of its nodes and choosing `Lock Path` from the context menu.
Points of a locked path cannot be selected or modified in Edit View.
Like with focusing, locked paths can still be changed by filters, plug-ins, and scripts.
Points of a locked path turn red when the mouse cursor is placed on them, indicating that they cannot be dragged.
Unlock a path by choosing `Unlock Path` from the context menu on any of its nodes.

Lock and unlock a glyph by choosing `Locked` from its context menu.
A lock ![](https://handbook.glyphsapp.com/v/content/icons/locked-accent-color.svg) icon appears in the top-right corner of the glyph in Edit View and Font View.
A locked glyph cannot be modified: not with the Select tool, not by a filter, plug-in, or script.
This edit-protection is helpful if the glyph is considered final, and no further edits should be applied.