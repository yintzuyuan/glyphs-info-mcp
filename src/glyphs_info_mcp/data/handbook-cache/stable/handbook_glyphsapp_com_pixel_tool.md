## [Pixel Tool](#pixel-tool)

The Pixel tool ![](https://handbook.glyphsapp.com/v/content/icons/pixel-tool.svg) (shortcut `X`, `Shift-B` if the Pencil tool is selected) draws pixel components.
Use the pixel tool to create pixel fonts and pixel symbols.

### [Setup](#pixel-tool/setup)

![](https://handbook.glyphsapp.com/v/content/images/root/bitmap-font.svg)

The Pixel tool requires a grid spacing of 2 or above.
Change it in `File → Font Info… → Other → Grid Spacing`.
See [Grid Spacing & Subdivision](https://handbook.glyphsapp.com/single-page/#grid-spacing-and-subdivision "Font Info ⯈ Other Settings ⯈ Grid Spacing & Subdivision") for details.

The Pixel tool uses the glyph named `pixel` to draw pixels when clicking and dragging in Edit View.
If the glyph named `pixel` is not already in the font, Glyphs will offer to add it upon a click with the Pixel tool:

![](https://handbook.glyphsapp.com/v/content/images/root/alert-add-pixel-glyph.png)

Click `Add` to create the `pixel` glyph.
By default, the `pixel` glyph is a square of the same size as the grid spacing.

### [Drawing Pixels](#pixel-tool/drawing)

Select the Pixel tool, click once, and add a pixel component on the canvas.
Click again to remove the pixel.
Click and drag the mouse to add multiple pixels.
Start to drag on a pixel already in place to remove pixels while dragging.

### [Pixel Shape](#pixel-tool/pixel-shape)

![](https://handbook.glyphsapp.com/v/content/images/root/x-mark-pixels.svg)

The `pixel` glyph can be modified to contain any arbitrary shape.
Reduce the grid spacing to a lower number (for example, the default of 1) to draw path segments smaller than a pixel.
For instance, the `pixel` can be an x-mark ![](https://handbook.glyphsapp.com/v/content/icons/x-mark-pixel.svg) for a stitch effect.
Increase the grid spacing again when using the Pixel tool.

# [Interpolation](#interpolation)

The glyph outlines drawn in Edit View belong to a *font master*.
Initially, a Glyphs file contains a single master named `Regular`.
If a Glyphs file contains additional masters (for example, a *Thin* and *Bold* master), this is referred to as a Multiple Masters setup.
Working with Multiple Masters allows Glyphs to export font instances not just for each master, but also between masters.

A small number of masters can result in a large number of interpolated instances.
In this example, two masters *Thin* and *Bold* are used to produce a total of six instances along a *Weight* axis.

![](https://handbook.glyphsapp.com/v/content/images/root/multiple-masters-workflow.svg)

An *interpolation axis* describes the aspect of the glyph design that changes between masters.
The most common axes are the *Weight* (from light to bold) and the *Width* (from condensed to extended), but there are many more possible interpolation axes.

A Multiple Master setup can have one or more axes.
While a single axis can be thought of as a line along which the design varies, two axes create a two-dimensional space in which every point is a possible font instance.
This space is referred to as the *designspace*, which may also have three or more dimensions.

Two perspectives on the three-axes designspace of ABC Arizona, the typeface in which this handbook is set.

![](https://handbook.glyphsapp.com/v/content/images/root/multiple-masters-cube-set.svg)