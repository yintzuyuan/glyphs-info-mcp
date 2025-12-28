## [Drawing Paths](#drawing-paths)

### [Draw Tool](#draw-tool)

![](https://handbook.glyphsapp.com/v/content/images/root/first-path.svg)

Draw outlines with the Draw tool ![](https://handbook.glyphsapp.com/v/content/icons/draw-tool.svg) (shortcut `P` as in Pen or Path).
Click anywhere on the canvas to place a node.
Placing multiple nodes connects them to a path.

Click and drag to create a curved path segment.
Dragging extends two handles from the placed node.
The length of the handles controls the curvature of the segment.
Hold down the `Option` key to change the handle of the next segment only, and keep the handle of the previous segment as it is.
Hold down the `Command` key while dragging to change the length of only the next handle while keeping both handles at the same angle.
When dragging, hold down the `Space` bar to reposition the node.
Click on the first node of a path to close the path.

This handbook uses the term *node* to refer to on-curve points, *handle* for off-curve points, and *point* as an umbrella word for both types.

A node can either be a *smooth node* ![](https://handbook.glyphsapp.com/v/content/icons/node-smooth-selected.svg) or a *corner node* ![](https://handbook.glyphsapp.com/v/content/icons/node-corner-selected.svg).
Smooth nodes always keep both of their handles in a straight line.
They appear round and green.
Corner nodes appear square and blue.
Their handles may form a straight line, but they can also form any non-smooth corner.
The size and colors of nodes are [configurable in the settings](https://handbook.glyphsapp.com/single-page/#settings/appearance "Settings ⯈ Appearance").

![](https://handbook.glyphsapp.com/v/content/images/root/path.svg)

*Handles* (also called *Bézier control points* or *off-curve points*) control the curvature of their path segment.
They are displayed as small circles and connected to their node with a thin gray line.

In open paths, start and end points are displayed as short perpendicular blue lines.
The start point also features a blue triangle, indicating the path direction.
Points are stored in path direction order, which is significant for some path operations.
See also [Controlling Path Direction](https://handbook.glyphsapp.com/single-page/#controlling-path-direction "Edit View ⯈ Editing Paths ⯈ Controlling Path Direction").

Toggle the display of nodes with `View → Show Nodes → In Foreground` (`Cmd-Shift-N`).

![](https://handbook.glyphsapp.com/v/content/images/root/path-no-nodes.svg)

### [Pencil Tool](#pencil-tool)

The Pencil tool ![](https://handbook.glyphsapp.com/v/content/icons/pencil-tool.svg) (shortcut `B`) offers a quick way to draw freehand curves, especially when using a drawing tablet.
This includes drawing with Apple Pencil on an iPad using Sidecar.
The resulting paths will need some cleaning up (see [Editing Paths](https://handbook.glyphsapp.com/single-page/#editing-paths "Edit View ⯈ Editing Paths")) because Pencil paths usually contain too many nodes in an attempt to reproduce the pencil drawing faithfully.

### [Primitives](#primitives-tool)

Glyphs offers rectangles and ellipses as built-in primitive shapes.

![](https://handbook.glyphsapp.com/v/content/images/root/primitives-size-window.png)

Click the Primitives tool ![](https://handbook.glyphsapp.com/v/content/icons/primitives-tool-square.svg)/![](https://handbook.glyphsapp.com/v/content/icons/primitives-tool-circle.svg), or press `F` to activate it.
Click and hold the Primitives tool icon or press `Shift-F` to switch between the two shape options.
Alternatively, use `Draw Circle` or `Draw Rectangle` from the context menu to switch between the two modes.

![](https://handbook.glyphsapp.com/v/content/images/root/tools-menu-primitives.png)

Click once on the canvas to create a primitive by entering its measurements with the keyboard.
Click and drag to draw it directly into the edit area.
Hold down `Shift` for a perfect square or circle.
Hold down `Option` to draw the shape from its center.